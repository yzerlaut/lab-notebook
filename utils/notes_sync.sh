# ---------------------------------------------------------------------------
# Notes sync: OneDrive Lab-Notebook  <->  private-notes git repo (GitHub)
#
#   notes_sync  [YYYY-MM-DD] [-n]  copy the daily note (default: today) and the
#                                  markdown notes listed under its "### to synch"
#                                  heading to the repo root, commit, pull, push
#   notes_clean [YYYY-MM-DD] [-n]  move to _archives/ the notes of the repo root
#                                  that are not in that daily note, commit, push
#
# Notes go flat into the repo root under their own name, e.g.
#   Grants/2027-ANR-CodeReconf/CodeReconf-proposal.md  <->  CodeReconf-proposal.md
#   Daily-Notes/2026-10-06.md                          <->  2026-10-06.md
# Two-way: a note edited on GitHub is merged by git (pull --rebase) and the
# merged version is copied back to OneDrive. A note created in the repo (no
# file of that name anywhere in the Lab-Notebook) is copied to Daily-Notes/
# and linked under "to synch" in the daily note.
# -n = dry run (show what would be done).
# Works in bash and zsh.
# ---------------------------------------------------------------------------

NOTES_REPO="$HOME/Documents/Research/private-notes"
NOTES_SRC="$HOME/OneDrive - ICM/Lab-Notebook"
NOTES_DAILY_DIR="Daily-Notes"      # relative to NOTES_SRC
NOTES_SECTION="to synch"           # heading that holds the list

# _notes_list <YYYY-MM-DD>: NOTES_SRC-relative paths of the daily note and of
# the links under its "to synch" heading (links are relative to the daily-notes
# folder). Prints an empty line for a link that escapes NOTES_SRC.
_notes_list() {
    local note="$NOTES_SRC/$NOTES_DAILY_DIR/$1.md"
    [ -f "$note" ] || { echo "notes: no daily note $note" >&2; return 1; }
    printf '%s\n' "$NOTES_DAILY_DIR/$1.md"
    awk -v sec="$NOTES_SECTION" '
        /^#+[ \t]/ { if (f) exit; h = $0; sub(/^#+[ \t]+/, "", h); sub(/[ \t]+$/, "", h)
                     if (tolower(h) == tolower(sec)) f = 1; next }
        f' "$note" |
    sed -nE 's/^[[:space:]]*[-*+][[:space:]]+\[[^]]*\]\(<?([^)>]+)>?\).*/\1/p' |
    sed 's/%20/ /g' |
    while IFS= read -r link; do
        # collapse "a/b/../c" -> "a/c"
        printf '%s\n' "$NOTES_DAILY_DIR/$link" | awk -F/ '{
            n = 0
            for (i = 1; i <= NF; i++) {
                if ($i == "" || $i == ".") continue
                if ($i == "..") { if (n == 0) { print ""; exit }; n--; continue }
                a[++n] = $i
            }
            s = a[1]; for (i = 2; i <= n; i++) s = s "/" a[i]
            print s
        }'
    done
}

# _notes_daily <YYYY-MM-DD> [dry]: make sure the daily note is in Daily-Notes/,
# taking it from GitHub if it was created there (e.g. on the iPad).
# Returns 2 on a dry run when the note is only on GitHub.
_notes_daily() {
    local day="$1" dry="$2" note="$NOTES_SRC/$NOTES_DAILY_DIR/$1.md"
    [ -f "$note" ] && return 0
    if [ -n "$dry" ]; then
        git -C "$NOTES_REPO" fetch -q 2>/dev/null
        git -C "$NOTES_REPO" cat-file -e "@{u}:$day.md" 2>/dev/null ||
            { echo "notes: no daily note for $day, neither local nor on GitHub" >&2; return 1; }
        echo "  <- $day.md  (daily note from GitHub, to $NOTES_DAILY_DIR/)"
        echo "== dry run stops here: the daily note is only on GitHub"
        return 2
    fi
    git -C "$NOTES_REPO" pull -q --rebase ||
        { echo "notes: pull failed, cannot fetch the daily note from GitHub" >&2; return 1; }
    [ -f "$NOTES_REPO/$day.md" ] ||
        { echo "notes: no daily note for $day, neither local nor on GitHub" >&2; return 1; }
    cp -p "$NOTES_REPO/$day.md" "$note" &&
        echo "  <- $day.md  (daily note from GitHub, to $NOTES_DAILY_DIR/)"
}

