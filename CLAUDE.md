# Instructions for Claude

## Where instructions go

- Keep this file for repo-wide rules. Instructions specific to a submodule go in that submodule's own `CLAUDE.md` (e.g. `utils/spiking_network_dynamics/CLAUDE.md`).

## Git

- "Commit all changes" means already-tracked files only: use `git add -u` (plus submodule pointer updates), never add untracked files. This repo holds many untracked work folders (data, talks, scratch scripts). If untracked files look like they belong in the commit, ask first.

## Figures for the lab notes

- The lab notes (OneDrive-ICM/Lab-Notebook, Obsidian) are read in dark mode: plots with axes/labels destined for them use white annotations on black (matplotlib `dark_background`).
- This applies to plots, not image-strip figures (e.g. `rank-*.png`): don't restyle those unless asked.
