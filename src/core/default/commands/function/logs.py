import time, datetime

from argparse import ArgumentParser
from typing import List, Dict

from boto3 import client

from core.constructs.commands import BaseCommand, OutputWrapper

from core.utils import hasher

from core.default.commands.function.utils import get_cloud_id_from_cdev_name


class show_logs(BaseCommand):
    help = """
        Get the logs of a deployed lambda function
    """

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "function_name",
            type=str,
            help="The function that you want to watch. Name must include component name. ex: comp1.demo_function",
        )
        parser.add_argument(
            "--watch",
            action="store_true",
            help="watch the logs. If this flag is passed, only --start_time flag is read",
        )
        parser.add_argument(
            "--tail", action="store_true", help="show the tail of the logs"
        )
        parser.add_argument(
            "--limit",
            type=int,
            nargs='?',
            default=10000,
            help="number of events to show. Must be used with --tail.",
        )
        parser.add_argument(
            "--query",
            nargs='+',
            help="retrieve information base on a cloudWatch query",
        )
        parser.add_argument(
            "--start_time",
            type=lambda d: datetime.datetime.strptime(d, '%Y-%m-%d-%H:%M:%S'),
            help="set the start_time when use the query option, must be on the Y-m-d-H:M:S format",
        )
        parser.add_argument(
            "--end_time",
            type=lambda d: datetime.datetime.strptime(d, '%Y-%m-%d-%H:%M:%S'),
            help="set the end_time when use the query option, must be on the Y-m-d-H:M:S format",
        )

    def command(self, *args, **kwargs) -> None:
        (
            component_name,
            function_name,
        ) = self.get_component_and_resource_from_qualified_name(
            kwargs.get("function_name")
        )

        tail_val = kwargs.get("tail")
        limit_val = kwargs.get("limit")
        query_val = kwargs.get("query")
        start_time_val = kwargs.get("start_time")
        end_time_val = kwargs.get("end_time")

        cloud_name = get_cloud_id_from_cdev_name(component_name, function_name).split(
            ":"
        )[-1]
        if not cloud_name:
            self.stdout.write(
                f"Could not find function {function_name} in component {component_name}"
            )
            return

        cloud_watch_group_name = f"/aws/lambda/{cloud_name}"

        watch_val = kwargs.get("watch")
        if watch_val:
            _watch_log_group(cloud_watch_group_name, self.stdout)
            return

        cloud_watch_client = client("logs")
        if query_val is None:
            self.get_log_result(limit_val, tail_val, cloud_watch_client, cloud_watch_group_name)
        else:
            self.get_log_query_result(query_val, start_time_val, end_time_val,
                                      cloud_watch_client, cloud_watch_group_name)

    def get_log_result(self, limit_val, tail_val, cloud_watch_client, cloud_watch_group_name) -> None:
        log_streams_rv = cloud_watch_client.describe_log_streams(
            logGroupName=cloud_watch_group_name,
            orderBy="LastEventTime",
        )
        streams = _get_needed_streams(log_streams_rv.get("logStreams"))
        for stream in streams:
            response = cloud_watch_client.get_log_events(
                logGroupName=cloud_watch_group_name,
                logStreamName=stream,
                limit=limit_val,
                startFromHead=False if tail_val else True,
            )
            if tail_val:
                next_token = response.get("nextForwardToken")
            else:
                next_token = response.get("nextBackwardToken")
            prev_token = ""
            while next_token != prev_token:
                for event in response.get("events"):
                    self.stdout.write(
                        f"{datetime.datetime.fromtimestamp(event.get('timestamp') / 1000).strftime('%Y-%m-%d %H:%M:%S')} - {event.get('message')} "
                    )
                response = cloud_watch_client.get_log_events(
                    logGroupName=cloud_watch_group_name,
                    logStreamName=stream,
                    limit=limit_val,
                    startFromHead=False if tail_val else True,
                    nextToken=next_token
                )
                prev_token = next_token
                if tail_val:
                    next_token = response.get("nextForwardToken")
                else:
                    next_token = response.get("nextBackwardToken")

    def get_log_query_result(self, query_val, start_time_val, end_time_val,
                             cloud_watch_client, cloud_watch_group_name) -> None:
        print(query_val)
        print(start_time_val)
        print(end_time_val)
        print(cloud_watch_client)
        print(cloud_watch_group_name)
        if start_time_val is None:
            start_time_val = datetime.datetime.today() - datetime.timedelta(weeks=52)
        if end_time_val is None:
            end_time_val = datetime.datetime.now()
        query = ''
        for item in query_val:
            query = query + ' ' + str(item)
        start_query_response = cloud_watch_client.start_query(
            logGroupName=cloud_watch_group_name,
            startTime=int(start_time_val.timestamp()),
            endTime=int(end_time_val.timestamp()),
            queryString=query,
        )
        query_id = start_query_response['queryId']
        response = None

        while response == None or response['status'] == 'Running':
            self.stdout.write('Waiting for query to complete ...')
            time.sleep(1)
            response = cloud_watch_client.get_query_results(
                queryId=query_id
            )

        for item in response['results']:
            for item2 in item:
                self.stdout.write(item2['field'] + ': ' + item2['value'])


def _watch_log_group(group_name: str, stdout: OutputWrapper, args=None) -> None:
    cloud_watch_client = client("logs")

    events_hash = set()
    keep_watching = True
    while keep_watching:
        _previous_refresh_time = int(
            (time.mktime(datetime.datetime.now().timetuple()) - 60) * 1000
        )
        keep_watching = _read_from_streams(
            cloud_watch_client, group_name, stdout, events_hash, _previous_refresh_time
        )


def _read_from_streams(
        cloud_watch_client,
        group_name: str,
        stdout: OutputWrapper,
        events_hash,
        _previous_refresh_time,
) -> bool:
    try:
        log_streams_rv = cloud_watch_client.describe_log_streams(
            logGroupName=group_name,
            orderBy="LastEventTime",
        )

        streams = _get_needed_streams(
            log_streams_rv.get("logStreams"), _previous_refresh_time
        )

        for stream in streams:
            response = cloud_watch_client.get_log_events(
                logGroupName=group_name,
                logStreamName=stream,
                startTime=_previous_refresh_time,
                startFromHead=True,
            )

            for event in response.get("events"):
                event_hash = hasher.hash_list(
                    [
                        event.get("timestamp"),
                        event.get("message"),
                        event.get("ingestionTime"),
                    ]
                )

                if event_hash not in events_hash:
                    stdout.write(
                        f"{datetime.datetime.fromtimestamp(event.get('timestamp') / 1000).strftime('%Y-%m-%d %H:%M:%S')} - {event.get('message')}"
                    )

                events_hash.add(event_hash)

        time.sleep(0.2)
        return True
    except KeyboardInterrupt:
        stdout.write("Interrupted")

    return False


def _get_needed_streams(streams: List[Dict], start_time: float = None) -> List[str]:
    stream_names = [x.get("logStreamName") for x in streams]
    return stream_names
