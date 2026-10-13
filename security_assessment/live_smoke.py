"""Explicit live integration check, excluded from offline test discovery."""
import json
import sys

from .osv import OSVClient, OSVError


def main() -> int:
    client = OSVClient(timeout=15)
    print(f"Request: POST {client.query_url} (lodash, npm, 4.17.20)", flush=True)
    try:
        result = client.query("lodash", "npm", "4.17.20")
    except OSVError as exc:
        print(f"Live smoke failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result.to_dict(), indent=2))
    if not result.vulnerabilities:
        print("Live smoke failed: expected findings for this known vulnerable version", file=sys.stderr)
        return 1
    print("Live smoke passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
