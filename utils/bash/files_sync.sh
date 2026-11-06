# ---------------------------------------------------------------------------
# Sync files/folders to the same location (relative to ~) on another computer
#
#   sync_file <file> [<file> ...] user@host [-n]
#       copy the file(s) to the same place on the host, e.g. from ~/my-folder:
#       sync_file my-file.ext yann@host  ->  host:~/my-folder/my-file.ext
#       (missing folders are created on the host)
#
#   sync_folder user@host [-n]
#       mirror the current directory to the same place on the host, e.g. from
#       ~/code/my-folder  ->  host:~/code/my-folder (created if missing).
#       - git material is skipped (.git, .gitignore, .gitmodules, .github, ...)
#       - files deleted here are removed on the host, but moved to
#         host:<folder>/.sync-trash/<date_time>/ (listed in the output)
#
# Both are one-way (here -> host) and never overwrite a file that is newer on
# the host (rsync -u): such files are left untouched.
# -n = dry run (show what would be done).
# Works in bash and zsh. Needs ssh access to the host (keys recommended).
# ---------------------------------------------------------------------------

SF_TRASH=".sync-trash"     # hidden folder (inside the synced folder, on the host)

# ssh connection shared by the successive ssh/rsync calls (single login)
SF_SSH="${SF_SSH:-ssh -o ControlMaster=auto -o ControlPath=$HOME/.ssh/sf-%C -o ControlPersist=60}"
_sf_ssh() { sh -c "$SF_SSH \"\$@\"" _sf_ssh "$@"; }   # (zsh-safe word splitting)

