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
import sys, os, shutil, stat, argparse, time
sys.path += [os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          'physion', 'src')]
import numpy as np
import h5py
from PIL import Image

from physion.utils.files import get_files_with_extension
from physion.imaging.bruker.xml_parser import bruker_xml_parser
from physion.utils.compression.h5 import tiffs_to_h5
from physion.utils.progressBar import printProgressBar

ROOT_FOLDER = '//iss/rebola/raw_data/cibele'
H5_KEY = 'data'


def find_TSeries_folders(root):
    """ all folders named "TSeries-..." (no search inside them) """
    FOLDERS = []
    for folder, subdirs, _ in os.walk(root):
        for d in list(subdirs):
            if d.startswith('TSeries-'):
                FOLDERS.append(os.path.join(folder, d))
                subdirs.remove(d) # do not walk inside TSeries folders
    return sorted(FOLDERS)


def is_tiff(filename):
    return filename.lower().endswith(('.tif', '.tiff'))


def build_conversion_plan(TS_folder, h5_folder):
    """
    returns a list of (h5_file, tiff_files)
        with the same naming than physion.utils.compression.h5.convert_to_h5
    """
    xml_file = get_files_with_extension(TS_folder, extension='.xml')[0]
    xml = bruker_xml_parser(xml_file)

    plan = []
    for chan in xml['channels']:
        FILES = np.array(xml[chan]['tifFile'])
        depth_index = np.array(xml[chan]['depth_index'])
        for p in np.unique(depth_index):
            plan.append((os.path.join(h5_folder, '%s-plane%i.h5' %\
                                            (chan.replace(' ','-'), p)),
                         list(FILES[depth_index==p])))
    return plan


def check_tiff_coverage(TS_folder, plan):
    """
    returns the sets of:
        - "missing" tiffs: in the xml but not in the folder
        - "unplanned" tiffs: in the folder but not in the xml
    """
    planned = set(f for _, tiffs in plan for f in tiffs)
    present = set(f for f in os.listdir(TS_folder) if is_tiff(f))
    return planned-present, present-planned


def verify_h5(TS_folder, tiff_files, h5_file, batch_size=32):
    """ pixel-exact comparison of every h5 frame with its tiff """
    try:
        with h5py.File(h5_file, 'r') as f:
            if H5_KEY not in f:
                return 'no "%s" key' % H5_KEY
            dset = f[H5_KEY]
            if dset.shape[0]!=len(tiff_files):
                return '%i frames in h5 vs %i tiffs' % (dset.shape[0],
                                                       len(tiff_files))
            n = len(tiff_files)
            for i0 in range(0, n, batch_size):
                frames = dset[i0:i0+batch_size]
                for frame, tiff in zip(frames, tiff_files[i0:i0+batch_size]):
                    ref = np.array(Image.open(os.path.join(TS_folder, tiff)))
                    if (ref.shape!=frame.shape) or\
                            (not np.array_equal(ref, frame)):
                        print()
                        return 'frame mismatch with "%s"' % tiff
                i1 = min([n, i0+batch_size])
                printProgressBar(i1, n, prefix='    checking h5:',
                                 suffix='(%i/%i frames)' % (i1, n))
    except BaseException as be:
        print()
        return 'unreadable h5 (%s)' % be
    return None # no error


def copy_non_tiff_content(TS_folder, h5_folder):
    """ copy xml, env, References/, ... and check the copies on file sizes """
    errors = []
    for item in os.listdir(TS_folder):
        src, dst = os.path.join(TS_folder, item), os.path.join(h5_folder, item)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
            pairs = [(os.path.join(root, f),
                      os.path.join(dst, os.path.relpath(root, src), f))\
                        for root, _, files in os.walk(src) for f in files]
        elif not is_tiff(item):
            shutil.copy2(src, dst)
            pairs = [(src, dst)]
        else:
            continue
        for s, d in pairs:
            if (not os.path.isfile(d)) or\
                    (os.path.getsize(s)!=os.path.getsize(d)):
                errors.append('copy failed for "%s"' % s)
    return errors


def remove_readonly(func, path, _):
    """ on network shares, some files can be read-only """
    os.chmod(path, stat.S_IWRITE)
    func(path)


def process_TSeries(TS_folder, dry_run=False, delete=True):

    h5_folder = os.path.join(os.path.dirname(TS_folder),
                    os.path.basename(TS_folder).replace('TSeries', 'h5', 1))
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
