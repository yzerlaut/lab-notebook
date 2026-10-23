import datetime, pathlib
import os, shutil, argparse
import git # pip install gitpython

ARCHIVE = '_archives'

IGNORE = shutil.ignore_patterns('__pycache__', '*.pyc',
                                '.ipynb_checkpoints', '.DS_Store')

def get_archive_folder_and_timestamp():

    timestamp = \
        datetime.datetime.now().strftime("%d-")+\
        datetime.datetime.now().strftime("%A-")+\
        datetime.datetime.now().strftime("%H.%M.%S")

    folder = os.path.join(ARCHIVE,
                          datetime.datetime.now().strftime("%Y"),
                          datetime.datetime.now().strftime("%m-%B"))

    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)

    return folder, timestamp


def commit_and_push(paths, message):

    repo.index.add(paths)
    repo.index.commit(message)
    try:
        repo.remotes.origin.push()
        print('  [ok] successfully pushed')
    except BaseException as be:
        print('  [xx] not pushed ...')


def archive_file(args, test=False):

    folder, timestamp = get_archive_folder_and_timestamp()
    
    filename = '%s-%s' %(timestamp,
                         os.path.basename(args.filename))

    if not test:
        shutil.copy(args.filename,
                    os.path.join(folder, filename))

    print("""
        archiving '%s' as:
            %s 
          """ % (args.filename,
                 os.path.join(folder, filename)))

    if not test:
        commit_and_push([os.path.join(folder, filename)],
                        'add '+filename)


def archive_folder(args, test=False):
    """
    archive a whole folder of scripts as a single timestamped folder:
        _archives/YYYY/MM-Month/DD-Day-HH.MM.SS-folder-name/
    """

    folder, timestamp = get_archive_folder_and_timestamp()

    foldername = '%s-%s' %(timestamp,
                           os.path.basename(args.filename))
    target = os.path.join(folder, foldername)

    if not test:
        shutil.copytree(args.filename, target, ignore=IGNORE)

    print("""
        archiving the folder '%s' as:
            %s/ 
          """ % (args.filename, target))

    if not test:
        files = [os.path.join(root, f)\
                    for root, _, fs in os.walk(target) for f in fs]
        for f in sorted(files):
            print('            - %s' % os.path.relpath(f, target))
        commit_and_push(files, 'add '+foldername)


def unarchive_file(args, test=False):

    filename =  os.path.basename(args.filename).split('.')[-2][3:]+\
            '.'+os.path.basename(args.filename).split('.')[-1]

    print("""
        bringing back the archive: '%s' 
            as:   ./%s 
          """ % (args.filename,
                 filename))

    if not test:
        shutil.copy(args.filename,
                    os.path.join('.', filename))

def unarchive_folder(args, test=False):

    # strip the "DD-Day-HH.MM.SS-" timestamp
    foldername = os.path.basename(args.filename).split('.', 2)[-1][3:]

    print("""
        bringing back the archived folder: '%s' 
            as:   ./%s/
          """ % (args.filename,
                 foldername))

    if not test:
        shutil.copytree(args.filename,
                        os.path.join('.', foldername),
                        ignore=IGNORE,
                        dirs_exist_ok=True)


def is_in_archive(path):
    archive = os.path.abspath(ARCHIVE)
    return os.path.commonpath([os.path.abspath(path), archive])==archive

if __name__=='__main__':

    repo = git.Repo(os.path.dirname(__file__))

    parser=argparse.ArgumentParser(description="""

        archive a given script (or folder of scripts) in the lab notebook

        python archive.py your-script.py
        python archive.py your-folder-of-scripts/

        N.B. 
            [de-archive] TBD

                                   """,
            formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("filename")
    parser.add_argument('-d', "--debug", 
                        action="store_true")

    args = parser.parse_args()
    args.filename = os.path.normpath(args.filename) # drop trailing "/"
      
    if os.path.isdir(args.filename):

        if is_in_archive(args.filename):
            unarchive_folder(args, test=args.debug)
        else:
            archive_folder(args, test=args.debug)

    elif os.path.isfile(args.filename):

        if len(args.filename.split('.'))>=4:
            unarchive_file(args, test=args.debug)
        else:
            archive_file(args, test=args.debug)


