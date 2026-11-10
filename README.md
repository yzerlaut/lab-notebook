# Laboratory Notebook

## Setup (with `uv`)

A Python 3.14 environment in `.venv/` at the root of the repository, with `physion` installed in editable mode (changes in `physion/src` apply without reinstalling).

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

3. Create the environment (`uv` downloads Python 3.14 if needed):
    ```
    uv venv --python 3.14
    ```

4. Install `physion` in editable mode:
    ```
    uv pip install -e ./physion
    ```
    with the optional dependencies of `physion/pyproject.toml` as needed, e.g.:
    ```
    uv pip install -e "./physion[ephys,test]"
    ```
    (extras: `ephys`, `acquisition`, `diffusion`, `test`)

5. Use it, either by activating the environment:
    ```
    source .venv/bin/activate
    python my-script.py
    ```
    or without activating it, from the repository folders:
    ```
    uv run python my-script.py
    ```
    [!!] not from inside `physion/`: there `uv run` finds `physion/pyproject.toml` and
    creates a separate `physion/.venv` (activate the environment instead)
6. VS Code (with the repository root as workspace folder):
    - the Interactive Window and notebooks need `ipykernel` in the environment:
        ```
        uv pip install ipykernel
        ```
    - Cmd+Shift+P -> "Python: Select Interpreter" -> `.venv/bin/python`
        (if not listed: "Enter interpreter path..." -> `./.venv/bin/python`)
    - in the Interactive Window or a notebook: kernel picker (top right)
        -> "Python Environments" -> `.venv`
    - default of the workspace, already set in `.vscode/settings.json` (tracked in git):
        ```json
        {
            "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
            "python.terminal.activateEnvironment": true
        }
        ```
        (the second line activates `.venv` in each new VS Code terminal)
    - check, in a cell: `import sys; print(sys.executable)` -> `.../lab-notebook/.venv/bin/python`

To check the installation:
```
uv run python -c "import physion; print(physion.__file__)"
```
(should print a path in `physion/src/physion/`)

## Usage

### 1) Archive

```
python tools/archive.py the-script-you-want-to-back-up
```

This will:
- duplicate the file with a timestamp 
    (e.g.  `archive/2025-10-06-18:54:11-the-script-you-want-to-back-up`)
- perform a `git add` and `git commit` to this repository 

It also works with a whole folder of scripts:

```
python archive.py Medicine-Programming-Projects/
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

### 3) Sync to OneDrive

`utils/bash/onedrive_sync.py` mirrors each subfolder of `~/Documents/Lab-Notebook`
to the folder of the same name in `Lab-Notebook` on OneDrive, without the OneDrive
app (it uses [rclone](https://rclone.org)).

Setup (once per machine):
```
brew install rclone        # or: sudo apt install rclone / winget install Rclone.Rclone
rclone config              # n -> name "onedrive" -> Microsoft OneDrive -> log in
                           #   -> OneDrive Business (ICM account)
```

Usage:
```
python utils/bash/onedrive_sync.py -n               # dry run (show what would be done)
python utils/bash/onedrive_sync.py                  # sync every subfolder
python utils/bash/onedrive_sync.py Grants Projects  # sync only these subfolders
```

- one-way (here -> OneDrive): a file that is newer on OneDrive is never overwritten
- files deleted here are removed from OneDrive, but moved to
  `Lab-Notebook/.sync-trash/<date_time>/<subfolder>/` on OneDrive
- not synced: hidden folders (`.obsidian`, `.git`, ...) and files at the top level of
  the Lab-Notebook; git material and system files (`.DS_Store`, ...) are skipped everywhere
- other locations: `--src <local folder>`, `--remote <rclone remote>`, `--dest <OneDrive folder>`

If the login in `rclone config` asks for admin approval, the institution blocks rclone
for this account: ask IT to allow it.
