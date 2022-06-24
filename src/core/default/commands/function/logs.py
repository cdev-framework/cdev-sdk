import time, datetime

from argparse import ArgumentParser
from typing import List, Optional

from boto3 import client
from botocore.exceptions import ClientError

from core.constructs.commands import BaseCommand

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
        cloud_group_name = self._get_cloud_group_name(kwargs.get("function_name"))
        if not cloud_group_name:
            return

        watch_val = kwargs.get("watch")
        if watch_val:
            self._watch_log_group(cloud_group_name)
        else:
            query_val = kwargs.get("query")
            if query_val is None:
                self._show_log(cloud_group_name, **kwargs)
            else:
                self._show_filtered_log(cloud_group_name, **kwargs)

    def _get_cloud_group_name(self, function_name: str) -> Optional[str]:
        (
            component_name,
            resource_name,
        ) = self.get_component_and_resource_from_qualified_name(
            function_name
        )

        cloud_name = get_cloud_id_from_cdev_name(component_name, resource_name)
        if not cloud_name:
            return None

        cloud_name = cloud_name.split(":")
        if len(cloud_name) < 2:
            return None

        cloud_name = cloud_name[-1]
        cloud_group_name = f"/aws/lambda/{cloud_name}"
        return cloud_group_name

    def _show_log(self, cloud_group_name, **kwargs) -> None:
        backwards = kwargs.get("tail")
        limit_val = kwargs.get("limit")

        cloud_client = client("logs")
        streams = self._get_streams(cloud_client, cloud_group_name)

        start_from_head = not backwards
        next_token_name = "nextBackwardToken" if start_from_head else "nextForwardToken"
        for stream_name in streams:
            response = cloud_client.get_log_events(
                logGroupName=cloud_group_name,
                logStreamName=stream_name,
                limit=limit_val,
                startFromHead=start_from_head,
            )
            prev_token = ""
            next_token = response.get(next_token_name)
            while next_token != prev_token:
                for event in response.get("events"):
                    self.stdout.write(self._format_event(event))

                response = cloud_client.get_log_events(
                    logGroupName=cloud_group_name,
                    logStreamName=stream_name,
                    limit=limit_val,
                    startFromHead=start_from_head,
                    nextToken=next_token
                )
                prev_token = next_token
                next_token = response.get(next_token_name)

    def _show_filtered_log(
        self,
        cloud_group_name,
        query_val,
        **kwargs,
    ) -> None:

        start_time_val = kwargs.get("start_time")
        end_time_val = kwargs.get("end_time")

        if start_time_val is None:
            start_time_val = datetime.datetime.today() - datetime.timedelta(weeks=52)

        if end_time_val is None:
            end_time_val = datetime.datetime.now()

        query = ' '.join([str(item) for item in query_val])

        cloud_client = client("logs")
        start_query_response = cloud_client.start_query(
            logGroupName=cloud_group_name,
            startTime=int(start_time_val.timestamp()),
            endTime=int(end_time_val.timestamp()),
            queryString=query,
        )
        query_id = start_query_response['queryId']
        while True:
            self.stdout.write('Waiting for query to complete ...')
            time.sleep(1)
            response = cloud_client.get_query_results(queryId=query_id)
            for results in response['results']:
                for item2 in results:
                    self.stdout.write(item2['field'] + ': ' + item2['value'])

            if response['status'] != 'Running':
                break

    def _watch_log_group(self, group_name: str) -> None:

        events_hash = set()
        keep_watching = True
        cloud_client = client("logs")
        while keep_watching:
            previous_refresh_time = int(
                (time.mktime(datetime.datetime.now().timetuple()) - 60) * 1000
            )
            keep_watching = self._read_from_streams(
                cloud_client, group_name, events_hash, previous_refresh_time
            )

    def _read_from_streams(
        self,
        cloud_client,
        group_name: str,
        events_hash: set,
        previous_refresh_time,
    ) -> bool:
        try:
            streams = self._get_streams(cloud_client, group_name, previous_refresh_time)
            start_from_head = True
            for stream in streams:
                self._process_stream(cloud_client, stream, group_name, events_hash, start_from_head, previous_refresh_time)

            time.sleep(0.2)
            return True
        except KeyboardInterrupt:
            self.stdout.write("Interrupted")

        return False

    def _get_streams(self, cloud_client, cloud_group_name: str, start_time: float = None) -> List[str]:
        try:
            log_streams_rv = cloud_client.describe_log_streams(
                logGroupName=cloud_group_name,
                orderBy="LastEventTime",
            )
            stream_names = [x.get("logStreamName") for x in log_streams_rv.get("logStreams")]
            return stream_names
        except ClientError as e:
            raise Exception(f"Function {cloud_group_name} has not generated any logs. Trigger the function to generate logs.")

    def _process_stream(
        self,
        cloud_client,
        stream,
        group_name: str,
        events_hash: set,
        start_from_head: bool,
        previous_refresh_time: int
    ) -> None:
        log_events = cloud_client.get_log_events(
            logGroupName=group_name,
            logStreamName=stream,
            startTime=previous_refresh_time,
            startFromHead=start_from_head,
        )

        for stream_event in log_events.get("events"):
            self._process_stream_event(stream_event, events_hash)

    def _process_stream_event(
        self,
        event: dict,
        events_hash: set,
    ) -> None:

        event_hash = hasher.hash_list(
            [
                event.get("timestamp"),
                event.get("message"),
                event.get("ingestionTime"),
            ]
        )

        if event_hash not in events_hash:
            self.stdout.write(self._format_event(event))

        events_hash.add(event_hash)

    def _format_event(self, event) -> str:
        return f"{datetime.datetime.fromtimestamp(event.get('timestamp') / 1000).strftime('%Y-%m-%d %H:%M:%S')} - {event.get('message')} "