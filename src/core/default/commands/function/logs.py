
from argparse import ArgumentParser
import time, math, datetime

from typing import List, Dict
from boto3 import client

from core.constructs.commands import BaseCommand, OutputWrapper

from core.utils import hasher

from core.default.commands.function.utils import get_cloud_id_from_cdev_name




class show_logs(BaseCommand):

    help = """
        Get the logs of a deployed lambda function
    """

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            "function_name", type=str, help="The function that you want to watch. Name must include component name. ex: comp1.demo_function"
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
            "--number",
            action="store_true",
            help="number of events to show. Must be used with --tail.",
        )

    def command(self, *args, **kwargs):

        full_function_name: str = kwargs.get("function_name")
        component_name = full_function_name.split('.')[0]
        function_name = full_function_name.split('.')[1]
        watch_val = kwargs.get("watch")
        tail_val = kwargs.get("tail")
        number_val = kwargs.get("number")

        cloud_name = get_cloud_id_from_cdev_name(component_name, function_name).split(":")[-1]

        if not cloud_name:
            self.stdout.write(f"Could not find function {function_name} in component {component_name}")
            return

        cloud_watch_group_name = f"/aws/lambda/{cloud_name}"

        if watch_val:
            _watch_log_group(cloud_watch_group_name, self.stdout)
            return

        cloud_watch_client = client("logs")
        print(cloud_watch_group_name)
        log_streams_rv = cloud_watch_client.describe_log_streams(
            logGroupName=cloud_watch_group_name,
            orderBy="LastEventTime",
        )

        streams = _get_needed_streams(log_streams_rv.get("logStreams"))

        for stream in streams:
            response = cloud_watch_client.get_log_events(
                logGroupName=cloud_watch_group_name,
                logStreamName=stream,
                startFromHead=True,
            )

            for event in response.get("events"):
                self.stdout.write(
                    f"{datetime.datetime.fromtimestamp(event.get('timestamp')/1000).strftime('%Y-%m-%d %H:%M:%S')} - {event.get('message')}"
                )


def _watch_log_group(group_name: str, stdout: OutputWrapper, args=None):
    cloud_watch_client = client("logs")
    _previous_refresh_time = int(
        (time.mktime(datetime.datetime.now().timetuple()) - 60) * 1000
    )
    events_hash = set()

    while True:
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

                    if not event_hash in events_hash:
                        stdout.write(
                            f"{datetime.datetime.fromtimestamp(event.get('timestamp')/1000).strftime('%Y-%m-%d %H:%M:%S')} - {event.get('message')}"
                        )

                    events_hash.add(event_hash)

                _previous_refresh_time = int(
                    (time.mktime(datetime.datetime.now().timetuple()) - 60) * 1000
                )

                time.sleep(0.2)
        except KeyboardInterrupt:
            return




def _get_needed_streams(streams: List[Dict], start_time: float = None) -> List[str]:
    stream_names = [x.get("logStreamName") for x in streams]

    return stream_names
