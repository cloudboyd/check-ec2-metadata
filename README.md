# Check AWS EC2 Metadata
This script is designed to fetch metadata from an EC2 instance in a structured and flexible way. It supports both IMDSv1 and IMDSv2, works with IPv4 and IPv6, and provides options to retrieve metadata in nested JSON or simple JSON formats.

## Features
- IMDSv1 and IMDSv2 Support: Works with both Instance Metadata Service versions.
- IPv4 and IPv6 Support: Can fetch metadata using IPv4 or IPv6 endpoints.
- Nested JSON Output: Returns metadata in a hierarchical JSON structure.
- Simple JSON Output: Returns only the value of a specified key in a simple JSON format. (Only works with --key/-k)
- Metadata Access Check: Verifies if metadata access is enabled on the instance.
- IMDS Version Check: Determines whether the instance supports IMDSv1, IMDSv2, or both.

## 📂 What included in this repository
- **Python file**
  - `check-ec2-metadata.py` : Contains code that check AWS EC2 instance's metadata. See usage below.
- **README.md**
  - You're reading this file.

## Assumption on this project
  - If no argument provided, shows all metadata on the running instance. (same as `-k ""`)
  - All requests will try to retrieve data with IMDSv2 first, if IMDSv2 fails, attempt to fetch metadata using IMDSv1
  - Provide `--check-imds-version` or `-v` for checking IMDS version supported on the instance. And might be also useful for auditing if required.
  - Provide `--check-metadata-access` or `-m` for checking if metada access is enabled on the instance. And might be also useful for auditing if required.
  - The output data shows in a JSON format (including error message if any, and also for -v, -m).
  - The instance should already had python/python3 installed. (Both Windows and Linux should be supported)
  - This script can be run in the instance by user, or can be remotely triggered by other 3rd party tools (if valid credential provided).
  - This script does not support `/latest/dynamic` or `/latest/user-data` endpoints, only fetch data from `/latest/meta-data` endpoint.


## Usage:
See below for how to use, and all available options:
> usage: check-ec2-metadata.py [-h] [-6] [-k KEY] [-s] [-v] [-m]
> 
> optional arguments:
>  -h, --help            : show this help message and exit
>  -6, --ipv6            : Use IPv6 metadata endpoint.
>  -k KEY, --key KEY     : Specific metadata key or path to fetch. If empty, lists all keys at the root path.
>  -s, --simple          : Show only the value of the specified key in simple JSON format.
>  -v, --check-imds-version : Check IMDS version support (v1, v2, or both). Must be used with -k
>  -m, --check-metadata-access : Check if metadata access is enabled.


## 🧪 Example Outputs:
- Check if metadata access is enabled on the instance:
  - if metatdata access is enalbed:
