#!/usr/bin/env bash
# Builds all the visual-stimulation protocols of Sally, in parallel
#   (movies in ~/Documents/Notebook/Ressources/visualStim-protocols/Sally/, see build_movie.py)
#
# usage (from anywhere):
#     bash build-visualStim-protocols-Sally/run_all.sh                    # all protocols, 4 at a time
#     bash build-visualStim-protocols-Sally/run_all.sh -j 6               # 6 at a time
#     bash build-visualStim-protocols-Sally/run_all.sh -j 1               # one after the other
#     bash build-visualStim-protocols-Sally/run_all.sh rough_mapping uniform_screens   # some of them
#
# - runs with the uv environment of the repository root (.venv)
# - the output of each protocol goes to logs/<protocol>.log (in this folder),
#     follow one with: tail -f build-visualStim-protocols-Sally/logs/<protocol>.log
# - a failing protocol does not stop the others, a summary is printed at the end
# - the two image-ID tasks share the morph images (images/ + images.csv in the output folder):
#     they run one after the other, in the same parallel slot
# [!!] existing protocol folders of the same name are replaced

FOLDER="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$FOLDER")"
LOGS="$FOLDER/logs"

NJOBS=4
if [ "$1" = "-j" ]; then
    NJOBS=$2
    shift 2
fi

PROTOCOLS=(
    # longest first: they start right away
    neurometricTask_imageID
    neurometricTaskwithOpto_imageID
    fourDimOfVisualInfo_20trials
    mixedTuningContrastwithOpto
    neurometricTask_gratingAngle
    neurometricTask_imageTiming
    neurometricTaskwithOpto_imageTiming
    bg_luminance_opto
    rough_mapping
    precise_mapping
    flashed_stimuli
    uniform_screens
)
if [ $# -gt 0 ]; then
    PROTOCOLS=("${@%.py}")
fi

# protocols that must run one after the other (shared files): grouped in one job
SEQUENTIAL="neurometricTask_imageID neurometricTaskwithOpto_imageID"

JOBS=()   # each job: space-separated protocols, run in sequence
GROUP=""
for p in "${PROTOCOLS[@]}"; do
    if [[ " $SEQUENTIAL " == *" $p "* ]]; then
        GROUP="$GROUP $p"
    else
        JOBS+=("$p")
    fi
done
[ -n "$GROUP" ] && JOBS=("${GROUP# }" "${JOBS[@]}")

run_protocol() {
    # $1: protocol -> logs/$1.log, and its exit code + duration in logs/$1.status
    local t0=$SECONDS
    (cd "$FOLDER" && uv run --project "$ROOT" python "$1.py") > "$LOGS/$1.log" 2>&1
    echo "$? $(( SECONDS-t0 ))" > "$LOGS/$1.status"
}

run_job() {
    for p in $1; do
        echo "  [start] $p"
        run_protocol "$p"
        read code dt < "$LOGS/$p.status"
        if [ "$code" -eq 0 ]; then
            echo "  [ok]    $p  ($(( dt/60 ))min$(( dt%60 ))s)"
        else
            echo "  [!!]    $p  FAILED, see logs/$p.log"
        fi
    done
}

mkdir -p "$LOGS"
for p in "${PROTOCOLS[@]}"; do rm -f "$LOGS/$p.log" "$LOGS/$p.status"; done

echo "=================================================================="
echo "  ${#PROTOCOLS[@]} protocols, $NJOBS in parallel (logs in $LOGS)"
echo "=================================================================="
START=$SECONDS
for job in "${JOBS[@]}"; do
    # wait for a free slot
    while [ "$(jobs -pr | wc -l)" -ge "$NJOBS" ]; do
        sleep 1
    done
    run_job "$job" &
done
wait

echo
echo "=================================================================="
echo "  done in $(( (SECONDS-START)/60 ))min$(( (SECONDS-START)%60 ))s"
FAILED=0
for p in "${PROTOCOLS[@]}"; do
    if [ -f "$LOGS/$p.status" ] && read code dt < "$LOGS/$p.status" && [ "$code" -eq 0 ]; then
        echo "  [ok]  $p  ($(( dt/60 ))min$(( dt%60 ))s)"
    else
        echo "  [!!]  $p  FAILED, see logs/$p.log"
        FAILED=1
    fi
done
echo "=================================================================="
exit $FAILED
