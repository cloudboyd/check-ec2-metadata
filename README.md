# Check AWS EC2 Metadata
This script is designed to fetch metadata from an EC2 instance in a structured and flexible way. It supports both IMDSv1 and IMDSv2, works with IPv4 and IPv6, and provides options to retrieve metadata in nested JSON or simple JSON formats.

## 💡 Features
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

## ‼️ Assumption on this project
  - If no argument provided, shows all metadata on the running instance. (same as `-k ""`)
  - All requests will try to retrieve data with IMDSv2 first, if IMDSv2 fails, attempt to fetch metadata using IMDSv1
  - Provide `--check-imds-version` or `-v` for checking IMDS version supported on the instance. And might be also useful for auditing if required.
  - Provide `--check-metadata-access` or `-m` for checking if metada access is enabled on the instance. And might be also useful for auditing if required.
  - The output data shows in a JSON format (including error message if any, and also for -v, -m).
  - The instance should already had python/python3 installed. (Both Windows and Linux should be supported)
  - This script can be run in the instance by user, or can be remotely triggered by other 3rd party tools (if valid credential provided).
  - This script does not support `/latest/dynamic` or `/latest/user-data` endpoints, only fetch data from `/latest/meta-data` endpoint.


## 💁🏽 Usage:
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
- Check if metadata access is enabled on the instance (`-m argument`):
<img width="394" alt="Screenshot 2025-03-24 at 12 47 48 AM" src="https://github.com/user-attachments/assets/aa083df5-bbb8-42d8-960b-183c2da8d328" />
<img width="398" alt="Screenshot 2025-03-24 at 12 47 02 AM" src="https://github.com/user-attachments/assets/b53d3227-38bc-4617-8a11-f33f3859331a" />

- Check which IMDS versions are supported on the instance (`-v argument`):
<img width="401" alt="Screenshot 2025-03-24 at 12 48 13 AM" src="https://github.com/user-attachments/assets/a6387703-3b38-45c9-b844-d127e82fb571" />
<img width="400" alt="Screenshot 2025-03-24 at 12 47 35 AM" src="https://github.com/user-attachments/assets/fd1fc9b9-c52e-4fa3-8141-1b42c691c6ec" />

- Check if IPv6 is enabled on the instance (`-6 argument`) :
  - Please note: If IPv6 is enabled, it will try to fetch the key data as provided (You can also check if IPv6 is enabled with `-k ipv6`; IPv6 returned if it's available, or else return `No metadata found.`)
<img width="370" alt="Screenshot 2025-03-24 at 12 45 56 AM" src="https://github.com/user-attachments/assets/54f144d1-1bfb-4c0f-a573-e2ee7e12cf32" />
<img width="419" alt="Screenshot 2025-03-24 at 1 44 55 AM" src="https://github.com/user-attachments/assets/836ff516-3d1f-4fd5-9b83-3a73d10c0f60" />
<img width="430" alt="Screenshot 2025-03-24 at 1 48 53 AM" src="https://github.com/user-attachments/assets/fb4e951a-0842-4a01-9f4b-6261c2df7727" />

- Check the value of the provided key, and return output in nested JSON format (`-k argument`):
<img width="465" alt="Screenshot 2025-03-24 at 12 48 37 AM" src="https://github.com/user-attachments/assets/a6c2e3fb-cb46-46f0-a36a-74bf9b628024" />
<img width="845" alt="Screenshot 2025-03-24 at 12 49 39 AM" src="https://github.com/user-attachments/assets/b650df90-f6ea-4efa-8ab7-034d182dbeb5" />

- Check the value of the provided key, and return output in simple JSON format (`-k <KEY> and -s arguments`):
<img width="866" alt="Screenshot 2025-03-24 at 12 49 49 AM" src="https://github.com/user-attachments/assets/ebe44255-7868-49c7-85b6-49be53d575bf" />
<img width="484" alt="Screenshot 2025-03-24 at 12 48 50 AM" src="https://github.com/user-attachments/assets/b2e4c8be-ad4e-49b2-ad4c-501a0d35d3a2" />

- Below shows that the request is fetched with IMDSv2 by default:
<img width="860" alt="Screenshot 2025-03-24 at 12 52 25 AM" src="https://github.com/user-attachments/assets/9c244306-3aaa-4f0c-8145-1e9a050ae6d7" />

- Below shows that if no key is provided, it will show all metadata information:
<img width="1286" alt="Screenshot 2025-03-24 at 12 44 52 AM" src="https://github.com/user-attachments/assets/7048d28b-fa08-43f2-ab5c-a90f226d4f6e" />







