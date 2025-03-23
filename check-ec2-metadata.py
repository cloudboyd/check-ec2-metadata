import requests
import argparse
import json

# Metadata endpoints
IMDS_IPV4_URL = "http://169.254.169.254"
IMDS_IPV6_URL = "http://[fd00:ec2::254]"
IMDS_TOKEN_HEADER = "X-aws-ec2-metadata-token"
IMDS_TOKEN_TTL = "21600"  # 6 hours

def fetch_imdsv2_token(base_url):
    """Fetch IMDSv2 token."""
    token_url = f"{base_url}/latest/api/token"
    headers = {"X-aws-ec2-metadata-token-ttl-seconds": IMDS_TOKEN_TTL}
    try:
        response = requests.put(token_url, headers=headers, timeout=2)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return None

def fetch_metadata(base_url, token=None, key=""):
    """Fetch EC2 metadata and determine if the key is the last key."""
    metadata_url = f"{base_url}/latest/meta-data/{key}"
    headers = {IMDS_TOKEN_HEADER: token} if token else {}
    try:
        response = requests.get(metadata_url, headers=headers, timeout=2)
        response.raise_for_status()
        content = response.text

        # If key is empty (root path), treat it as a directory
        if key == "":
            return content, False  # It's a directory (not the last key)

        # Check if the key is a directory (ends with '/')
        if key.endswith("/"):
            return content, False  # It's a directory (not the last key)

        # Check if the content ends with '/'
        if content.endswith("/"):
            return content, False  # It's a directory (not the last key)

        # Check if the content contains multiple lines
        if "\n" in content:
            return content, False  # It's a list of keys (not the last key)

        # If none of the above, treat it as the last key
        return content, True
    except requests.exceptions.RequestException as e:
        return None, False

def list_keys(base_url, token=None, key=""):
    """List available metadata keys at the specified path."""
    metadata, is_last_key = fetch_metadata(base_url, token=token, key=key)
    if metadata and not is_last_key:
        return metadata.splitlines()
    return []

def check_metadata_access(base_url):
    """Check if metadata access is enabled on the instance."""
    # Attempt to fetch metadata using IMDSv2 first
    token = fetch_imdsv2_token(base_url)
    if token:
        try:
            response = requests.get(
                f"{base_url}/latest/meta-data/instance-id",
                headers={IMDS_TOKEN_HEADER: token},
                timeout=2,
            )
            if response.status_code == 200:
                return True, token  # Metadata access is enabled, return token
        except requests.exceptions.RequestException:
            pass

    # If IMDSv2 fails, attempt to fetch metadata using IMDSv1
    try:
        response = requests.get(f"{base_url}/latest/meta-data/instance-id", timeout=2)
        if response.status_code == 200:
            return True, None  # Metadata access is enabled, no token needed
    except requests.exceptions.RequestException:
        pass

    # If both attempts fail, metadata access is likely disabled
    return False, None

def check_imds_version(base_url):
    """Check if the instance supports IMDSv1, IMDSv2, or both."""
    # Check IMDSv2 support
    imdsv2_supported = False
    token = fetch_imdsv2_token(base_url)
    if token:
        try:
            response = requests.get(
                f"{base_url}/latest/meta-data/instance-id",
                headers={IMDS_TOKEN_HEADER: token},
                timeout=2,
            )
            if response.status_code == 200:
                imdsv2_supported = True
        except requests.exceptions.RequestException:
            pass
    else:
        pass

    # Check IMDSv1 support
    imdsv1_supported = False
    try:
        response = requests.get(f"{base_url}/latest/meta-data/instance-id", timeout=2)
        if response.status_code == 200:
            imdsv1_supported = True
    except requests.exceptions.RequestException:
        pass

    # Determine IMDS version support
    if imdsv1_supported and imdsv2_supported:
        return "Supports both IMDSv1 and IMDSv2"
    elif imdsv1_supported:
        return "Supports only IMDSv1"
    elif imdsv2_supported:
        return "Supports only IMDSv2"
    else:
        return "Does not support IMDSv1 or IMDSv2"

