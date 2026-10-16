# ---------------------------------------------------------------------------
# Obsidian sync: OneDrive Lab-Notebook  <->  iCloud vault (for iPad editing)
#
#   obs_push [YYYY-MM-DD] [-n]   OneDrive -> iCloud
#   obs_pull [YYYY-MM-DD] [-n]   iCloud   -> OneDrive
#   obs_sync [YYYY-MM-DD] [-n]   pull, then push (two-way, newest file wins)
#   obs_clean [YYYY-MM-DD] [-n]  in iCloud Work/, move to the Trash the daily
#                                notes of previous days and the folders not
#                                listed in the current daily note
#
# The daily note (default: today) is synced, plus every markdown link
# listed under its "### to synch" heading. On the iCloud side, everything
# goes flat into the Work folder under its own name, e.g.
#   Grants/2027-ANR-CodeReconf  <->  Work/2027-ANR-CodeReconf
#   Daily-Notes/2026-10-05.md   <->  Work/2026-10-05.md
# -n = dry run (show what would be copied).
# Works in bash and zsh.
# ---------------------------------------------------------------------------

OBS_ONEDRIVE="$HOME/OneDrive - ICM/Lab-Notebook"
OBS_ICLOUD="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Perso/Work"
OBS_DAILY_DIR="Daily-Notes"        # relative to the OneDrive root
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

# List OneDrive-relative paths to sync from a daily note (the note itself first).
# Links in the note are relative to the OneDrive daily-notes folder.
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

# _obs_run <push|pull> <label> [YYYY-MM-DD] [-n]
_obs_run() {
    local dir="$1" label="$2"; shift 2
    local day dry="" arg note rel_note list rel od ic src dst n=0
    day=$(date +%F)
    for arg in "$@"; do
        case "$arg" in
            -n|--dry-run) dry="-n" ;;
            ????-??-??)   day="$arg" ;;
            *) echo "usage: obs_push|obs_pull|obs_sync [YYYY-MM-DD] [-n]" >&2; return 1 ;;
        esac
    done

    rel_note="$OBS_DAILY_DIR/$day.md"
    od="$OBS_ONEDRIVE/$rel_note"
    ic="$OBS_ICLOUD/$day.md"
    # Read the list from the source side's note (it may have been edited there),
    # falling back to the other side.
    if [ "$dir" = push ]; then src="$od"; dst="$ic"; else src="$ic"; dst="$od"; fi
    if   [ -f "$src" ]; then note="$src"
    elif [ -f "$dst" ]; then note="$dst"
    else echo "obs: no daily note for $day in either vault" >&2; return 1
    fi

    echo "== $label  ($day)${dry:+  [dry run]}"
    list=$(_obs_list "$note" "$rel_note")

    while IFS= read -r rel; do
        [ -z "$rel" ] && { echo "  ! skipping a link that points outside the vault" >&2; continue; }
        od="$OBS_ONEDRIVE/$rel"
        ic="$OBS_ICLOUD/$(basename "$rel")"
        if [ "$dir" = push ]; then src="$od"; dst="$ic"; else src="$ic"; dst="$od"; fi
        if [ -d "$src" ]; then
            [ -z "$dry" ] && mkdir -p "$dst"
            echo "  [dir]  $rel  <->  Work/$(basename "$rel")"
            rsync -auv $dry --exclude='.DS_Store' --exclude='.obsidian' \
                  --exclude='.trash' --exclude='~$*' --exclude='.~lock.*' "$src/" "$dst/" | sed '/^$/d;/^sent /d;/^total /d;/^building /d;/^Transfer starting/d;/^\.\/$/d;s/^/         /'
        elif [ -f "$src" ]; then
            [ -z "$dry" ] && mkdir -p "$(dirname "$dst")"
            echo "  [file] $rel  <->  Work/$(basename "$rel")"
            rsync -au $dry "$src" "$dst"
        else
            echo "  ! not found: $src" >&2
            continue
        fi
        n=$((n + 1))
    done <<EOF
$list
EOF
    echo "== $n item(s) processed"
}

obs_push() { _obs_run push "OneDrive -> iCloud" "$@"; }
obs_pull() { _obs_run pull "iCloud -> OneDrive" "$@"; }
obs_sync() { obs_pull "$@" && obs_push "$@"; }

# Clean iCloud Work/: old daily notes + folders not in the current daily note.
# Items are moved to the Trash after confirmation. An old daily note edited on
# the iPad and not yet pulled back to OneDrive is kept.
obs_clean() {
    local day dry="" arg note keep list entry name od ans dest n=0
    day=$(date +%F)
    for arg in "$@"; do
        case "$arg" in
            -n|--dry-run) dry=1 ;;
            ????-??-??)   day="$arg" ;;
            *) echo "usage: obs_clean [YYYY-MM-DD] [-n]" >&2; return 1 ;;
        esac
    done

    if   [ -f "$OBS_ICLOUD/$day.md" ]; then note="$OBS_ICLOUD/$day.md"
    elif [ -f "$OBS_ONEDRIVE/$OBS_DAILY_DIR/$day.md" ]; then note="$OBS_ONEDRIVE/$OBS_DAILY_DIR/$day.md"
    else echo "obs: no daily note for $day in either vault, nothing cleaned" >&2; return 1
    fi

    # names (in Work/) of the items listed in the current daily note
    keep=$(_obs_list "$note" "$OBS_DAILY_DIR/$day.md" |
           while IFS= read -r entry; do [ -n "$entry" ] && basename "$entry"; done)

    list=$(find "$OBS_ICLOUD" -mindepth 1 -maxdepth 1 ! -name '.*' | sort |
        while IFS= read -r entry; do
            name=$(basename "$entry")
            printf '%s\n' "$keep" | grep -qxF -- "$name" && continue
            if [ -d "$entry" ]; then
                printf '%s\n' "$name"
            elif printf '%s\n' "$name" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}\.md$' &&
                 [[ "${name%.md}" < "$day" ]]; then
                od="$OBS_ONEDRIVE/$OBS_DAILY_DIR/$name"
                if [ ! -f "$od" ] || [ "$entry" -nt "$od" ]; then
                    echo "  ! keeping $name: edits not pulled to OneDrive (run: obs_pull ${name%.md})" >&2
                    continue
                fi
                printf '%s\n' "$name"
            fi
        done)

    if [ -z "$list" ]; then echo "== nothing to clean in Work/"; return 0; fi
    echo "== to move to the Trash (keeping items of $day):"
    printf '%s\n' "$list" | sed 's/^/     Work\//'
    [ -n "$dry" ] && { echo "== dry run, nothing moved"; return 0; }

    printf 'Proceed? [y/N] '
    read -r ans
    case "$ans" in y|Y|yes) ;; *) echo "== aborted"; return 1 ;; esac

    while IFS= read -r name; do
        dest="$HOME/.Trash/$name"
        [ -e "$dest" ] && dest="$HOME/.Trash/${name%.md} $(date +%H.%M.%S)${name##"${name%.md}"}"
        mv "$OBS_ICLOUD/$name" "$dest" && n=$((n + 1))
    done <<EOF
$list
EOF
    echo "== $n item(s) moved to the Trash"
}
