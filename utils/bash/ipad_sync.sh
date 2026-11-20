#!/bin/sh
# ---------------------------------------------------------------------------
# Two-way sync of the Obsidian vault: iPad (iSH)  <->  remote, without rsync
#
#   sh ipad_sync.sh [-n] [-y] [--force-pull | --force-push]      (run in iSH)
#
#   -n, --dry-run   show the plan only, change nothing
#   -y, --yes       no confirmation, even when more than $MAX_CHANGES files change
#   --force-pull    the remote is right: the iPad is made identical to it (files
#                   absent from the remote are moved to the iPad trash, differing
#                   ones are overwritten, the iPad copy going to the trash)
#   --force-push    the iPad is right: same, in the other direction
#
# Safety: when more than $MAX_CHANGES files (default 20) would be copied, moved
# to the trash or overwritten, the plan is shown and a yes/no confirmation is
# asked (e.g. after re-mounting the vault in iSH, an empty or wrong folder would
# otherwise be seen as "all files deleted on the iPad").
#
# How it works (rsync hangs on iSH, so only find/stat/awk/tar/ssh are used):
#   1. list (mtime, size) of the vault files on both sides (1 ssh call)
#   2. compare with the state saved at the end of the previous sync, to tell
#      which side changed, created or deleted each file
#   2b. files present on both sides but with a different (mtime, size) are
#      compared by content (md5): identical ones are left alone (1 ssh call)
#   3. move deleted / conflict-losing files to .sync-trash/<date>/ (in the
#      vault, on the side where they are removed; Obsidian ignores dot folders)
#   4. transfer in one tar stream per direction (2 ssh calls)
#   5. stat the transferred files again and save the new state
#   (a single ssh connection is opened and shared by all these calls)
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
#   first sync (no state): a file present on both sides is compared by
#   content, identical -> left as is, different -> conflict.
#   A file whose content is identical on both sides is never copied nor
#   trashed, whatever its timestamps.
#
# The "remote" side is the first reachable host of $HOSTS (macbook, then the
# lab server); set REMOTE=user@host to force one. Each host has its own sync
# state ($HOME/.ipad_sync.<host>.state), so alternating between them is safe.
#
# Needs in iSH: openssh-client (ssh keys to the hosts, `macbook` and
# `lab-server` defined in ~/.ssh/config: HostName fd10::9 and fd10::1), and a
# tar supporting -T (busybox tar does; otherwise `apk add tar`). The vault
# must be mounted:
#   mount -t ios . /mnt/Lab-Notebook      (pick the Obsidian vault folder)
# ---------------------------------------------------------------------------

HOSTS="${HOSTS:-macbook lab-server}"            # (ssh config), by priority
REMOTE="${REMOTE:-}"                                      # empty = first reachable of $HOSTS
REMOTE_VAULT="${REMOTE_VAULT:-Documents/Notebook}"      # relative to the host's ~
IPAD_VAULT="${IPAD_VAULT:-/mnt/Notebook}"
STATE="${STATE:-}"                                        # empty = per host, see _pick_host
_REMOTE0="$REMOTE"; _STATE0="$STATE"      # re-picked at each run (when sourced)

# the whole vault is synced, restricted to these extensions (empty = all files)
SYNC_EXT="md canvas png jpg jpeg gif svg pdf"
# never synced (folder or file names; Office/LibreOffice lock files)
SKIP='.git .obsidian .trash .sync-trash .DS_Store ~$* .~lock.*'

MAX_CHANGES="${MAX_CHANGES:-20}"   # more file changes than this -> ask for confirmation

SSH="${SSH:-ssh -o ServerAliveInterval=15 -o ConnectTimeout=10}"
_SSH0="$SSH"                              # $SSH gets the connection sharing options at each run
TRASH=".sync-trash/$(date +%Y-%m-%d_%H.%M.%S)"

