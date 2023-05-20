# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
All releases will correspond to releases on [PyPI](https://pypi.org/project/cdev/).
All release will have a corresponding git tag.

## [0.0.30] - 2023-05-25

### Fixed

- Fixed error with Kinesis Data Stream remove

## [0.0.30] - 2023-03-29

### Fixed

- Fixed error with Kinesis Data Stream permissions

## [0.0.29] - 2023-03-29

### Added

- Added the Kinesis Data Stream resource and event

## [0.0.28]

### Fixed

- Updated json safe write to handle missing directories

## [0.0.27]

### Added

- Added the `delete-environment` command

## [0.0.26]

### Added

- Added the `remove-resource` command to help when the backend gets in an inconsistent state

## [0.0.25]

### Added

- Detailed view of the changes that will be deployed via the `--detail` flag
- Add `url` as an output value for Sqs Queues

## [0.0.24] - 2023-02-06

### Fixed

- Reimplemented packaged module discovery and layer creation
- Update Lambda function to use dependencies as part of the hash

## [0.0.23] - 2023-01-23

### Fixed

- Fix small bug with relative locations in RECORD files

## [0.0.22] - 2023-01-21

### Fixed

- Updated packaged modules to use RECORD file for generating needed files

## [0.0.21] - 2023-01-17

### Fixed

- Bug with parsing relative packages with multiple levels

## [0.0.20] - 2023-01-08

### Fixed

- Bug with parsing nested relative packages

### Added

- Add vpc parameters to Serverless Function resource
- Add timeout and dead letter queue parameters to SQS Queue Resource
- Add parameter for API Gateway to use IAM authentication

## [0.0.13] - 2022-09-29

### Fixed

- Create the aws config files if they do not exist when creating credentials
- Refactor the package names and reflect this on the website

## [0.0.12] - 2022-09-01

### Added

- Add sequence to ask for the users `Aws` credentials when creating a project.
- Add option to create a bucket even if buckets are available

## [0.0.11] - 2022-08-25

### Added

- Update the number of buckets in initialization selection tool from 10 to 25
- Add `__init__.py` file to the twilio quick start project
- Update the output of cloud values during the `deploy` command to use a `rich` table
- Update the output of current state output

### Fixed

- Fix bug in the backend component diff logic

## [0.0.9] - 2022-06-20

### Added

- Add support for Serverless Function Resource to preserve original callable object
- Add `pre-commit` to the code base to be used for styling
- Add `tox` to help with testing multiple `python` versions
- Add CONTRIBUTING.md
- Add type hint to functions
- Update imports to be absolute when possible
- Add function to parse qualified resources into its parts
- Add support for lambda functions to update the handler
- Add option to set your memory, storage and timeout on serverless functions
- Add user input for setting artifact bucket when creating a new project
- Add query, tail and limit args to logging function
- Add sync to watch for filesystem changes
- Add keep-in-sync argument to _cdev run static_site.sync <resource>_
- Add tags to resources that support them

### Fixed

- Fix issues with a bucket when it is not empty and we need to delete it
- Refactor automated packaging system
- Refactor Project, Environment, and Workspace abstractions
- Fix issue with uploading static site files if the mimetype could not be guessed

## [0.0.8] - 2022-04-05

### Added

- Add Twilio quick start template

## [0.0.7] - 2022-03-29

## Added

- Add `sync` command for static sites
- Add template project for power tools library
- Add support for api routes to return different types than 'application/json'

## Changed

- Fix bug with syncing index and error documents for static sites
- Fix bug with deduplicating more than two of the same resource.
- Fix bug with not parsing type annotations in function definitions

## [0.0.6] - 2022-03-14

## Added

- Added 'relationaldb.shell' command to open interactive session with a db
- Add flag to output command to only print the value

## Changed

- Fix bug with third party project's that have no top_level.txt and have a '-' in the name
- Fix bug with returned package names from relative imported files
- Fix bug with naming of key for relationdb output cluster_arn value
- Fix bug with db shell command looking up wrong key from output

## [0.0.5] - 2022-03-09

### Added

- Updated Manifest to include core/utils/fs_manager/standard_library_names/\*

## [0.0.4] - 2022-03-09

### Added

- Support for parsing functions with annotations
- Support for adding JWT authorizers with the API Gateway
- Support for changing a Project's base settings class
- Slack Bot template project### Added
- Support for parsing functions with annotations
- Support for adding JWT authorizers with the API Gateway
- Support for changing a Project's base settings class
- Slack Bot template project

### Changed

- Make Layer and Serverless Function artifacts use workspace relative paths
- Deduplicate resources generated from the `finder` package

## [0.0.3] - 2022-02-18

### Added

- Create 'MANIFEST.in' to include 'cdev/template-projects/' and exclude '\_\_pycache\_\_'
- Add 'MANIFEST.in' to the final package
- Added this Change Log

## [0.0.2] - 2022-02-18

### Added

- Create project on PyPI