# quote a string for the remote shell: abc'd -> 'abc'\''d'
_sf_q() { printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"; }

# escape a remote rsync path for the remote shell: my folder -> my\ folder
# (RSYNC_OLD_ARGS=1 below stops rsync >= 3.2.4 from escaping it a second time)
_sf_e() { printf '%s' "$1" | sed 's/[^A-Za-z0-9_.\/+-]/\\&/g'; }

# _sf_rel <absolute path>: path relative to ~ (fails if outside ~)
_sf_rel() {
    case "$1" in
        "$HOME")   printf '.\n' ;;
        "$HOME"/*) printf '%s\n' "${1#"$HOME"/}" ;;
        *) echo "sync: $1 is not inside your home folder ($HOME)" >&2; return 1 ;;
    esac
}

# drop rsync -v noise
_sf_filter() {
    sed "/^$/d;/^sent /d;/^total /d;/^building /d;/^Transfer starting/d;/^\.\/$/d;/^deleting /d;
         s/^Skip newer '\(.*\)'$/\1  (kept: newer on the host)/;s/^/     /"
}

sync_file() {
    local arg host="" dry="" files="" f dir rel n=0 out
    for arg in "$@"; do
        case "$arg" in
            -n|--dry-run) dry="-n" ;;
            -*) echo "usage: sync_file <file> [<file> ...] user@host [-n]" >&2; return 1 ;;
            *)  [ -n "$host" ] && files="$files$host
"
                host="$arg" ;;
        esac
    done
    if [ -z "$files" ]; then
        echo "usage: sync_file <file> [<file> ...] user@host [-n]" >&2; return 1
    fi
    case "$host" in *:*) echo "sync_file: give the host without ':path' ($host)" >&2; return 1 ;; esac

    echo "== files -> $host${dry:+  [dry run]}"
    while IFS= read -r f; do
        [ -z "$f" ] && continue
        if [ -d "$f" ]; then
            echo "  ! $f is a folder: cd into it and use sync_folder" >&2; continue
        elif [ ! -f "$f" ]; then
            echo "  ! not found: $f" >&2; continue
        fi
        dir=$(cd "$(dirname "$f")" && pwd) || continue
        rel=$(_sf_rel "$dir") || continue
        if [ -z "$dry" ]; then
            _sf_ssh "$host" "mkdir -p $(_sf_q "$rel")" || { echo "  ! cannot create ~/$rel on $host" >&2; continue; }
        fi
        out=$(RSYNC_OLD_ARGS=1 rsync -auv $dry -e "$SF_SSH" \
                    "$f" "$host:$(_sf_e "$rel")/" | _sf_filter) || { echo "  ! rsync failed for $f" >&2; continue; }
        if printf '%s\n' "$out" | grep -qxF "     $(basename "$f")"; then
            echo "  copied   ~/$rel/$(basename "$f")"
            n=$((n + 1))
        else
            echo "  skipped  ~/$rel/$(basename "$f")  (already up to date, or newer on $host)"
        fi
    done <<EOF
$files
EOF
    echo "== $n file(s) copied"
}

sync_folder() {
    local arg host="" dry="" rel qrel state stamp out deleted nd
    for arg in "$@"; do
        case "$arg" in
            -n|--dry-run) dry="-n" ;;
            -*|"") echo "usage: sync_folder user@host [-n]" >&2; return 1 ;;
            *)  [ -n "$host" ] && { echo "usage: sync_folder user@host [-n]" >&2; return 1; }
                host="$arg" ;;
        esac
    done
    [ -z "$host" ] && { echo "usage: sync_folder user@host [-n]" >&2; return 1; }
    case "$host" in *:*) echo "sync_folder: give the host without ':path' ($host)" >&2; return 1 ;; esac

    rel=$(_sf_rel "$PWD") || return 1
    if [ "$rel" = "." ]; then
        echo "sync_folder: refusing to mirror your whole home folder" >&2; return 1
    fi
    if [ -z "$(ls -A)" ]; then
        echo "sync_folder: $PWD is empty, refusing (it would empty the host folder)" >&2; return 1
    fi
    qrel=$(_sf_q "$rel")

    echo "== ~/$rel  ->  $host:~/$rel${dry:+  [dry run]}"

    # create the folder on the host if needed
    if [ -n "$dry" ]; then
        state=$(_sf_ssh "$host" "[ -d $qrel ] && echo exists || echo missing") || return 1
    else
        state=$(_sf_ssh "$host" "[ -d $qrel ] && echo exists || { mkdir -p $qrel && echo created; }") || return 1
    fi
    case "$state" in
        exists)  ;;
        created) echo "  created $host:~/$rel" ;;
        missing) echo "  $host:~/$rel does not exist, it would be created"
                 echo "== dry run, nothing done"; return 0 ;;
        *) echo "sync_folder: could not access $host:~/$rel" >&2; return 1 ;;
    esac

    # 1) deletions: list what exists on the host but not here (rsync dry run,
    #    --existing + --ignore-existing = transfer nothing), then move those
    #    items to the host's trash folder. (rsync --backup is not used for this:
    #    macOS openrsync silently skips deletions when it is set.)
    stamp=$(date +%Y-%m-%d_%H.%M.%S)
    if [ "$state" = exists ]; then
        out=$(RSYNC_OLD_ARGS=1 rsync -rvn -e "$SF_SSH" \
                    --existing --ignore-existing --delete \
                    --exclude="/$SF_TRASH" --exclude='.git*' --exclude='.DS_Store' \
                    ./ "$host:$(_sf_e "$rel")/") || { echo "sync_folder: rsync failed (deletion pass)" >&2; return 1; }
        # top-level deleted items only (a deleted folder carries its content)
        deleted=$(printf '%s\n' "$out" | sed -n 's/^deleting //p' | LC_ALL=C sort |
                  awk 'd != "" && index($0, d) == 1 { next } { print; d = ($0 ~ /\/$/) ? $0 : "" }')
        if [ -n "$deleted" ]; then
            nd=$(printf '%s\n' "$deleted" | wc -l | tr -d ' ')
            echo "  -- $nd item(s) deleted here, to remove on $host:"
            printf '%s\n' "$deleted" | sed 's/^/     /'
            if [ -n "$dry" ]; then
                echo "     (would be moved to $host:~/$rel/$SF_TRASH/$stamp/)"
            else
                printf '%s\n' "$deleted" | _sf_ssh "$host" "sh -c $(_sf_q '
                    cd "$1" || exit 1
                    while IFS= read -r p; do
                        p=${p%/}; [ -e "$p" ] || [ -L "$p" ] || continue
                        mkdir -p "$2/$(dirname "$p")" && mv "$p" "$2/$p" ||
                            echo "     ! could not move $p" >&2
                    done' ) _ $(_sf_q "$rel") $(_sf_q "$SF_TRASH/$stamp")" ||
                    { echo "sync_folder: moving deleted items to the trash failed" >&2; return 1; }
                echo "     moved to $host:~/$rel/$SF_TRASH/$stamp/"
            fi
        fi
    fi

    # 2) copy new/modified files (never overwrite files newer on the host)
    out=$(RSYNC_OLD_ARGS=1 rsync -auv $dry -e "$SF_SSH" \
                --exclude="/$SF_TRASH" --exclude='.git*' --exclude='.DS_Store' \
                ./ "$host:$(_sf_e "$rel")/" | _sf_filter) || { echo "sync_folder: rsync failed (copy pass)" >&2; return 1; }
    if [ -n "$out" ]; then
        echo "  -- copied:"
        printf '%s\n' "$out"
    else
        echo "  -- no file to copy (up to date)"
    fi
    echo "== done${dry:+ (dry run, nothing changed)}"
}
