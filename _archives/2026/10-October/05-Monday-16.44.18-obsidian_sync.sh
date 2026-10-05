# ---------------------------------------------------------------------------
# Obsidian sync: OneDrive Lab-Notebook  <->  iCloud vault (for iPad editing)
#
#   obs_push [YYYY-MM-DD] [-n]   OneDrive -> iCloud
#   obs_pull [YYYY-MM-DD] [-n]   iCloud   -> OneDrive
#   obs_sync [YYYY-MM-DD] [-n]   pull, then push (two-way, newest file wins)
#
# The daily note (default: today) is synced, plus every markdown link
# listed under its "### to synch" heading. Paths are mirrored relative to
# the Lab-Notebook root, so the relative links keep working in both vaults.
# -n = dry run (show what would be copied).
# Works in bash and zsh.
# ---------------------------------------------------------------------------

OBS_ONEDRIVE="$HOME/OneDrive - ICM/Lab-Notebook"
OBS_ICLOUD="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Perso/Work"
OBS_DAILY_DIR="Daily-Notes"        # relative to the vault roots
OBS_SECTION="to synch"             # heading that holds the list

# Collapse "a/b/../c/./d" -> "a/c/d" (lexical, no filesystem access).
# Prints nothing if the path escapes the root.
_obs_normpath() {
    printf '%s\n' "$1" | awk -F/ '{
        n = 0
        for (i = 1; i <= NF; i++) {
            if ($i == "" || $i == ".") continue
            if ($i == "..") { if (n == 0) exit; n--; continue }
            a[++n] = $i
        }
        s = a[1]; for (i = 2; i <= n; i++) s = s "/" a[i]
        print s
    }'
}

# List vault-relative paths to sync from a daily note (the note itself first).
_obs_list() {
    local note="$1" rel_note="$2" note_dir
    note_dir=$(dirname "$rel_note")
    printf '%s\n' "$rel_note"
    awk -v sec="$OBS_SECTION" '
        /^#+[ \t]/ { if (f) exit; h = $0; sub(/^#+[ \t]+/, "", h); sub(/[ \t]+$/, "", h)
                     if (tolower(h) == tolower(sec)) f = 1; next }
        f' "$note" |
    sed -nE 's/^[[:space:]]*[-*+][[:space:]]+\[[^]]*\]\(<?([^)>]+)>?\).*/\1/p' |
    sed 's/%20/ /g' |
    while IFS= read -r link; do
        _obs_normpath "$note_dir/$link"
    done
}

# _obs_run <src_root> <dst_root> <label> [YYYY-MM-DD] [-n]
_obs_run() {
    local src_root="$1" dst_root="$2" label="$3"; shift 3
    local day dry="" arg note rel_note list rel src dst n=0
    day=$(date +%F)
    for arg in "$@"; do
        case "$arg" in
            -n|--dry-run) dry="-n" ;;
            ????-??-??)   day="$arg" ;;
            *) echo "usage: obs_push|obs_pull|obs_sync [YYYY-MM-DD] [-n]" >&2; return 1 ;;
        esac
    done

    rel_note="$OBS_DAILY_DIR/$day.md"
    # Read the list from the source side's note (it may have been edited there),
    # falling back to the other side.
    if   [ -f "$src_root/$rel_note" ]; then note="$src_root/$rel_note"
    elif [ -f "$dst_root/$rel_note" ]; then note="$dst_root/$rel_note"
    else echo "obs: no daily note $rel_note in either vault" >&2; return 1
    fi

    echo "== $label  ($day)${dry:+  [dry run]}"
    list=$(_obs_list "$note" "$rel_note")

    while IFS= read -r rel; do
        [ -z "$rel" ] && { echo "  ! skipping a link that points outside the vault" >&2; continue; }
        src="$src_root/$rel"; dst="$dst_root/$rel"
        if [ -d "$src" ]; then
            [ -z "$dry" ] && mkdir -p "$dst"
            echo "  [dir]  $rel"
            rsync -auv $dry --exclude='.DS_Store' --exclude='.obsidian' \
                  --exclude='.trash' --exclude='~$*' --exclude='.~lock.*' "$src/" "$dst/" | sed '/^$/d;/^sent /d;/^total /d;/^building /d;/^Transfer starting/d;/^\.\/$/d;s/^/         /'
        elif [ -f "$src" ]; then
            [ -z "$dry" ] && mkdir -p "$(dirname "$dst")"
            echo "  [file] $rel"
            rsync -au $dry "$src" "$dst"
        else
            echo "  ! not found in source: $rel" >&2
            continue
        fi
        n=$((n + 1))
    done <<EOF
$list
EOF
    echo "== $n item(s) processed"
}

obs_push() { _obs_run "$OBS_ONEDRIVE" "$OBS_ICLOUD" "OneDrive -> iCloud" "$@"; }
obs_pull() { _obs_run "$OBS_ICLOUD" "$OBS_ONEDRIVE" "iCloud -> OneDrive" "$@"; }
obs_sync() { obs_pull "$@" && obs_push "$@"; }
