# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.6] [Unreleased] [Github Repo]

## [0.0.5] - 2019-10-21
### Added
- GROUP class to send commands to a group of devices (one at a time or parallel)
- Name option parameter, and automatic naming (to make easier manage groups)
- 'Group silent' parameter and 'device silent' parameter to silence output
- Group output attribute, that catches the output of a group command and makes a dictionary like {device_1 :output_1, ..., device_n:output_n}
- Custom path indication with bundle_dir parameter at group creation (then no need to further indicate in cmd method)

## [0.0.4] - 2019-10-14
### Added
- Custom path indication with bundle_dir option in cmd method to indicate the path to the picocom binary for app development (command line or standalone) (For serial devices)

## [0.0.3] - 2019-09-28
### Added
- Silent option
- Custom path indication with bundle_dir option in cmd method to indicate the path to the web_repl_cmd_r binary for app development (command line or standalone) (For wireless devices)

## [0.0.2] - 2019-08-28
### Fix
- PYBOARD class commands output


## [0.0.1] - 2019-08-16
### Added
- First release
