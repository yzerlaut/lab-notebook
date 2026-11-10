#!/usr/bin/env python3
"""
OneDrive delete: remove folder(s) from the OneDrive Lab-Notebook (via rclone)

    python delete.py Projects/old-analysis     move it to the OneDrive trash folder
    python delete.py Talks/2024 Talks/2025     several folders at once
    python delete.py Projects/old -n           dry run (show what would be done)
    python delete.py Projects/old -y           no confirmation prompt
    python delete.py .sync-trash --permanent   empty the trash folder

Paths are relative to "Lab-Notebook" on OneDrive. By default, a folder is not
erased but moved to OneDrive:Lab-Notebook/.sync-trash/<date_time>/<path>/,
the same place where sync.py puts the files deleted locally. With
--permanent it is purged (it then only remains in the OneDrive recycle bin,
for the retention time set by the institution).

Only removes things on OneDrive: the local ~/Documents/Lab-Notebook is not
touched, so delete the folder there too, or the next sync.py will upload it
again.
"""

import argparse
import datetime
import json
import subprocess

from common import (TRASH, TIMESTAMP_FORMAT, add_common_args, check_rclone,
                    clean_relpath, fail, remote_root)

SCRIPT = "onedrive delete"


def folder_size(path):
    """(number of files, bytes) of a remote folder, or None if it is missing."""
    res = subprocess.run(["rclone", "size", "--json", path],
                         capture_output=True, text=True)
    if res.returncode != 0:
        return None
    info = json.loads(res.stdout)
    return info["count"], info["bytes"]


def human(nbytes):
    for unit in ("B", "kB", "MB", "GB"):
        if nbytes < 1000:
            return f"{nbytes:.0f} {unit}" if unit == "B" else f"{nbytes:.1f} {unit}"
        nbytes /= 1000
    return f"{nbytes:.1f} TB"


def confirm(question):
    try:
        return input(f"{question} [y/N] ").strip().lower() in ("y", "yes")
    except EOFError:
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Delete folder(s) from the OneDrive Lab-Notebook.")
    parser.add_argument("folders", nargs="+",
                        help="folder(s) to delete, relative to the OneDrive Lab-Notebook")
    parser.add_argument("--permanent", action="store_true",
                        help="purge instead of moving to the trash folder")
    parser.add_argument("-y", "--yes", action="store_true",
                        help="do not ask for confirmation")
    add_common_args(parser)
    args = parser.parse_args()

    # validate the paths before touching anything
    paths = []
    for folder in args.folders:
        rel = clean_relpath(folder)
        if rel is None:
            fail(SCRIPT, f"'{folder}' is not a folder inside {args.dest} "
                         "(the whole Lab-Notebook cannot be deleted)")
        in_trash = rel == TRASH or rel.startswith(TRASH + "/")
        if in_trash and not args.permanent:
            fail(SCRIPT, f"'{rel}' is in the trash folder, use --permanent")
        paths.append(rel)

    check_rclone(SCRIPT, args.remote)
    root = remote_root(args.remote, args.dest)
    stamp = datetime.datetime.now().strftime(TIMESTAMP_FORMAT)

    # check that they exist and show what will go
    found = []
    for rel in paths:
        size = folder_size(f"{root}/{rel}")
        if size is None:
            print(f"  ! not found on OneDrive: {root}/{rel}")
            continue
        print(f"  {root}/{rel}  ({size[0]} files, {human(size[1])})")
        found.append(rel)
    if not found:
        fail(SCRIPT, "nothing to delete")

    action = ("PERMANENTLY delete" if args.permanent
              else f"move to {args.dest}/{TRASH}/{stamp}/")
    if not (args.dry_run or args.yes or confirm(f"{action} the folder(s) above?")):
        fail(SCRIPT, "cancelled")

    failed = []
    for rel in found:
        src = f"{root}/{rel}"
        if args.permanent:
            cmd = ["rclone", "purge", src]
        else:
            cmd = ["rclone", "move", src, f"{root}/{TRASH}/{stamp}/{rel}",
                   "--delete-empty-src-dirs", "--create-empty-src-dirs"]
        if args.dry_run:
            cmd.append("--dry-run")
        print(f"\n=== {rel}", flush=True)
        ok = subprocess.run(cmd + ["-v", "--stats", "0"]).returncode == 0
        if (ok and not args.permanent and not args.dry_run
                and folder_size(src) is not None):
            # 'move' may leave the (now empty) top folder behind
            ok = subprocess.run(["rclone", "rmdirs", src]).returncode == 0
        if not ok:
            failed.append(rel)

    print()
    if failed:
        fail(SCRIPT, f"failed for {', '.join(failed)}")
    label = "dry run done" if args.dry_run else "done"
    print(f"{SCRIPT}: {label} ({len(found)} folder(s))")


if __name__ == "__main__":
    main()
