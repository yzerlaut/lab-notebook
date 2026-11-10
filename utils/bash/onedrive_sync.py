#!/usr/bin/env python3
"""
OneDrive sync: ~/Documents/Lab-Notebook  ->  OneDrive Lab-Notebook (via rclone)

    python onedrive_sync.py                  sync every subfolder
    python onedrive_sync.py Grants Projects  sync only these subfolders
    python onedrive_sync.py -n               dry run (show what would be done)

Each subfolder of ~/Documents/Lab-Notebook is mirrored to the folder of the
same name in "Lab-Notebook" on OneDrive, without the OneDrive app:
  - one-way (here -> OneDrive); a file that is newer on OneDrive is never
    overwritten (rclone --update) and is listed as skipped
  - files deleted here are removed from OneDrive, but moved to
    OneDrive:Lab-Notebook/.sync-trash/<date_time>/<subfolder>/
  - hidden folders (.obsidian, .git, ...) and files at the top level of the
    Lab-Notebook are not synced; git material and system files are skipped
    everywhere

Needs rclone (https://rclone.org/install/) with a OneDrive remote, set up
once with:  rclone config   (n -> name "onedrive" -> Microsoft OneDrive)
Another remote name or path can be given with --remote / --dest / --src.
"""

import argparse
import datetime
import shutil
import subprocess
import sys
from pathlib import Path

SRC = Path.home() / "Documents" / "Lab-Notebook"
REMOTE = "onedrive"                  # rclone remote name
DEST = "Lab-Notebook"                # folder on the OneDrive side
TRASH = ".sync-trash"                # in DEST, for files deleted locally

EXCLUDES = [
    ".git/**", ".gitignore", ".gitmodules", ".github/**",
    ".DS_Store", "._*", "Thumbs.db", "desktop.ini",
    "__pycache__/**", ".ipynb_checkpoints/**", "~$*",
]


def check_rclone(remote):
    if shutil.which("rclone") is None:
        sys.exit("onedrive_sync: rclone not found, see https://rclone.org/install/")
    remotes = subprocess.run(["rclone", "listremotes"], capture_output=True,
                             text=True).stdout.split()
    if f"{remote}:" not in remotes:
        sys.exit(f"onedrive_sync: no rclone remote named '{remote}' "
                 f"(found: {' '.join(remotes) or 'none'}), run: rclone config")


def subfolders(src, names):
    if not src.is_dir():
        sys.exit(f"onedrive_sync: no folder {src}")
    if names:
        missing = [n for n in names if not (src / n).is_dir()]
        if missing:
            sys.exit(f"onedrive_sync: not subfolders of {src}: {', '.join(missing)}")
        return [src / n for n in names]
    return sorted(p for p in src.iterdir()
                  if p.is_dir() and not p.name.startswith("."))


def main():
    parser = argparse.ArgumentParser(
        description="Mirror the subfolders of the local Lab-Notebook to OneDrive.")
    parser.add_argument("folders", nargs="*",
                        help="subfolders to sync (default: all)")
    parser.add_argument("-n", "--dry-run", action="store_true",
                        help="show what would be done")
    parser.add_argument("--src", type=Path, default=SRC,
                        help=f"local Lab-Notebook (default: {SRC})")
    parser.add_argument("--remote", default=REMOTE,
                        help=f"rclone remote name (default: {REMOTE})")
    parser.add_argument("--dest", default=DEST,
                        help=f"folder on OneDrive (default: {DEST})")
    args = parser.parse_args()

    check_rclone(args.remote)
    folders = subfolders(args.src.expanduser(), args.folders)
    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    root = f"{args.remote}:{args.dest}"

    failed = []
    for folder in folders:
        print(f"\n=== {folder.name}  ->  {root}/{folder.name}", flush=True)
        cmd = ["rclone", "sync", str(folder), f"{root}/{folder.name}",
               "--update",
               "--backup-dir", f"{root}/{TRASH}/{stamp}/{folder.name}",
               "--create-empty-src-dirs",
               "--stats-one-line", "--stats", "0",
               "-v"]
        for pattern in EXCLUDES:
            cmd += ["--exclude", pattern]
        if args.dry_run:
            cmd.append("--dry-run")
        if subprocess.run(cmd).returncode != 0:
            failed.append(folder.name)

    print()
    if failed:
        sys.exit(f"onedrive_sync: failed for {', '.join(failed)}")
    label = "dry run done" if args.dry_run else "done"
    print(f"onedrive_sync: {label} ({len(folders)} folder(s))")


if __name__ == "__main__":
    main()
