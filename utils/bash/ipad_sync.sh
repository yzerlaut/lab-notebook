#!/bin/sh
# ---------------------------------------------------------------------------
# Two-way sync of the Obsidian vault: iPad (iSH)  <->  laptop, without rsync
#
#   sh ipad_sync.sh [-n]        (run in iSH; -n = dry run, show the plan only)
#
# How it works (rsync hangs on iSH, so only find/stat/awk/tar/ssh are used):
#   1. list (mtime, size) of the vault files on both sides (1 ssh call)
#   2. compare with the state saved at the end of the previous sync, to tell
#      which side changed, created or deleted each file
#   3. move deleted / conflict-losing files to .sync-trash/<date>/ (in the
#      vault, on the side where they are removed; Obsidian ignores dot folders)
#   4. transfer in one tar stream per direction (2 ssh calls)
#   5. re-list both sides and save the new state
#
# Rules, per file:
#   changed on one side only          -> copied to the other side
#   new on one side                   -> copied to the other side
#   deleted on one side, unchanged on
#   the other                         -> deleted there too (moved to the trash)
#   deleted on one side, modified on
#   the other                         -> the modified one is restored
#   changed on both sides (conflict)  -> the most recent wins, the other copy
#                                        goes to the trash
#   first sync (no state): a file present on both sides with the same size is
#   considered identical, otherwise treated as a conflict.
#
# Needs in iSH: openssh-client (ssh keys to the laptop), and a tar supporting
# -T (busybox tar does; otherwise `apk add tar`). The vault must be mounted:
#   mount -t ios . /mnt/Lab-Notebook      (pick the Obsidian vault folder)
# ---------------------------------------------------------------------------

LAPTOP="${LAPTOP:-yann@macbook}"                                 # (ssh config)
LAPTOP_VAULT="${LAPTOP_VAULT:-Documents/Notebook}"      # relative to the laptop's ~
IPAD_VAULT="${IPAD_VAULT:-/mnt/Notebook}"
STATE="${STATE:-$HOME/.ipad_sync.state}"

# the whole vault is synced, restricted to these extensions (empty = all files)
SYNC_EXT="md canvas png jpg jpeg gif svg pdf"
# never synced (folder or file names; Office/LibreOffice lock files)
SKIP='.git .obsidian .trash .sync-trash .DS_Store ~$* .~lock.*'

SSH="${SSH:-ssh -o ServerAliveInterval=15 -o ConnectTimeout=10}"
TRASH=".sync-trash/$(date +%Y-%m-%d_%H.%M.%S)"

