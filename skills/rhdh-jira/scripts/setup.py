#!/usr/bin/env python3
"""Verify acli installation and Jira authentication for RHDH projects."""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

RHDH_PROJECTS = ["RHIDP", "RHDHPLAN", "RHDHBUGS", "RHDHSUPP"]
JIRA_CONFIG_RELATIVE = Path(".config", "acli", "jira_config.yaml")


def find_acli():
    """Find acli binary on PATH."""
    acli = shutil.which("acli")
    if acli:
        return acli

    # Check common locations on Windows
    if sys.platform == "win32":
        home = Path.home()
        candidates = [
            home / ".path" / "acli.exe",
            home / "AppData" / "Local" / "acli" / "acli.exe",
        ]
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)

    return None


def check_config():
    """Check if Jira API token config exists."""
    config_path = Path.home() / JIRA_CONFIG_RELATIVE
    if not config_path.exists():
        return None, "not found"

    try:
        content = config_path.read_text(encoding="utf-8")
        if "api_token" in content:
            return str(config_path), "api_token"
        elif "oauth" in content.lower():
            return str(config_path), "oauth"
        else:
            return str(config_path), "unknown"
    except OSError as e:
        return None, f"read error: {e}"


def smoke_test(acli_path):
    """Run a smoke test to verify Jira connectivity."""
    try:
        result = subprocess.run(
            [acli_path, "jira", "project", "list", "--recent", "1"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        if result.returncode == 0 and stdout.strip():
            return True, stdout.strip()
        return False, stderr.strip() or "empty response"
    except subprocess.TimeoutExpired:
        return False, "timeout after 30s"
    except OSError as e:
        return False, str(e)


def check_projects(acli_path):
    """Check which RHDH projects are accessible."""
    accessible = []
    inaccessible = []

    for project in RHDH_PROJECTS:
        try:
            result = subprocess.run(
                [acli_path, "jira", "project", "view", "--key", project],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=15,
            )
            if result.returncode == 0:
                accessible.append(project)
            else:
                stderr = result.stderr or ""
                inaccessible.append((project, stderr.strip()))
        except (subprocess.TimeoutExpired, OSError) as e:
            inaccessible.append((project, str(e)))

    return accessible, inaccessible


def main():
    parser = argparse.ArgumentParser(
        description="Verify acli installation and Jira authentication for RHDH."
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--quick", action="store_true", help="Skip project accessibility check")
    args = parser.parse_args()

    results = {
        "acli_found": False,
        "acli_path": None,
        "config_found": False,
        "config_path": None,
        "auth_type": None,
        "connectivity": False,
        "connectivity_detail": None,
        "projects_accessible": [],
        "projects_inaccessible": [],
        "overall": "fail",
    }

    # Step 1: Find acli
    acli_path = find_acli()
    if acli_path:
        results["acli_found"] = True
        results["acli_path"] = acli_path
    else:
        results["connectivity_detail"] = "acli not found on PATH"
        _output(results, args.json)
        sys.exit(1)

    # Step 2: Check config
    config_path, auth_type = check_config()
    if config_path:
        results["config_found"] = True
        results["config_path"] = config_path
        results["auth_type"] = auth_type

    # Step 3: Smoke test (do NOT use 'acli auth status' — it lies with API tokens)
    ok, detail = smoke_test(acli_path)
    results["connectivity"] = ok
    results["connectivity_detail"] = detail

    if not ok:
        _output(results, args.json)
        sys.exit(1)

    # Step 4: Check project access
    if not args.quick:
        accessible, inaccessible = check_projects(acli_path)
        results["projects_accessible"] = accessible
        results["projects_inaccessible"] = [{"project": p, "error": e} for p, e in inaccessible]

    results["overall"] = "pass"
    _output(results, args.json)
    sys.exit(0)


def _output(results, as_json):
    """Print results in JSON or human-readable format."""
    if as_json:
        json.dump(results, sys.stdout, indent=2)
        print()
        return

    print("=" * 50)
    print("RHDH Jira Setup Check")
    print("=" * 50)

    # acli
    if results["acli_found"]:
        print(f"  [PASS] acli found: {results['acli_path']}")
    else:
        print("  [FAIL] acli not found on PATH")
        print("         Install from: https://developer.atlassian.com/cloud/acli/")
        return

    # Config
    if results["config_found"]:
        print(f"  [PASS] Config found: {results['config_path']}")
        print(f"         Auth type: {results['auth_type']}")
    else:
        print("  [WARN] No Jira config found at ~/.config/acli/jira_config.yaml")
        print("         Run: acli auth login")

    # Connectivity
    if results["connectivity"]:
        print("  [PASS] Jira connectivity verified")
    else:
        print(f"  [FAIL] Jira connectivity failed: {results['connectivity_detail']}")
        return

    # Projects
    if results["projects_accessible"]:
        print(f"  [PASS] Projects accessible: {', '.join(results['projects_accessible'])}")
    if results["projects_inaccessible"]:
        for item in results["projects_inaccessible"]:
            print(f"  [WARN] {item['project']}: {item['error']}")

    print()
    print(f"Overall: {results['overall'].upper()}")


if __name__ == "__main__":
    main()