# _notes_commit_push <message>: commit the markdown changes, pull, push.
_notes_commit_push() {
    git -C "$NOTES_REPO" add -A -- '*.md'
    if ! git -C "$NOTES_REPO" diff --cached --quiet; then
        git -C "$NOTES_REPO" commit -q -m "$1" && echo "== committed: $1"
    fi
    if ! git -C "$NOTES_REPO" pull -q --rebase; then
        git -C "$NOTES_REPO" rebase --abort 2>/dev/null
        echo "notes: pull failed (offline or conflict); local commit kept." >&2
        echo "       fix it with: cd \"$NOTES_REPO\" && git pull --rebase  (then rerun)" >&2
        return 1
    fi
}

# _notes_new: names of the repo-root notes that exist nowhere in NOTES_SRC
# (notes created on GitHub / in the repo).
_notes_new() {
    local local_names
    local_names=$(find "$NOTES_SRC" -type f -name '*.md' ! -path '*/.trash/*' | sed 's|.*/||')
    find "$NOTES_REPO" -mindepth 1 -maxdepth 1 -type f -name '*.md' ! -name 'README.md' | sort |
    while IFS= read -r name; do
        name=$(basename "$name")
        printf '%s\n' "$local_names" | grep -qxF -- "$name" || printf '%s\n' "$name"
    done
}

# _notes_add_link <daily note> <name.md>: add "- [name](name.md)" at the end of
# the "to synch" list (the heading is created at the top if missing).
_notes_add_link() {
    local note="$1" name="$2" tmp
    tmp=$(mktemp) || return 1
    awk -v sec="$NOTES_SECTION" -v item="- [${name%.md}]($(printf '%s' "$name" | sed 's/ /%20/g'))" '
        FNR == NR {
            if (/^#+[ \t]/) {
                if (f) { f = 0; done = 1 }
                else if (!done) { h = $0; sub(/^#+[ \t]+/, "", h); sub(/[ \t]+$/, "", h)
                                  if (tolower(h) == tolower(sec)) { f = 1; at = FNR } }
            } else if (f && /^[ \t]*[-*+][ \t]+\[/) at = FNR
            next
        }
        FNR == 1 && !at { print "### " sec; print item }
        { print }
        FNR == at { print item }' "$note" "$note" > "$tmp" && cat "$tmp" > "$note"
    rm -f "$tmp"
}

_notes_push() {
    if [ -n "$(git -C "$NOTES_REPO" log --oneline '@{u}..' 2>/dev/null)" ]; then
        git -C "$NOTES_REPO" push -q && echo "== pushed to GitHub"
    else
        echo "== GitHub already up to date"
    fi
}

notes_sync() {
    local day dry="" arg list rel name src dst new note n=0
    day=$(date +%F)
    for arg in "$@"; do
        case "$arg" in
            -n|--dry-run) dry=1 ;;
            ????-??-??)   day="$arg" ;;
            *) echo "usage: notes_sync [YYYY-MM-DD] [-n]" >&2; return 1 ;;
        esac
    done
    _notes_daily "$day" "$dry"; case $? in 0) ;; 2) return 0 ;; *) return 1 ;; esac
    list=$(_notes_list "$day") || return 1

    # 1. OneDrive -> repo, for the notes edited since the last sync
    echo "== Lab-Notebook -> private-notes  ($day)${dry:+  [dry run]}"
    while IFS= read -r rel; do
        [ -z "$rel" ] && { echo "  ! skipping a link outside the Lab-Notebook" >&2; continue; }
        name=$(basename "$rel"); src="$NOTES_SRC/$rel"; dst="$NOTES_REPO/$name"
        case "$name" in *.md) ;; *) echo "  ! not a markdown note, skipped: $rel" >&2; continue ;; esac
        [ -f "$src" ] || { echo "  ! not found: $rel" >&2; continue; }
        if { [ ! -f "$dst" ] || [ "$src" -nt "$dst" ]; } && ! cmp -s "$src" "$dst"; then
            echo "  -> $name"
            [ -z "$dry" ] && cp -p "$src" "$dst"
        fi
        n=$((n + 1))
    done <<EOF
