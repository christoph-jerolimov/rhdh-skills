"""Generic utility functions shared across prow scripts.

NOTE: This file is a subset of rhdh_lifecycle/utils.py (lifecycle skill).
      When modifying either copy, update both to keep them in sync.
"""

from __future__ import annotations


def ver_sort_key(version_str):
    """Sort key for version strings like '4.16' or '26.2'."""
    try:
        return [int(x) for x in version_str.split(".")]
    except ValueError:
        return [0]
