from cdev.management.base import BaseCommand, OutputWrapper
from argparse import ArgumentParser
import boto3
import os
from cdev.backend import cloud_mapper_manager

RUUID = 'cdev::simple::staticsite'

class sync_files(BaseCommand):

    help = """
        Get the logs of a deployed lambda function
    """

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument("resource_name", type=str, help= "The function that you want to watch")
        parser.add_argument("--dir", type=str, help= "watch the logs. If this flag is passed, only --start_time flag is read")
        

    def command(self, *args, **kwargs):
        resource_name = kwargs.get("resource_name")
        override_directory = kwargs.get("dir")


        bucket_name = cloud_mapper_manager.get_output_value_by_name(RUUID, resource_name, "bucket_name")

        s3 = boto3.resource('s3') 
        bucket = s3.Bucket(bucket_name)

        for subdir, dirs, files in os.walk(override_directory):
            for file in files:
                full_path = os.path.join(subdir, file)
                
                key_name = os.path.relpath(full_path,override_directory,)
                bucket.upload_file(full_path, key_name)
                
