# Changelog

Notable changes to this project will be documented in this file.

## [Unreleased]

## [beta] - 2025-07-27

### Fixed

- File extention (.txt) was removed from file name generation in `generate_file_name` function

### Added

- Prefixed patient names with "仮" and "カリ".
- Random phone numbers starts with a prefix like "099".
- Added logics to use real Japanese postal codes and consistent addresses. Addresses below town level are randomly generated, but 'chome (丁目)' is fixed to '99 丁目', and building names are prefixed with "仮" to avoid real addresses.

### Changed

- Switched default port from 22 to 2222 in SSH setup

## [1.1.0] - 2025-06-30

### Added

- Dockerized Nginx + Certbot reverse proxy setup
- Django + S3 static/media configuration

## [1.0.0] - 2025-06-01

### Added

- Initial release: Django app with EC2 deployment, PostgreSQL, and basic nginx setup