# quote for a shell: abc'd -> 'abc'\''d'
_q() { printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"; }

# shell script printing "mtime size path" for the synced files of vault $1
# (piped to `sh` locally or on the laptop, works with GNU/busybox and BSD stat)
_list_script() {
    printf 'cd %s || exit 1\n' "$(_q "$1")"
    printf 'if stat -c %%Y . >/dev/null 2>&1; then fmt="-c"; f="%%Y %%s %%n"; else fmt="-f"; f="%%m %%z %%N"; fi\n'
    set -f    # no globbing of the patterns below
    o=; printf 'find . \\('
    for s in $SKIP; do printf '%s -name %s' "$o" "$(_q "$s")"; o=' -o'; done
    printf ' \\) -prune -o -type f'
    if [ -n "$SYNC_EXT" ]; then
        o=; printf ' \\('
        for e in $SYNC_EXT; do printf '%s -iname %s' "$o" "$(_q "*.$e")"; o=' -o'; done
        printf ' \\)'
    fi
    set +f
    # "mtime size ./path" -> "mtime size path"
    printf ' -exec stat "$fmt" "$f" {} + | sed %s\n' "$(_q 's/^\([0-9]* [0-9]*\) \.\//\1 /')"
}

# shell script moving the files listed in $2 (vault-relative) of vault $1 to
# the trash folder (the list is embedded, so the script can be piped to ssh)
_trash_script() {
    printf 'cd %s || exit 1\n' "$(_q "$1")"
    printf 'T=%s\n' "$(_q "$TRASH")"
    cat <<'EOF'
while IFS= read -r p; do
    [ -e "$p" ] || continue
    mkdir -p "$T/$(dirname "$p")" && mv "$p" "$T/$p" || echo "  ! could not move $p to the trash" >&2
done <<'__SYNC_LIST__'
EOF
    cat "$2"
    echo "__SYNC_LIST__"
}

_list_laptop() { _list_script "$LAPTOP_VAULT" | $SSH "$LAPTOP" sh; }
_list_ipad()   { _list_script "$IPAD_VAULT" | sh; }

# _plan <state> <laptop list> <ipad list>: prints "ACTION<tab>path", with
# ACTION in PULL, PUSH (copy), DEL_L, DEL_I (delete), CONF_L, CONF_I (conflict,
# laptop / iPad version wins)
_plan() {
    awk -v SF="$1" -v LF="$2" -v IF="$3" '
    function rest(s, n) { while (n-- > 0) sub(/^[^ ]* /, "", s); return s }
    FILENAME == SF { p = rest($0, 4); S[p] = $1 " " $2; SI[p] = $3 " " $4; all[p] = 1; next }
    FILENAME == LF { p = rest($0, 2); L[p] = $1 " " $2; all[p] = 1; next }
    FILENAME == IF { p = rest($0, 2); I[p] = $1 " " $2; all[p] = 1; next }
    function mt(x,  v) { split(x, v, " "); return v[1] + 0 }
    function sz(x,  v) { split(x, v, " "); return v[2] }
    END {
        for (p in all) {
            inL = (p in L); inI = (p in I); inS = (p in S)
            lchg = inL && (!inS || L[p] != S[p])
            ichg = inI && (!inS || I[p] != SI[p])
            a = ""
            if (inL && inI) {
                if (!inS) { if (sz(L[p]) != sz(I[p])) a = (mt(L[p]) >= mt(I[p])) ? "CONF_L" : "CONF_I" }
                else if (lchg && ichg) a = (mt(L[p]) >= mt(I[p])) ? "CONF_L" : "CONF_I"
                else if (lchg) a = "PULL"
                else if (ichg) a = "PUSH"
            } else if (inL) {
                a = (inS && !lchg) ? "DEL_L" : "PULL"
            } else if (inI) {
                a = (inS && !ichg) ? "DEL_I" : "PUSH"
            }
            if (a != "") print a "\t" p
        }
    }' "$1" "$2" "$3" > "$1.plan" || return 1
    LC_ALL=C sort -t "$(printf '\t')" -k2 "$1.plan"; rm -f "$1.plan"
}

# _pick <plan> <ACTION...>: paths of the given actions
_pick() {
    plan="$1"; shift
    for a in "$@"; do sed -n "s/^$a	//p" "$plan"; done
}

ipad_sync() {
    dry=""
    for arg in "$@"; do
        case "$arg" in
            -n|--dry-run) dry=1 ;;
            *) echo "usage: ipad_sync [-n]" >&2; return 1 ;;
        esac
    done
    [ -d "$IPAD_VAULT" ] || { echo "ipad_sync: $IPAD_VAULT not found (mount -t ios . $IPAD_VAULT)" >&2; return 1; }

    tmp=$(mktemp -d) || return 1
    trap 'rm -rf "$tmp"' EXIT INT TERM
    touch "$STATE"

    echo "== listing files on the laptop ($LAPTOP) ..."
    _list_laptop > "$tmp/L" || { echo "ipad_sync: cannot list the laptop vault" >&2; return 1; }
    echo "== listing files on the iPad ..."
    _list_ipad > "$tmp/I" || { echo "ipad_sync: cannot list the iPad vault" >&2; return 1; }
    echo "   $(wc -l < "$tmp/L" | tr -d ' ') file(s) on the laptop, $(wc -l < "$tmp/I" | tr -d ' ') on the iPad"

    cp "$STATE" "$tmp/S"
    _plan "$tmp/S" "$tmp/L" "$tmp/I" > "$tmp/plan" || { echo "ipad_sync: comparison failed" >&2; return 1; }
    if [ ! -s "$tmp/plan" ]; then echo "== already in sync"; return 0; fi

    _pick "$tmp/plan" PULL CONF_L > "$tmp/pull"
    _pick "$tmp/plan" PUSH CONF_I > "$tmp/push"
    _pick "$tmp/plan" DEL_I CONF_L > "$tmp/trash_ipad"
    _pick "$tmp/plan" DEL_L CONF_I > "$tmp/trash_laptop"

    _show() { [ -s "$2" ] && { echo "  -- $1:"; sed 's/^/     /' "$2"; }; }
    _pick "$tmp/plan" PULL   > "$tmp/x"; _show "laptop -> iPad" "$tmp/x"
    _pick "$tmp/plan" PUSH   > "$tmp/x"; _show "iPad -> laptop" "$tmp/x"
    _pick "$tmp/plan" DEL_I  > "$tmp/x"; _show "deleted on the laptop, removed on the iPad" "$tmp/x"
    _pick "$tmp/plan" DEL_L  > "$tmp/x"; _show "deleted on the iPad, removed on the laptop" "$tmp/x"
    _pick "$tmp/plan" CONF_L > "$tmp/x"; _show "CONFLICT, laptop version kept (iPad version to the trash)" "$tmp/x"
    _pick "$tmp/plan" CONF_I > "$tmp/x"; _show "CONFLICT, iPad version kept (laptop version to the trash)" "$tmp/x"
    [ -s "$tmp/trash_ipad" ] || [ -s "$tmp/trash_laptop" ] &&
        echo "  (removed files are moved to <vault>/$TRASH/ on their side)"
    [ -n "$dry" ] && { echo "== dry run, nothing changed"; return 0; }

    if [ -s "$tmp/trash_ipad" ]; then
        _trash_script "$IPAD_VAULT" "$tmp/trash_ipad" | sh
    fi
    if [ -s "$tmp/trash_laptop" ]; then
        _trash_script "$LAPTOP_VAULT" "$tmp/trash_laptop" | $SSH "$LAPTOP" sh ||
            echo "  ! moving files to the laptop trash failed" >&2
    fi

    if [ -s "$tmp/pull" ]; then
        echo "== laptop -> iPad: $(wc -l < "$tmp/pull" | tr -d ' ') file(s)"
        $SSH "$LAPTOP" "cd $(_q "$LAPTOP_VAULT") && COPYFILE_DISABLE=1 tar cf - -T -" < "$tmp/pull" |
            (cd "$IPAD_VAULT" && tar xmf -) || echo "  ! transfer laptop -> iPad failed" >&2
    fi
    if [ -s "$tmp/push" ]; then
        echo "== iPad -> laptop: $(wc -l < "$tmp/push" | tr -d ' ') file(s)"
        (cd "$IPAD_VAULT" && tar cf - -T "$tmp/push") |
            $SSH "$LAPTOP" "cd $(_q "$LAPTOP_VAULT") && tar xf -" || echo "  ! transfer iPad -> laptop failed" >&2
    fi

    # new state: files present on both sides, with their current (mtime, size)
    echo "== saving the sync state ..."
    _list_laptop > "$tmp/L" && _list_ipad > "$tmp/I" || { echo "ipad_sync: cannot re-list, state not saved" >&2; return 1; }
    awk -v LF="$tmp/L" '
        function rest(s) { sub(/^[^ ]* [^ ]* /, "", s); return s }
        FILENAME == LF { L[rest($0)] = $1 " " $2; next }
        { p = rest($0); if (p in L) print L[p], $1, $2, p }' "$tmp/L" "$tmp/I" > "$STATE.new" &&
        mv "$STATE.new" "$STATE"
    echo "== done"
}

# run when executed (not when sourced from an interactive shell)
case "$0" in *ipad_sync*) ipad_sync "$@" ;; esac
