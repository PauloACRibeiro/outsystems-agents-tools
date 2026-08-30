#!/usr/bin/env python3
"""Check generated_at_utc freshness of the generated JSON catalogs in references/.

The `Catalog-backed official` evidence label depends on catalog currency.
Status per catalog: fresh, stale-warn (> --warn-days), stale-fail
(> --fail-days), untracked (no parseable timestamp, e.g. 'source-derived'),
corrupt (unreadable or malformed JSON), or missing. Exit 1 when any catalog
is stale-fail, missing, or corrupt.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from json_file_io import JSONFileError, read_json_file  # noqa: E402

CATALOGS = [
    "o11-designing-screens-widget-catalog.json",
    "odc-data-grid-reference.json",
    "odc-studio-widget-catalog.json",
    "odc-ui-pattern-catalog.json",
    "outsystems-ui-implementation-reference.json",
]

REFRESH_HINTS = {
    "o11-designing-screens-widget-catalog.json": "scripts/refresh_o11_designing_screens_catalog.py",
    "odc-data-grid-reference.json": "scripts/refresh_odc_data_grid_reference.py",
    "odc-studio-widget-catalog.json": "scripts/refresh_odc_studio_widget_catalog.py",
    "odc-ui-pattern-catalog.json": "scripts/refresh_odc_ui_catalog.py",
    "outsystems-ui-implementation-reference.json": "scripts/refresh_outsystems_ui_reference.py",
}


def parse_generated_at(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def classify(age_days, warn_days, fail_days):
    if age_days is None:
        return "untracked"
    if age_days > fail_days:
        return "stale-fail"
    if age_days > warn_days:
        return "stale-warn"
    return "fresh"


def audit(references_dir, warn_days, fail_days, now=None):
    now = now or datetime.now(timezone.utc)
    rows = []
    for name in CATALOGS:
        path = Path(references_dir) / name
        if not path.is_file():
            rows.append({"catalog": name, "age_days": None, "status": "missing",
                         "refresh": REFRESH_HINTS[name]})
            continue
        try:
            data = read_json_file(path)
        except JSONFileError:
            rows.append({"catalog": name, "age_days": None, "status": "corrupt",
                         "refresh": REFRESH_HINTS[name]})
            continue
        generated = parse_generated_at(data.get("generated_at_utc")) if isinstance(data, dict) else None
        age_days = (now - generated).days if generated else None
        rows.append({"catalog": name, "age_days": age_days,
                     "status": classify(age_days, warn_days, fail_days),
                     "refresh": REFRESH_HINTS[name]})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--references-dir",
                        default=Path(__file__).resolve().parents[1] / "references", type=Path)
    parser.add_argument("--warn-days", default=45, type=int)
    parser.add_argument("--fail-days", default=120, type=int)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    rows = audit(args.references_dir, args.warn_days, args.fail_days)
    failing = [r for r in rows if r["status"] in ("stale-fail", "missing", "corrupt")]
    if args.json:
        print(json.dumps({"pass": not failing, "catalogs": rows}, indent=2))
    else:
        for r in rows:
            age = "n/a" if r["age_days"] is None else f"{r['age_days']}d"
            print(f"{r['status']:<11} {age:>5}  {r['catalog']}  (refresh: {r['refresh']})")
    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main())
