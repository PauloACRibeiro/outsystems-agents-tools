import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import verify_export_integrity as v  # noqa: E402


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_export(root: Path) -> None:
    """A minimal valid generated tree + EXPORT-MANIFEST.json describing it."""
    files = {
        "skills/demo-skill/SKILL.md": "skill body\n",
        "skills/demo-skill/references/foo.md": "reference\n",
    }
    entries = []
    for rel, text in files.items():
        write(root / rel, text)
        entries.append(
            {"path": rel, "sha256": sha256_bytes(text.encode()), "size": len(text.encode())}
        )
    # repo-authored siblings the export must ignore
    write(root / "skills" / "README.md", "# skills\n")
    write(root / "skills" / ".gitkeep", "")
    manifest = {"pack_name": "demo", "version": "2026-07-18", "files": entries}
    write(root / "skills" / "EXPORT-MANIFEST.json", json.dumps(manifest, indent=2))


class VerifyExportIntegrityTests(unittest.TestCase):
    def test_clean_export_reports_no_problems(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            make_export(root)
            self.assertEqual(v.verify(root), [])

    def test_ignores_repo_authored_siblings(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            make_export(root)
            # README/.gitkeep are not in the manifest and must NOT be flagged
            self.assertEqual(v.verify(root), [])

    def test_detects_hand_edited_file(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            make_export(root)
            write(root / "skills" / "demo-skill" / "SKILL.md", "TAMPERED\n")
            problems = v.verify(root)
            self.assertTrue(any("modified" in p and "SKILL.md" in p for p in problems), problems)

    def test_detects_deleted_file(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            make_export(root)
            (root / "skills" / "demo-skill" / "references" / "foo.md").unlink()
            problems = v.verify(root)
            self.assertTrue(any("missing" in p and "foo.md" in p for p in problems), problems)

    def test_detects_untracked_addition_in_managed_subtree(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            make_export(root)
            write(root / "skills" / "demo-skill" / "SNEAKED-IN.md", "not exported\n")
            problems = v.verify(root)
            self.assertTrue(any("untracked" in p and "SNEAKED-IN.md" in p for p in problems), problems)

    def test_missing_manifest_is_a_problem(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            write(root / "skills" / "README.md", "# skills\n")
            problems = v.verify(root)
            self.assertTrue(any("EXPORT-MANIFEST" in p for p in problems), problems)

    def test_main_returns_nonzero_on_tamper(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            make_export(root)
            write(root / "skills" / "demo-skill" / "SKILL.md", "TAMPERED\n")
            self.assertEqual(v.main([str(root)]), 1)

    def test_main_returns_zero_on_clean(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            make_export(root)
            self.assertEqual(v.main([str(root)]), 0)


if __name__ == "__main__":
    unittest.main()