def is_ipv6_enabled():
    """Check if the IPv6 metadata endpoint is reachable using IMDSv2."""
    # Fetch IMDSv2 token for IPv6
    token = fetch_imdsv2_token(IMDS_IPV6_URL)
    if token:
        try:
            response = requests.get(
                f"{IMDS_IPV6_URL}/latest/meta-data/instance-id",
                headers={IMDS_TOKEN_HEADER: token},
                timeout=2,
            )
            if response.status_code == 200:
                return True  # IPv6 is enabled
        except requests.exceptions.RequestException:
            pass

    # If IMDSv2 fails, attempt to fetch metadata using IMDSv1
    try:
        response = requests.get(f"{IMDS_IPV6_URL}/latest/meta-data/instance-id", timeout=2)
        if response.status_code == 200:
            return True  # IPv6 is enabled
    except requests.exceptions.RequestException:
        pass

    # If both attempts fail, IPv6 is likely not enabled
    return False

def build_nested_json(keys, value):
    """Build a nested JSON structure from a list of keys and a value."""
    if not keys:
        return value
    return {keys[0]: build_nested_json(keys[1:], value)}

def fetch_nested_metadata(base_url, token=None, key=""):
    """Fetch metadata and return it as a nested JSON structure."""
    metadata, is_last_key = fetch_metadata(base_url, token=token, key=key)
    if metadata:
        if is_last_key:
            # If it's the last key, return the value
            return metadata
        else:
            # If it's a directory, fetch all keys and build nested JSON
            keys = metadata.splitlines()
            nested_json = {}
            for k in keys:
                nested_json[k] = fetch_nested_metadata(base_url, token=token, key=f"{key}/{k}" if key else k)
            return nested_json
    else:
        return None

def main():
    parser = argparse.ArgumentParser(description="Fetch EC2 metadata.")
    parser.add_argument("-6", "--ipv6", action="store_true", help="Use IPv6 metadata endpoint.")
    parser.add_argument("-k", "--key", type=str, default="", help="Specific metadata key or path to fetch. If empty, lists all keys at the root path.")
    parser.add_argument("-s", "--simple", action="store_true", help="Show only the value of the specified key in simple JSON format.")
    parser.add_argument("-v", "--check-imds-version", action="store_true", help="Check IMDS version support (v1, v2, or both).")
    parser.add_argument("-m", "--check-metadata-access", action="store_true", help="Check if metadata access is enabled.")
    args = parser.parse_args()

    # Determine the base URL (IPv4 or IPv6)
    if args.ipv6:
        if is_ipv6_enabled():
            base_url = IMDS_IPV6_URL
        else:
            print(json.dumps({"error": "IPv6 is not enabled on this instance."}, indent=2))
            return
    else:
        base_url = IMDS_IPV4_URL

    if args.check_metadata_access:
        # Check if metadata access is enabled
        access_enabled, token = check_metadata_access(base_url)
        if access_enabled:
            print(json.dumps({"metadata_access": "enabled"}, indent=2))
        else:
            print(json.dumps({"metadata_access": "disabled"}, indent=2))
    elif args.check_imds_version:
        # Check IMDS version support
        access_enabled, token = check_metadata_access(base_url)
        if access_enabled:
            result = check_imds_version(base_url)
            print(json.dumps({"imds_version_support": result}, indent=2))
        else:
            print(json.dumps({"error": "Metadata access is disabled. Cannot check IMDS version."}, indent=2))
    else:
        # Fetch metadata or list keys
        access_enabled, token = check_metadata_access(base_url)
        if access_enabled:
            if args.key:
                if args.simple:
                    # Fetch specific metadata and return in simple JSON format
                    metadata, is_last_key = fetch_metadata(base_url, token=token, key=args.key)
                    if metadata and is_last_key:
                        print(json.dumps({"value": metadata}, indent=2))
                    else:
                        print(json.dumps({"error": "No value found for the specified key."}, indent=2))
                else:
                    # Fetch specific metadata and build nested JSON
                    nested_json = fetch_nested_metadata(base_url, token=token, key=args.key)
                    if nested_json:
                        # Build nested JSON structure for the provided key
                        keys = args.key.split("/")
                        result = build_nested_json(keys, nested_json)
                        print(json.dumps(result, indent=2))
                    else:
                        print(json.dumps({"error": "No metadata found."}, indent=2))
            else:
                # List all keys at the root path
                nested_json = fetch_nested_metadata(base_url, token=token, key="")
                if nested_json:
                    print(json.dumps(nested_json, indent=2))
                else:
                    print(json.dumps({"error": "No keys found."}, indent=2))
        else:
            print(json.dumps({"error": "Metadata access is disabled. Cannot fetch metadata or list keys."}, indent=2))

if __name__ == "__main__":
    main()
