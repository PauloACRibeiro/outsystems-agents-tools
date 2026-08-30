#!/usr/bin/env python3
"""Write an OMI-to-Mentor-session correlation file.

Writes omi-link.json into an already-finalized polling-behavior session
directory (one whose name is the real Mentor runId, not a still-provisional
pending-* placeholder), recording which OMI scenario/prompt produced that
Mentor run. This is a forward-only correlation convention this repo owns;
it does not modify the polling-behavior skill itself.

Exit 0 on success; 2 on a usage/target error (missing directory, missing
meta.json, or a still-provisional pending-* directory name).
"""
import argparse
import json
import sys
from pathlib import Path


def write_link(session_dir, omi_scenario, prompt_source, recorded_by):
    session_dir = Path(session_dir)
    if not session_dir.is_dir():
        raise SystemExit(f"no such session directory: {session_dir}")
    if session_dir.name.startswith("pending-"):
        raise SystemExit(
            f"{session_dir} is still a provisional session directory (name "
            "starts with 'pending-') - link only after the polling skill's "
            "update-run-id step renames it to the real Mentor runId, or the "
            "link will be orphaned by the rename")
    meta_path = session_dir / "meta.json"
    if not meta_path.is_file():
        raise SystemExit(
            f"{session_dir} has no meta.json - not a polling-behavior session directory")

    link = {
        "omi_scenario": omi_scenario,
        "prompt_source": prompt_source,
        "recorded_by": recorded_by,
    }
    link_path = session_dir / "omi-link.json"
    link_path.write_text(json.dumps(link, indent=2) + "\n", encoding="utf-8")
    return link_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-dir", required=True, type=Path)
    parser.add_argument("--omi-scenario", required=True)
    parser.add_argument("--prompt-source", required=True)
    parser.add_argument("--recorded-by", required=True)
    args = parser.parse_args()

    try:
        link_path = write_link(
            args.session_dir, args.omi_scenario, args.prompt_source, args.recorded_by)
    except SystemExit as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"wrote {link_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
