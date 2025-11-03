import datetime, pathlib
import os, shutil, argparse
import git # pip install gitpython

ARCHIVE = '_archives'

def archive_file(args, test=False):

    timestamp = \
        datetime.datetime.now().strftime("%d-")+\
        datetime.datetime.now().strftime("%A-")+\
        datetime.datetime.now().strftime("%H.%M.%S")

    pathlib.Path(os.path.join(ARCHIVE,
        datetime.datetime.now().strftime("%Y"))).mkdir(\
                                                exist_ok=True)

    folder = os.path.join(ARCHIVE,
                          datetime.datetime.now().strftime("%Y"),
                          datetime.datetime.now().strftime("%m-%B"))

    pathlib.Path(folder).mkdir(exist_ok=True)
    
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
        repo.index.add(os.path.join(folder, filename))
        repo.index.commit('add '+filename) 
        try:
            repo.remotes.origin.push()
            print('  [ok] successfully pushed')
        except BaseException as be:
            print('  [xx] not pushed ...')


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

if __name__=='__main__':

    repo = git.Repo(os.path.dirname(__file__))

    parser=argparse.ArgumentParser(description="""

        archive a given script in the lab notebook

        python archive.py your-script.py

        N.B. 
            [de-archive] TBD

                                   """,
            formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("filename")
    parser.add_argument('-d', "--debug", 
                        action="store_true")

    args = parser.parse_args()
      
    if os.path.isfile(args.filename):

        if len(args.filename.split('.'))>=4:
            unarchive_file(args, test=args.debug)
        else:
            archive_file(args, test=args.debug)


