#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Check GKE Kubernetes version lifecycle using endoflife.date API.

Primary source: https://endoflife.date/api/google-kubernetes-engine.json
  (auto-scraped from Google's GKE release notes)

GKE uses a pre-existing long-running cluster whose version is NOT managed
in CI config. This script only reports available versions for reference.
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

API_URL = "https://endoflife.date/api/google-kubernetes-engine.json"


def fetch_api():
    """Fetch GKE lifecycle data from endoflife.date."""
    req = urllib.request.Request(API_URL, headers={"User-Agent": "rhdh-skill"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, OSError) as exc:
        print(f"ERROR: Failed to fetch {API_URL}: {exc}", file=sys.stderr)
        sys.exit(1)


def is_supported(entry, today):
    """Check if a GKE version still has any support."""
    eol = entry.get("eol", "N/A")
    if eol == "N/A":
        return True
    if isinstance(eol, bool):
        return not eol
    return eol > today


def get_status(entry, today):
    """Determine support status: Standard, Maintenance, or Unknown."""
    support = entry.get("support", "N/A")
    if support == "N/A" or isinstance(support, bool):
        return "Unknown"
    if support > today:
        return "Standard"
    return "Maintenance"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check GKE Kubernetes version lifecycle using endoflife.date API."
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Output as JSON",
    )
    args = parser.parse_args(argv)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    data = fetch_api()

    supported = [e for e in data if is_supported(e, today)]
    supported.sort(key=lambda e: [int(x) for x in e["cycle"].split(".")], reverse=True)

    if args.json_output:
        result = []
        for e in supported:
            result.append(
                {
                    "version": e["cycle"],
                    "status": get_status(e, today),
                    "eol": e.get("eol", "N/A"),
                    "release_date": e.get("releaseDate", "N/A"),
                }
            )
        json.dump(result, sys.stdout, indent=2)
        print()
        return

    print("=== GKE Version Support (endoflife.date) ===")
    print("Supported minor versions (newest first):")
    print(f"  {'VERSION':<8s} {'STATUS':<12s} {'END OF SUPPORT':<18s} {'RELEASE DATE':<18s}")
    print(f"  {'-------':<8s} {'------':<12s} {'--------------':<18s} {'------------':<18s}")
    for e in supported:
        ver = e["cycle"]
        status = get_status(e, today)
        eol = str(e.get("eol", "N/A"))
        rel = str(e.get("releaseDate", "N/A"))
        print(f"  {ver:<8s} {status:<12s} {eol:<18s} {rel:<18s}")

    print()
    print("NOTE: GKE uses a long-running static cluster. Version is NOT managed in CI config.")
    print("      Updates require manual intervention on the cluster itself.")


if __name__ == "__main__":
    main()
