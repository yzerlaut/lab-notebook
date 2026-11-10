#!/usr/bin/env python3
"""
OneDrive sync: ~/Documents/Lab-Notebook  ->  OneDrive Lab-Notebook (via rclone)

    python sync.py                  sync every subfolder
    python sync.py Grants Projects  sync only these subfolders
    python sync.py -n               dry run (show what would be done)

Each subfolder of ~/Documents/Lab-Notebook is mirrored to the folder of the
same name in "Lab-Notebook" on OneDrive, without the OneDrive app:
  - one-way (here -> OneDrive); a file that is newer on OneDrive is never
    overwritten (rclone --update)
  - files deleted here are removed from OneDrive, but moved to
    OneDrive:Lab-Notebook/.sync-trash/<date_time>/<subfolder>/
  - hidden folders (.obsidian, .git, ...) and files at the top level of the
    Lab-Notebook are not synced; git material and system files are skipped
    everywhere

Other locations: --src, --remote, --dest (see common.py for the defaults).
"""

import argparse
import datetime
import subprocess
from pathlib import Path

from common import (SRC, TRASH, TIMESTAMP_FORMAT, add_common_args,
                    check_rclone, fail, remote_root)

SCRIPT = "onedrive sync"

EXCLUDES = [
    ".git/**", ".gitignore", ".gitmodules", ".github/**",
    ".DS_Store", "._*", "Thumbs.db", "desktop.ini",
    "__pycache__/**", ".ipynb_checkpoints/**", "~$*",
]


def subfolders(src, names):
    """The subfolders to sync: the given names, or all non-hidden ones."""
    if not src.is_dir():
        fail(SCRIPT, f"no folder {src}")
    if names:
        missing = [n for n in names if not (src / n).is_dir()]
        if missing:
            fail(SCRIPT, f"not subfolders of {src}: {', '.join(missing)}")
        return [src / n for n in names]
    return sorted(p for p in src.iterdir()
                  if p.is_dir() and not p.name.startswith("."))


def sync_folder(folder, root, stamp, dry_run):
    """Mirror one local folder to <root>/<name>. Returns True on success."""
    print(f"\n=== {folder.name}  ->  {root}/{folder.name}", flush=True)
    cmd = ["rclone", "sync", str(folder), f"{root}/{folder.name}",
           "--update",
           "--backup-dir", f"{root}/{TRASH}/{stamp}/{folder.name}",
           "--create-empty-src-dirs",
           "--stats-one-line", "--stats", "0",
           "-v"]
    for pattern in EXCLUDES:
        cmd += ["--exclude", pattern]
    if dry_run:
        cmd.append("--dry-run")
    return subprocess.run(cmd).returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description="Mirror the subfolders of the local Lab-Notebook to OneDrive.")
    parser.add_argument("folders", nargs="*",
                        help="subfolders to sync (default: all)")
    parser.add_argument("--src", type=Path, default=SRC,
                        help=f"local Lab-Notebook (default: {SRC})")
    add_common_args(parser)
    args = parser.parse_args()

    check_rclone(SCRIPT, args.remote)
    folders = subfolders(args.src.expanduser(), args.folders)
    stamp = datetime.datetime.now().strftime(TIMESTAMP_FORMAT)
    root = remote_root(args.remote, args.dest)

    failed = [f.name for f in folders
              if not sync_folder(f, root, stamp, args.dry_run)]

    print()
    if failed:
        fail(SCRIPT, f"failed for {', '.join(failed)}")
    label = "dry run done" if args.dry_run else "done"
    print(f"{SCRIPT}: {label} ({len(folders)} folder(s))")


if __name__ == "__main__":
    main()
