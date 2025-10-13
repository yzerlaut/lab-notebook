# Laboratory Notebook

## Usage

### 1) Archive

```
python tools/archive.py the-script-you-want-to-back-up
```

This will:
- duplicate the file with a timestamp 
    (e.g.  `archive/2025-10-06-18:54:11-the-script-you-want-to-back-up`)
- perform a `git add` and `git commit` to this repository 


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