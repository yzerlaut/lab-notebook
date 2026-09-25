"""
Convert all "TSeries-xxx" folders (Bruker tiffs) found in a root folder
    into "h5-xxx" folders (one h5 file per channel and plane, key: "data"),
    and delete each TSeries folder once its conversion has been verified.

A TSeries folder is deleted only if:
    - every tiff of the folder is referenced in the Bruker xml file
    - every h5 file opens and matches its tiffs frame by frame (pixel-exact)
    - every non-tiff file/folder (xml, env, References/, ...) has been
        copied to the h5 folder (checked on file sizes)

usage:
    python Convert-TSeries-to-h5.py --dry-run   # only lists what would be done
    python Convert-TSeries-to-h5.py             # converts and deletes
    python Convert-TSeries-to-h5.py --no-delete # converts only
"""
import sys, os, shutil, argparse, time
sys.path += [os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          'physion', 'src')]

# the checks are shared with the 2P-conversion window of physion
from physion.utils.compression.h5 import tiffs_to_h5,\
        build_conversion_plan, check_tiff_coverage, verify_h5,\
        copy_non_tiff_content, remove_readonly
from physion.imaging.folders import find_TSeries_folders, compressed_folder

ROOT_FOLDER = '//iss/rebola/raw_data/cibele'
H5_KEY = 'data'


def process_TSeries(TS_folder, dry_run=False, delete=True):

    h5_folder = compressed_folder(TS_folder, 'h5')
    print('\n--> "%s" \n       to "%s"' % (TS_folder, h5_folder))

    plan = build_conversion_plan(TS_folder, h5_folder)
    for h5_file, tiffs in plan:
        print('     - %s : %i frames' % (os.path.basename(h5_file), len(tiffs)))

    missing, unplanned = check_tiff_coverage(TS_folder, plan)
    if len(missing)>0:
        print('     [!!] %i tiffs of the xml are missing (e.g. %s)' %\
                            (len(missing), sorted(missing)[0]))
        return 'SKIPPED (%i/%i tiffs missing), TSeries kept' %\
                    (len(missing), sum(len(t) for _, t in plan))
    blocking = []
    if len(unplanned)>0:
        blocking.append('%i tiffs are not referenced in the xml (e.g. %s)' %\
                            (len(unplanned), sorted(unplanned)[0]))
    for m in blocking:
        print('     [!!] %s' % m)

    if dry_run:
        return 'dry-run: would convert & ' +\
                    ('delete' if len(blocking)==0 else 'NOT delete')

    os.makedirs(h5_folder, exist_ok=True)

    # 1) conversion (skipped if a valid h5 exists from a previous run)
    errors = []
    for h5_file, tiffs in plan:
        if os.path.isfile(h5_file) and\
                verify_h5(TS_folder, tiffs, h5_file) is None:
            print('     [ok] %s already converted' % os.path.basename(h5_file))
            continue
        tic = time.time()
        tiffs_to_h5(TS_folder, tiffs, h5_file+'.tmp', dataset_key=H5_KEY)
        os.replace(h5_file+'.tmp', h5_file) # a h5 file is always complete
        # 2) verification
        error = verify_h5(TS_folder, tiffs, h5_file)
        if error is None:
            print('     [ok] %s written and verified (%.0fs)' %\
                    (os.path.basename(h5_file), time.time()-tic))
        else:
            errors.append('%s: %s' % (os.path.basename(h5_file), error))

    # 3) metadata & other files
    errors += copy_non_tiff_content(TS_folder, h5_folder)

    for e in errors:
        print('     [!!] %s' % e)
    if len(errors)>0:
        return 'FAILED, TSeries kept'
    if len(blocking)>0:
        return 'converted, but NOT deleted (%s)' % '; '.join(blocking)

    # 4) deletion
    if delete:
        shutil.rmtree(TS_folder, onerror=remove_readonly)
        print('     [ok] "%s" deleted' % TS_folder)
        return 'converted & deleted'
    else:
        return 'converted (not deleted)'


if __name__=='__main__':

    parser = argparse.ArgumentParser(description=__doc__,
                        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('folder', nargs='?', default=ROOT_FOLDER)
    parser.add_argument('--dry-run', action='store_true',
                        help='only list the folders and the conversion plan')
    parser.add_argument('--no-delete', action='store_true',
                        help='convert and verify, but keep the TSeries folders')
    args = parser.parse_args()

    FOLDERS = find_TSeries_folders(args.folder)
    print('\n %i TSeries folders found in "%s"' % (len(FOLDERS), args.folder))

    summary = {}
    for TS_folder in FOLDERS:
        try:
            summary[TS_folder] = process_TSeries(TS_folder,
                                                 dry_run=args.dry_run,
                                                 delete=not args.no_delete)
        except Exception as e:
            print('     [!!] %s' % e)
            summary[TS_folder] = 'FAILED (%s), TSeries kept' % e

    print('\n ============== SUMMARY ==============')
    for TS_folder, status in summary.items():
        print(' - %s : %s' % (TS_folder, status))
