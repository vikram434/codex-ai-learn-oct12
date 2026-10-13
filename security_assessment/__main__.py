import argparse
import json
import os
import sys

from .osv import OSVClient, OSVError


def main() -> int:
    parser = argparse.ArgumentParser(description="Query OSV for one package version")
    parser.add_argument("name")
    parser.add_argument("ecosystem")
    parser.add_argument("version")
    parser.add_argument("--base-url", default=os.environ.get("OSV_BASE_URL", "https://api.osv.dev"))
    parser.add_argument("--timeout", type=float, default=10)
    args = parser.parse_args()
    try:
        result = OSVClient(args.base_url, args.timeout).query(args.name, args.ecosystem, args.version)
    except OSVError as exc:
        print(json.dumps({
            "status": "source_failure", "error": type(exc).__name__, "detail": str(exc),
            "message": "Assessment unavailable from this source; no security conclusion can be drawn.",
        }), file=sys.stderr)
        return 1
    except ValueError as exc:
        print(json.dumps({"status": "invalid_input", "error": type(exc).__name__, "message": str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps(result.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

