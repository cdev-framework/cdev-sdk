# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
All releases will correspond to releases on [PyPI](https://pypi.org/project/cdev/).
All release will have a corresponding git tag.

## [Unreleased]
- Fix bug with third party project's that have no top_level.txt and have a '-' in the name
- Fix bug with returned package names from relative imported files

## [0.0.5] - 2022-03-09
### Added
- Updated Manifest to include core/utils/fs_manager/standard_library_names/*

## [0.0.4] - 2022-03-09
### Changed
- Make Layer and Serverless Function artifacts use workspace relative paths
- Deduplicate resources generated from the `finder` package
### Added
- Support for parsing functions with annotations 
- Support for adding JWT authorizers with the API Gateway
- Support for changing a Project's base settings class
- Slack Bot template project

## [0.0.3] - 2022-02-18
### Added
- Create 'MANIFEST.in' to include 'cdev/template-projects/' and exclude '\_\_pycache\_\_'
- Add 'MANIFEST.in' to the final package 
- Added this Change Log

## [0.0.2] - 2022-02-18
### Added
- Create project on PyPI


