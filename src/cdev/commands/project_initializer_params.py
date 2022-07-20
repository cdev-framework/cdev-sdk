BUCKET_FILTERS = ["cdev-bucket", "cdev-staticsite"]

GENERATED_BUCKET_SUFFIX_LENGTH = 8

GENERATED_BUCKET_BASE = "cdev-generated-artifacts"

ARTIFACT_BUCKET_INTRO_MESSAGE = """
You will need to provide an S3 bucket that will be used by Cdev to upload your project artifacts (functions, layers, etc).
"""

MAXIMUM_BUCKETS_LISTED = 10

LIST_BUCKETS_FAILED = """
Failed to list your accounts S3 Buckets for selection. To use some of the main features of Cdev, you will need to create an S3 Bucket and provide it to Cdev via your `settings/base_settings.py.py` file.
"""

TOO_MANY_AVAILABLE_BUCKETS_MESSAGE = """
Your account has too many buckets for our selection utility. You can input the name of the bucket you would like to use for this project:
"""

ARTIFACT_BUCKET_SELECT_MESSAGE = """
Select one of the following buckets that are available in your account by using the UP and DOWN arrows key:
"""

NAME_OF_BUCKET_PROMPT = """
Name of bucket to store artifacts"""

BUCKET_NOT_AVAILABLE_MESSAGE = """
The provided bucket ({bucket_name}) is not available in your current account. Available buckets are:
"""

CONFIRM_BUCKET_CREATION = """
Confirm bucket creation"""

NO_BUCKET_SELECT_MESSAGE = """
No buckets were found in your AWS account, would you like one to be automatically created for you?
"""

CREATE_ARTIFACT_BUCKET_SUCCESS = """
Successfully created a S3 Bucket! Created bucket {bucket_name}.
"""

CREATE_ARTIFACT_BUCKET_FAILED = """
Failed to create the S3 Bucket. To use some of the main features of Cdev, you will need to create an S3 Bucket and provide it to Cdev via your `settings/base_settings.py.py` file.

See below for the exact error:
"""

DO_NOT_CREATE_BUCKET_SELECT_MESSAGE = """
No bucket created. To use some of the main features of Cdev, you will need to create an S3 Bucket and provide it to Cdev via your `settings/base_settings.py.py` file.
"""