# quote for a shell: abc'd -> 'abc'\''d'
_q() { printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"; }

# shell line choosing the stat format "mtime size path" (GNU/busybox or BSD)
_STATFMT='if stat -c %Y . >/dev/null 2>&1; then fmt="-c"; f="%Y %s %n"; else fmt="-f"; f="%m %z %N"; fi'

# shell script printing "mtime size path" for the synced files of vault $1
# (piped to `sh` locally or on the remote)
_list_script() {
    printf 'cd %s || exit 1\n' "$(_q "$1")"
    printf '%s\n' "$_STATFMT"
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

# shell script printing "mtime size path" for the files listed in $2
# (vault-relative) of vault $1 (missing files are skipped)
_stat_script() {
    printf 'cd %s || exit 1\n' "$(_q "$1")"
    printf '%s\n' "$_STATFMT"
    cat <<'EOF'
tr '\n' '\0' <<'__SYNC_LIST__' | xargs -0 stat "$fmt" "$f" 2>/dev/null
EOF
    cat "$2"
    echo "__SYNC_LIST__"
}

# _update_list <list> <new stats> <removed paths...>: the list without the
# removed paths, plus the new stats
_update_list() {
    l="$1"; n="$2"; shift 2
    cat "$@" > "$l.rm"
    awk -v RF="$l.rm" '
        function rest(s) { sub(/^[^ ]* [^ ]* /, "", s); return s }
        FILENAME == RF { R[$0] = 1; next }
        !(rest($0) in R)' "$l.rm" "$l"
    cat "$n"; rm -f "$l.rm"
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

# shell script printing "hash<tab>path" for the files listed in $2
# (vault-relative) of vault $1 (md5 with md5sum or BSD md5; cksum otherwise:
# if the two sides use different tools, the hashes never match and such files
# are handled as different)
_hash_script() {
    printf 'cd %s || exit 1\n' "$(_q "$1")"
    cat <<'EOF'
if command -v md5sum >/dev/null 2>&1; then H=md5sum
elif command -v md5 >/dev/null 2>&1; then H="md5 -r"
else H=cksum; fi
# one hashing process for all the files (forks are very slow on iSH)
tr '\n' '\0' <<'__SYNC_LIST__' | xargs -0 $H 2>/dev/null | sed 's/^\([^ ]*\)  */\1	/'
EOF
    cat "$2"
    echo "__SYNC_LIST__"
}

# _both <plan> <remote list> <ipad list>: paths of the copy / conflict actions
# whose file exists on both sides with the same size (candidates for the
# content check; files of different sizes differ, no need to read them)
_both() {
    awk -v PF="$1" -v LF="$2" -v IF="$3" '
    function rest(s, n) { while (n-- > 0) sub(/^[^ ]* /, "", s); return s }
    FILENAME == LF { L[rest($0, 2)] = $2; next }
    FILENAME == IF { I[rest($0, 2)] = $2; next }
    FILENAME == PF { a = $0; sub(/\t.*/, "", a); p = $0; sub(/^[^\t]*\t/, "", p)
        if (a ~ /^(PULL|PUSH|CONF_L|CONF_I)$/ && (p in L) && (p in I) && L[p] == I[p]) print p }' "$2" "$3" "$1"
}

# _drop_same <plan> <remote hashes> <ipad hashes>: the plan without the files
# whose content is identical on both sides (only mtime differs)
_drop_same() {
    awk -v LH="$2" -v IH="$3" '
    function path(s) { sub(/^[^\t]*\t/, "", s); return s }
    function key(s)  { sub(/\t.*/, "", s); return s }
    FILENAME == LH { L[path($0)] = key($0); next }
    FILENAME == IH { I[path($0)] = key($0); next }
    { p = path($0); if (!((p in L) && (p in I) && L[p] == I[p])) print }' "$2" "$3" "$1"
}

# _save_state <remote list> <ipad list>: files present on both sides, with
# their current (mtime, size)
_save_state() {
    awk -v LF="$1" '
        function rest(s) { sub(/^[^ ]* [^ ]* /, "", s); return s }
        FILENAME == LF { L[rest($0)] = $1 " " $2; next }
        { p = rest($0); if (p in L) print L[p], $1, $2, p }' "$1" "$2" > "$STATE.new" &&
        mv "$STATE.new" "$STATE"
}

# sets REMOTE to the first host of $HOSTS answering over ssh (unless already
# set), and STATE to that host's state file (unless already set)
_pick_host() {
    if [ -z "$REMOTE" ]; then
        for h in $HOSTS; do
            echo "== trying $h ..."
            if $SSH -o BatchMode=yes -o ConnectTimeout=5 "$h" true 2>/dev/null; then
                REMOTE="$h"; break
            fi
        done
        [ -n "$REMOTE" ] || { echo "ipad_sync: no host reachable among: $HOSTS" >&2; return 1; }
    fi
    if [ -z "$STATE" ]; then
        STATE="$HOME/.ipad_sync.${REMOTE#*@}.state"
        # state of the single-host version of this script (it synced with the macbook)
        [ ! -e "$STATE" ] && [ "${REMOTE#*@}" = macbook ] && [ -e "$HOME/.ipad_sync.state" ] &&
            mv "$HOME/.ipad_sync.state" "$STATE"
    fi
    echo "== syncing with $REMOTE"
}

_list_remote() { _list_script "$REMOTE_VAULT" | $SSH "$REMOTE" sh; }
_list_ipad()   { _list_script "$IPAD_VAULT" | sh; }

# _plan <state> <remote list> <ipad list>: prints "ACTION<tab>path", with
# ACTION in PULL, PUSH (copy), DEL_L, DEL_I (delete), CONF_L, CONF_I (conflict,
# remote / iPad version wins, the other copy goes to the trash)
# _plan ... <force>: with force = pull (or push), the remote (or iPad) side is
# copied over the other one, without looking at which side changed
_plan() {
    awk -v SF="$1" -v LF="$2" -v IF="$3" -v FORCE="$4" '
    function rest(s, n) { while (n-- > 0) sub(/^[^ ]* /, "", s); return s }
    FILENAME == SF { p = rest($0, 4); S[p] = $1 " " $2; SI[p] = $3 " " $4; all[p] = 1; next }
    FILENAME == LF { p = rest($0, 2); L[p] = $1 " " $2; all[p] = 1; next }
    FILENAME == IF { p = rest($0, 2); I[p] = $1 " " $2; all[p] = 1; next }
    function mt(x,  v) { split(x, v, " "); return v[1] + 0 }
    END {
        for (p in all) {
            inL = (p in L); inI = (p in I); inS = (p in S)
            lchg = inL && (!inS || L[p] != S[p])
            ichg = inI && (!inS || I[p] != SI[p])
            a = ""
            # same file on both sides: unchanged since the last sync (with no
            # state, the content check after the plan decides)
            same = inL && inI && inS && L[p] == S[p] && I[p] == SI[p]
            if (FORCE == "pull") {
                if (inL && !inI) a = "PULL"
                else if (inL && !same) a = "CONF_L"
                else if (!inL) a = "DEL_I"
            } else if (FORCE == "push") {
                if (inI && !inL) a = "PUSH"
                else if (inI && !same) a = "CONF_I"
                else if (!inI) a = "DEL_L"
            } else if (inL && inI) {
                if (!inS) a = (mt(L[p]) >= mt(I[p])) ? "CONF_L" : "CONF_I"
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
    dry=""; yes=""; force=""
    for arg in "$@"; do
        case "$arg" in
            -n|--dry-run) dry=1 ;;
            -y|--yes) yes=1 ;;
            --force-pull|--force-push)
                [ -n "$force" ] && [ "$force" != "${arg#--force-}" ] &&
                    { echo "ipad_sync: --force-pull and --force-push are exclusive" >&2; return 1; }
                force="${arg#--force-}" ;;
            *) echo "usage: ipad_sync [-n] [-y] [--force-pull | --force-push]" >&2; return 1 ;;
        esac
    done
    [ -d "$IPAD_VAULT" ] || { echo "ipad_sync: $IPAD_VAULT not found (mount -t ios . $IPAD_VAULT)" >&2; return 1; }
    REMOTE="$_REMOTE0"; STATE="$_STATE0"
    t0=$(date +%s)

    # one ssh connection for the whole run (the ssh handshake takes seconds on
    # iSH): the first call opens it, the next ones go through it
    tmp=$(mktemp -d) || return 1
    SSH="$_SSH0 -o ControlMaster=auto -o ControlPath=$tmp/mux -o ControlPersist=60"
    trap '[ -n "$REMOTE" ] && $SSH -O exit "$REMOTE" 2>/dev/null; rm -rf "$tmp"' EXIT INT TERM

    _pick_host || return 1
    touch "$STATE"

    echo "== listing files on both sides ..."
    _list_remote > "$tmp/L" & lpid=$!
    _list_ipad > "$tmp/I" || { echo "ipad_sync: cannot list the iPad vault" >&2; wait; return 1; }
    wait "$lpid" || { echo "ipad_sync: cannot list the remote vault" >&2; return 1; }
    echo "   $(wc -l < "$tmp/L" | tr -d ' ') file(s) on the remote, $(wc -l < "$tmp/I" | tr -d ' ') on the iPad [$(( $(date +%s) - t0 ))s]"

    cp "$STATE" "$tmp/S"
    _plan "$tmp/S" "$tmp/L" "$tmp/I" "$force" > "$tmp/plan" || { echo "ipad_sync: comparison failed" >&2; return 1; }
    if [ ! -s "$tmp/plan" ]; then echo "== already in sync"; return 0; fi

    # files present on both sides whose (mtime, size) differ: compare contents,
    # identical ones are left alone (only their timestamp differs)
    _both "$tmp/plan" "$tmp/L" "$tmp/I" > "$tmp/both"
    if [ -s "$tmp/both" ]; then
        echo "== comparing the content of $(wc -l < "$tmp/both" | tr -d ' ') file(s) present on both sides ..."
        # both sides hashed in parallel
        _hash_script "$REMOTE_VAULT" "$tmp/both" | $SSH "$REMOTE" sh > "$tmp/HL" & hpid=$!
        _hash_script "$IPAD_VAULT" "$tmp/both" | sh > "$tmp/HI"
        wait "$hpid"
        # (pipeline statuses are sed's: check that every file got a hash)
        nb=$(wc -l < "$tmp/both")
        if [ "$(wc -l < "$tmp/HL")" -eq "$nb" ] && [ "$(wc -l < "$tmp/HI")" -eq "$nb" ]; then
            _drop_same "$tmp/plan" "$tmp/HL" "$tmp/HI" > "$tmp/plan2" && mv "$tmp/plan2" "$tmp/plan"
            nsame=$(( $(wc -l < "$tmp/both") - $(_both "$tmp/plan" "$tmp/L" "$tmp/I" | wc -l) ))
            [ "$nsame" -gt 0 ] && echo "   $nsame file(s) with identical content (only the timestamp differs): left as is"
            echo "   [$(( $(date +%s) - t0 ))s]"
        else
            echo "ipad_sync: content comparison failed, nothing changed" >&2; return 1
        fi
        if [ ! -s "$tmp/plan" ]; then
            [ -z "$dry" ] && _save_state "$tmp/L" "$tmp/I"
            echo "== already in sync"; return 0
        fi
    fi
    [ -n "$force" ] && echo "== forced $force: the $( [ "$force" = pull ] && echo remote || echo iPad) side is kept"

    _pick "$tmp/plan" PULL CONF_L > "$tmp/pull"
    _pick "$tmp/plan" PUSH CONF_I > "$tmp/push"
    _pick "$tmp/plan" DEL_I CONF_L > "$tmp/trash_ipad"
    _pick "$tmp/plan" DEL_L CONF_I > "$tmp/trash_remote"

    _show() { [ -s "$2" ] && { echo "  -- $1:"; sed 's/^/     /' "$2"; }; }
    _pick "$tmp/plan" PULL   > "$tmp/x"; _show "remote -> iPad" "$tmp/x"
    _pick "$tmp/plan" PUSH   > "$tmp/x"; _show "iPad -> remote" "$tmp/x"
    _pick "$tmp/plan" DEL_I  > "$tmp/x"; _show "deleted on the remote, removed on the iPad" "$tmp/x"
    _pick "$tmp/plan" DEL_L  > "$tmp/x"; _show "deleted on the iPad, removed on the remote" "$tmp/x"
    if [ -n "$force" ]; then c="DIFFERENT"; else c="CONFLICT"; fi
    _pick "$tmp/plan" CONF_L > "$tmp/x"; _show "$c, remote version kept (iPad version to the trash)" "$tmp/x"
    _pick "$tmp/plan" CONF_I > "$tmp/x"; _show "$c, iPad version kept (remote version to the trash)" "$tmp/x"
    [ -s "$tmp/trash_ipad" ] || [ -s "$tmp/trash_remote" ] &&
        echo "  (removed files are moved to <vault>/$TRASH/ on their side)"

    n=$(wc -l < "$tmp/plan" | tr -d ' ')
    nI=$(wc -l < "$tmp/trash_ipad" | tr -d ' '); nL=$(wc -l < "$tmp/trash_remote" | tr -d ' ')
    echo "== $n file change(s): $(wc -l < "$tmp/pull" | tr -d ' ') remote -> iPad, $(wc -l < "$tmp/push" | tr -d ' ') iPad -> remote, $nI to the iPad trash, $nL to the remote trash"
    [ -n "$dry" ] && { echo "== dry run, nothing changed"; return 0; }

    if [ "$n" -gt "$MAX_CHANGES" ] && [ -z "$yes" ]; then
        echo "!! more than $MAX_CHANGES files would change."
        [ -s "$tmp/L" ] || echo "!! the remote vault ($REMOTE:$REMOTE_VAULT) has no file: wrong folder?"
        [ -s "$tmp/I" ] || echo "!! the iPad vault ($IPAD_VAULT) has no file: is it mounted? (mount -t ios . $IPAD_VAULT)"
        printf "proceed? [y/N] "
        ans=; read -r ans 2>/dev/null < /dev/tty || read -r ans || ans=
        case "$ans" in
            y|Y|yes|YES) ;;
            *) echo "== aborted, nothing changed (use -y to skip this question)"; return 1 ;;
        esac
    fi

    if [ -s "$tmp/trash_ipad" ]; then
        _trash_script "$IPAD_VAULT" "$tmp/trash_ipad" | sh
    fi
    if [ -s "$tmp/trash_remote" ]; then
        _trash_script "$REMOTE_VAULT" "$tmp/trash_remote" | $SSH "$REMOTE" sh ||
            echo "  ! moving files to the remote trash failed" >&2
    fi

    if [ -s "$tmp/pull" ]; then
        echo "== remote -> iPad: $(wc -l < "$tmp/pull" | tr -d ' ') file(s)"
        $SSH "$REMOTE" "cd $(_q "$REMOTE_VAULT") && COPYFILE_DISABLE=1 tar cf - -T -" < "$tmp/pull" |
            (cd "$IPAD_VAULT" && tar xmf -) || echo "  ! transfer remote -> iPad failed" >&2
    fi
    if [ -s "$tmp/push" ]; then
        echo "== iPad -> remote: $(wc -l < "$tmp/push" | tr -d ' ') file(s)"
        (cd "$IPAD_VAULT" && tar cf - -T "$tmp/push") |
            $SSH "$REMOTE" "cd $(_q "$REMOTE_VAULT") && tar xf -" || echo "  ! transfer iPad -> remote failed" >&2
    fi

    # new state: files present on both sides, with their current (mtime, size);
    # only the files touched by this run are stat-ed again
    echo "== saving the sync state ..."
    : > "$tmp/nL"; : > "$tmp/nI"
    if [ -s "$tmp/push" ]; then
        _stat_script "$REMOTE_VAULT" "$tmp/push" | $SSH "$REMOTE" sh > "$tmp/nL" ||
            { echo "ipad_sync: cannot stat the remote files, state not saved" >&2; return 1; }
    fi
    [ -s "$tmp/pull" ] && _stat_script "$IPAD_VAULT" "$tmp/pull" | sh > "$tmp/nI"
    _update_list "$tmp/L" "$tmp/nL" "$tmp/trash_remote" "$tmp/push" > "$tmp/L2" &&
        _update_list "$tmp/I" "$tmp/nI" "$tmp/trash_ipad" "$tmp/pull" > "$tmp/I2" &&
        _save_state "$tmp/L2" "$tmp/I2"
    echo "== done [$(( $(date +%s) - t0 ))s]"
}

# run when executed (not when sourced from an interactive shell)
case "$0" in *ipad_sync*) ipad_sync "$@" ;; esac
