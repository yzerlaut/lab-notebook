"""
Shared settings and helpers for the OneDrive scripts (sync.py, delete.py).

All the scripts go through rclone (https://rclone.org/install/) with a
OneDrive remote, set up once with:
    rclone config   (n -> name "onedrive" -> Microsoft OneDrive)
"""

import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath

SRC = Path.home() / "Documents" / "Lab-Notebook"
REMOTE = "onedrive"                  # rclone remote name
DEST = "Lab-Notebook"                # folder on the OneDrive side
TRASH = ".sync-trash"                # in DEST, for removed files and folders

TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"


def fail(script, message):
    sys.exit(f"{script}: {message}")


def check_rclone(script, remote):
    """Exit with a hint if rclone or the remote is missing."""
    if shutil.which("rclone") is None:
        fail(script, "rclone not found, see https://rclone.org/install/")
    remotes = subprocess.run(["rclone", "listremotes"], capture_output=True,
                             text=True).stdout.split()
    if f"{remote}:" not in remotes:
        fail(script, f"no rclone remote named '{remote}' "
                     f"(found: {' '.join(remotes) or 'none'}), run: rclone config")


def remote_root(remote, dest):
    """'onedrive:Lab-Notebook'"""
    return f"{remote}:{dest}"


def clean_relpath(path):
    """
    Normalise a path relative to the OneDrive Lab-Notebook ('a/./b/' -> 'a/b').
    Returns None for an empty path or one that leaves the Lab-Notebook.
    """
    parts = []
    for part in PurePosixPath(path.replace("\\", "/")).parts:
        if part in ("", ".", "/"):
            continue
        if part == "..":
            if not parts:
                return None
            parts.pop()
            continue
        parts.append(part)
    return "/".join(parts) or None


def add_common_args(parser):
    parser.add_argument("-n", "--dry-run", action="store_true",
                        help="show what would be done")
    parser.add_argument("--remote", default=REMOTE,
                        help=f"rclone remote name (default: {REMOTE})")
    parser.add_argument("--dest", default=DEST,
                        help=f"folder on OneDrive (default: {DEST})")
