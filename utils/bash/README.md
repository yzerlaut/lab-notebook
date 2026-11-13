# Shell utilities

| file               | functions / usage                    | runs on        |
|--------------------|--------------------------------------|----------------|
| `files_sync.sh`    | `sync_file`, `sync_folder`: copy files/folders to the same place on another computer (rsync over ssh) | macOS, Linux |
| `notes_sync.sh`    | `notes_sync`, `notes_clean`: Lab-Notebook <-> `private-notes` git repo | macOS, Linux |
| `ipad_sync.sh`     | `sh ipad_sync.sh [-n]`: two-way sync of the Obsidian vault iPad (iSH) <-> `lab-server` | iSH on the iPad |
| `obsidian_sync.sh` | `obs_push`, `obs_pull`, `obs_sync`, `obs_clean`: Lab-Notebook <-> iCloud vault | macOS only (needs iCloud Drive) |
| `update_ip.sh`     | `update_ip`: static IP on the iPad hotspot, DHCP elsewhere | macOS, Linux (NetworkManager) |

The functions are loaded from the shell config (`~/.zshrc` on macOS, `~/.bashrc` on Linux):
```
LN=~/path/to/lab-notebook     # where this repo is cloned
for f in "$LN"/utils/bash/{files,notes,obsidian}_sync.sh "$LN"/utils/bash/update_ip.sh; do
    source "$f"
done
```

## Linux workstation (`lab-server`, user `yann`)

There is no OneDrive app on Linux: the Lab-Notebook is the local copy
`~/Documents/Lab-Notebook`, kept in sync with OneDrive by rclone
(see [../onedrive/README.md](../onedrive/README.md)). `notes_sync.sh` and
`obsidian_sync.sh` use `~/OneDrive - ICM/Lab-Notebook` when it exists (MacBook),
`~/Documents/Lab-Notebook` otherwise (all paths can be overridden: `NOTES_SRC`,
`NOTES_REPO`, `OBS_ONEDRIVE`, `OBS_ICLOUD`).

Once:
1. `sudo apt install rclone rsync`, then `rclone config` (see the OneDrive README)
   and `python utils/onedrive/sync.py --pull` to get the Lab-Notebook.
2. Clone the `private-notes` repo into `~/Documents/Research/private-notes` (for `notes_sync`).
3. Copy the Obsidian vault from the MacBook, keeping the file dates (the iPad sync
   state relies on them):
   `cd ~/Documents/Notebook && sync_folder yann@lab-server` (on the MacBook).
4. On the iPad (iSH): add `lab-server` to `~/.ssh/config` (`HostName` = the
   workstation's address, `User yann`), copy the iSH public key to
   `~/.ssh/authorized_keys` on the workstation, then run `sh ipad_sync.sh -n`
   first to check the plan. The default host is now `yann@lab-server`; the
   MacBook remains usable with `SERVER=yann@macbook sh ipad_sync.sh`.
   The iPad must be able to reach the workstation (lab network or VPN).

Daily use on the workstation:
```
python utils/onedrive/sync.py --pull   # get the OneDrive changes
notes_sync                              # daily note <-> private-notes / GitHub
python utils/onedrive/sync.py          # send the changes back to OneDrive
```
