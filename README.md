# Laboratory Notebook

## Setup (with `uv`)

A Python 3.14 environment in `.venv/` at the root of the repository, defined by
`pyproject.toml` (+ `.python-version`, `uv.lock`), with `physion` installed in editable mode
(changes in `physion/src` apply without reinstalling), plus `ipykernel` and `pytest`.

1. Install `uv` (once per machine):
    ```
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
    (or `brew install uv`)

2. Get the repository with its submodules (`physion`, `utils/...`):
    ```
    git clone --recurse-submodules https://github.com/yzerlaut/lab-notebook
    cd lab-notebook
    ```
    (in an existing clone: `git submodule update --init --recursive`)

3. Create/update the environment (`uv` downloads Python 3.14 if needed):
    ```
    uv sync
    ```
    with optional dependencies of `physion` as needed: `uv sync --extra ephys`
    (extras: `ephys`, `acquisition`, `diffusion`; `--all-extras` for all of them).
    Re-run `uv sync` after a change of `pyproject.toml` or of the `physion` dependencies.

4. Use it, either without activating it (from the repository folders):
    ```
    uv run python my-script.py
    ```
    or by activating it:
    ```
    source .venv/bin/activate
    python my-script.py
    ```
    [!!] from inside a submodule with its own `pyproject.toml` (`physion/`,
    `statemod-network/`, `utils/spiking_network_dynamics/`), `uv run` uses that
    submodule's own environment (`<submodule>/.venv`), not the root one.

5. VS Code (with the repository root as workspace folder): `.venv/bin/python` is the
    default interpreter, set in `.vscode/settings.json` (tracked in git):
    ```json
    {
        "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
        "python.terminal.activateEnvironment": true
    }
    ```
    - if not picked up: Cmd+Shift+P -> "Python: Select Interpreter" -> `.venv/bin/python`
    - in the Interactive Window or a notebook: kernel picker (top right)
        -> "Python Environments" -> `.venv`

To check the installation:
```
uv run python -c "import physion; print(physion.__file__)"
```
(should print a path in `physion/src/physion/`)

## Usage

### 1) Archive

```
uv run utils/archive.py the-script-you-want-to-back-up
```

This will:
- duplicate the file with a timestamp 
    (e.g.  `archive/2025-10-06-18:54:11-the-script-you-want-to-back-up`)
- perform a `git add` and `git commit` to this repository 

It also works with a whole folder of scripts:

```
uv run utils/archive.py Medicine-Programming-Projects/
```

The folder is copied (without `__pycache__` or `.ipynb_checkpoints`) as
`_archives/2025/10-October/07-Tuesday-09.09.59-Medicine-Programming-Projects/`
and all its files are committed together.


### 2) Recover

Find the file you're looking for with `tree`:

```
tree _archives/
```

This outputs the lab notebook as a tree structure:

```
_archives
└── 2025
    └── October
        ├── 07-Tuesday-09:09:59-fix-running-speed-calibration-in-data.py
        ├── 09-Thursday-19:39:22-anr-SST-vs-NDNF.py
        ├── 09-Thursday-19:39:55-fix-running-speed-calibration-in-data.py
        ├── 12-Sunday-18:30:21-anr-Toy-Ntwk.py
        ├── 13-Monday-13:16:11-Analysis-PhotoStim-Contamination.py
        └── 13-Monday-13:16:34-anr-Toy-Ntwk.py
```

You can recover the file you want with:
```
python archive.py _archives/2025/October/09-Thursday-19:39:22-anr-SST-vs-NDNF.py
```

and an archived folder the same way (it is copied back as `./Medicine-Programming-Projects/`):
```
python archive.py _archives/2025/10-October/07-Tuesday-09.09.59-Medicine-Programming-Projects/
```

### 3) OneDrive

`utils/onedrive/` has scripts to sync the local `~/Documents/Lab-Notebook` to the
`Lab-Notebook` folder on OneDrive and to delete folders there, without the OneDrive
app (via [rclone](https://rclone.org)):
```
python utils/onedrive/sync.py -n                   # dry run, then without -n
python utils/onedrive/delete.py Projects/old-stuff
```
See [utils/onedrive/README.md](utils/onedrive/README.md) for the setup and all options.

### 4) iPad (Obsidian vault)

`utils/bash/ipad_sync.sh` is a two-way sync of the Obsidian vault between the iPad (run in
[iSH](https://ish.app)) and a remote: the first reachable of `macbook`, then `lab-server`
(ssh aliases in the iSH `~/.ssh/config`). Mount the vault in iSH first
(`mount -t ios . /mnt/Notebook`, pick the vault folder), then:
```
sh ipad_sync.sh -n              # dry run: show the plan only
sh ipad_sync.sh                 # two-way sync
sh ipad_sync.sh --force-pull    # the remote is right: make the iPad identical to it
sh ipad_sync.sh --force-push    # the iPad is right: make the remote identical to it
sh ipad_sync.sh -y              # no confirmation question
REMOTE=yann@lab-server sh ipad_sync.sh     # force the remote host
```
- In a two-way sync, each file goes from the side where it changed (vs. the last sync) to the
  other; on a conflict, the most recent version wins.
- Removed or overwritten files are never deleted: they go to `<vault>/.sync-trash/<date>/` on
  their side.
- When more than 20 files would change (`MAX_CHANGES=20`), the plan is shown and a yes/no
  confirmation is asked. This catches a vault that is not (or wrongly) mounted after a
  re-mount, which would otherwise look like "all files deleted on the iPad". In that case
  answer no, fix the mount, and if needed restore with `--force-pull`.
- Other settings (environment variables): `REMOTE_VAULT` (default `Documents/Notebook`, in the
  remote's `~`), `IPAD_VAULT` (default `/mnt/Notebook`), `HOSTS`. See the header of the script.
