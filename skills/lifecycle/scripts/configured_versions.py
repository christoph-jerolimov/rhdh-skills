"""Print configured MAPT_KUBERNETES_VERSION per branch from CI config files.

Self-contained module for the lifecycle skill. Reads CI config YAML
files from a local openshift/release checkout or via the GitHub API.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

from ruamel.yaml import YAML

_yaml = YAML()
_yaml.preserve_quotes = True

GITHUB_REPO = os.environ.get("OPENSHIFT_RELEASE_REPO", "openshift/release")
_SENTINEL = Path("ci-operator/config/redhat-developer/rhdh")


def resolve_repo_root(explicit_dir=None):
    """Return (root_path, is_remote)."""
    if explicit_dir is not None:
        p = Path(explicit_dir)
        if (p / _SENTINEL).is_dir():
            return p.resolve(), False
        print(f"WARNING: {explicit_dir} does not contain {_SENTINEL}", file=sys.stderr)

    env_dir = os.environ.get("OPENSHIFT_RELEASE_DIR")
    if env_dir:
        p = Path(env_dir)
        if (p / _SENTINEL).is_dir():
            return p.resolve(), False

    cur = Path.cwd()
    while True:
        if (cur / _SENTINEL).is_dir():
            return cur.resolve(), False
        parent = cur.parent
        if parent == cur:
            break
        cur = parent

    return None, True


def _list_yaml_files(config_dir, pattern, root, is_remote):
    """List YAML files in a directory."""
    if is_remote:
        try:
            result = subprocess.run(
                ["gh", "api", f"repos/{GITHUB_REPO}/contents/{config_dir}", "--jq", ".[] | .path"],
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return []
        regex = re.compile(pattern.replace("*", ".*").replace("?", "."))
        return [
            line for line in result.stdout.strip().splitlines() if regex.search(Path(line).name)
        ]
    else:
        local_dir = root / config_dir if root else Path(config_dir)
        if not local_dir.is_dir():
            return []
        return sorted(str(f) for f in local_dir.glob(pattern) if f.is_file())


def _fetch_yaml(filepath, root, is_remote):
    """Read and parse a YAML file."""
    if is_remote:
        url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/HEAD/{filepath}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "rhdh-skill"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return _yaml.load(resp.read().decode("utf-8"))
        except (urllib.error.URLError, OSError):
            return None
    else:
        path = Path(filepath)
        if not path.is_file():
            return None
        with open(path) as fh:
            return _yaml.load(fh)


def _fetch_text(filepath, root, is_remote):
    """Read a file as raw text."""
    if is_remote:
        url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/HEAD/{filepath}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "rhdh-skill"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8")
        except (urllib.error.URLError, OSError):
            return None
    else:
        path = Path(filepath)
        return path.read_text() if path.is_file() else None


def print_configured_versions(config_dir, test_pattern, root, is_remote, mapt_ref=None):
    """Print configured MAPT_KUBERNETES_VERSION per branch."""
    mapt_tag = ""
    if mapt_ref:
        ref_path = mapt_ref if is_remote else str(root / mapt_ref) if root else mapt_ref
        text = _fetch_text(ref_path, root, is_remote)
        if text:
            for line in text.splitlines():
                if "tag:" in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        mapt_tag = parts[1]
                    break

    prefix = "redhat-developer-rhdh-"
    files = _list_yaml_files(config_dir, f"{prefix}*.yaml", root, is_remote)
    if not files:
        return

    pattern_re = re.compile(test_pattern)
    print("Configured MAPT_KUBERNETES_VERSION per branch:")
    for filepath in files:
        name = Path(filepath).stem
        branch = name[len(prefix) :] if name.startswith(prefix) else name
        data = _fetch_yaml(filepath, root, is_remote)
        if not data or "tests" not in data:
            continue
        versions = set()
        for test in data["tests"]:
            test_name = test.get("as", "")
            if pattern_re.search(test_name):
                ver = test.get("steps", {}).get("env", {}).get("MAPT_KUBERNETES_VERSION", "N/A")
                versions.add(ver)
        ver_str = ",".join(sorted(versions)) if versions else "N/A"
        print(f"  {branch}: {ver_str}")
    if mapt_tag:
        print(f"MAPT image: mapt:{mapt_tag}")
    print()
