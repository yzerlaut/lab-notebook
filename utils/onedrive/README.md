# OneDrive scripts

Scripts to manage the `Lab-Notebook` folder on OneDrive
without the OneDrive app (they use [rclone](https://rclone.org)):

| script      | what it does                                                        |
|-------------|---------------------------------------------------------------------|
| `sync.py`   | mirror the subfolders of `~/Documents/Lab-Notebook` to OneDrive     |
| `delete.py` | delete folder(s) on OneDrive (to a trash folder by default)         |
| `common.py` | shared settings (local folder, rclone remote, OneDrive folder) and helpers |

Setup (once per machine):
```
brew install rclone        # or: sudo apt install rclone / winget install Rclone.Rclone
rclone config              # n -> name "onedrive" -> Microsoft OneDrive -> log in
                           #   -> OneDrive Business (ICM account)
```
If the login asks for admin approval, the institution blocks rclone for this
account: ask IT to allow it.

## Sync

```
python utils/onedrive/sync.py -n               # dry run (show what would be done)
python utils/onedrive/sync.py                  # sync every subfolder
python utils/onedrive/sync.py Grants Projects  # sync only these subfolders
```

- each subfolder of `~/Documents/Lab-Notebook` goes to the folder of the same name in
  `Lab-Notebook` on OneDrive
- one-way (here -> OneDrive): a file that is newer on OneDrive is never overwritten
- files deleted here are removed from OneDrive, but moved to
  `Lab-Notebook/.sync-trash/<date_time>/<subfolder>/` on OneDrive
- not synced: hidden folders (`.obsidian`, `.git`, ...) and files at the top level of
  the Lab-Notebook; git material and system files (`.DS_Store`, ...) are skipped everywhere

## Delete

Paths are relative to `Lab-Notebook` on OneDrive:
```
python utils/onedrive/delete.py Projects/old-analysis -n    # dry run
python utils/onedrive/delete.py Projects/old-analysis       # move to the trash folder
python utils/onedrive/delete.py Talks/2024 Talks/2025 -y    # several, no confirmation
python utils/onedrive/delete.py .sync-trash --permanent     # empty the trash folder
```

- shows the size of each folder and asks for confirmation first (`-y` to skip)
- by default the folder is moved to `Lab-Notebook/.sync-trash/<date_time>/<path>/`;
  with `--permanent` it is purged (it then only remains in the OneDrive recycle bin)
- only acts on OneDrive: also delete the local folder, or the next `sync.py` uploads it again

Both scripts accept `--remote <rclone remote>` and `--dest <OneDrive folder>`, and
`sync.py` also `--src <local folder>`; the defaults are set in `common.py`.