$list
EOF
    if [ -n "$dry" ]; then
        _notes_new | sed "s|^|  <- |; s|\$|  (new on GitHub, to $NOTES_DAILY_DIR/)|"
        echo "== dry run, nothing copied, committed or pushed"; return 0
    fi

    # 2. commit + merge the GitHub edits
    _notes_commit_push "sync $day" || return 1

    # 3. repo -> OneDrive, for the notes changed on GitHub
    while IFS= read -r rel; do
        [ -z "$rel" ] && continue
        name=$(basename "$rel"); src="$NOTES_SRC/$rel"; dst="$NOTES_REPO/$name"
        [ -f "$src" ] && [ -f "$dst" ] || continue
        if ! cmp -s "$dst" "$src"; then
            cp -p "$dst" "$src" && echo "  <- $name  (updated from GitHub)"
        fi
    done <<EOF
$list
EOF

    # 4. notes created on GitHub -> Daily-Notes/, linked in the "to synch" list
    new=$(_notes_new)
    if [ -n "$new" ]; then
        note="$NOTES_SRC/$NOTES_DAILY_DIR/$day.md"
        while IFS= read -r name; do
            cp -p "$NOTES_REPO/$name" "$NOTES_SRC/$NOTES_DAILY_DIR/$name" &&
                _notes_add_link "$note" "$name" &&
                echo "  <- $name  (new on GitHub, to $NOTES_DAILY_DIR/)" && n=$((n + 1))
        done <<EOF
$new
EOF
        cp -p "$note" "$NOTES_REPO/$day.md"
        _notes_commit_push "import new notes into $day" || return 1
    fi

    _notes_push
    echo "== $n note(s) synced"
}

# Move to _archives/ the root notes that are not in the daily note (old daily
# notes included). Nothing is lost: the previous versions stay in git history.
notes_clean() {
    local day dry="" arg list keep new todo name n=0
    day=$(date +%F)
    for arg in "$@"; do
        case "$arg" in
            -n|--dry-run) dry=1 ;;
            ????-??-??)   day="$arg" ;;
            *) echo "usage: notes_clean [YYYY-MM-DD] [-n]" >&2; return 1 ;;
        esac
    done
    _notes_daily "$day" "$dry"; case $? in 0) ;; 2) return 0 ;; *) return 1 ;; esac
    list=$(_notes_list "$day") || return 1
    keep=$(printf '%s\n' "$list" | while IFS= read -r rel; do [ -n "$rel" ] && basename "$rel"; done)

    # get the GitHub edits first, so that the archived versions are the latest
    [ -z "$dry" ] && { git -C "$NOTES_REPO" pull -q --rebase || { echo "notes: pull failed" >&2; return 1; }; }

    # notes created on GitHub are kept: notes_sync imports them
    new=$(_notes_new)
    [ -n "$new" ] && printf '%s\n' "$new" |
        sed 's/^/  ! keeping new note (run notes_sync to import it): /' >&2

    todo=$(find "$NOTES_REPO" -mindepth 1 -maxdepth 1 -type f -name '*.md' ! -name 'README.md' | sort |
        while IFS= read -r name; do
            name=$(basename "$name")
            printf '%s\n%s\n' "$keep" "$new" | grep -qxF -- "$name" || printf '%s\n' "$name"
        done)

    if [ -z "$todo" ]; then echo "== nothing to archive"; return 0; fi
    echo "== to move to _archives/ (keeping the notes of $day):"
    printf '%s\n' "$todo" | sed 's/^/     /'
    [ -n "$dry" ] && { echo "== dry run, nothing moved"; return 0; }

    mkdir -p "$NOTES_REPO/_archives"
    while IFS= read -r name; do
        mv -f "$NOTES_REPO/$name" "$NOTES_REPO/_archives/$name" && n=$((n + 1))
    done <<EOF
$todo
EOF
    echo "== $n note(s) archived"
    _notes_commit_push "archive notes not in $day" && _notes_push
}
