import datetime, pathlib
import sys, os, shutil, argparse
import git # pip install gitpython

ARCHIVE = '_archives'

repo = git.Repo(os.path.dirname(__file__))

parser=argparse.ArgumentParser(description="""

    archive a given script in the lab notebook

    python archive.py your-script.py

    N.B. 
        [de-archive] TBD

                               """,
                                formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument("filename")

args = parser.parse_args()
  
if os.path.isfile(args.filename):

    timestamp = \
        datetime.datetime.now().strftime("%d-")+\
        datetime.datetime.now().strftime("%A-")+\
        datetime.datetime.now().strftime("%H:%M:%S")

    pathlib.Path(os.path.join(ARCHIVE,
        datetime.datetime.now().strftime("%Y"))).mkdir(\
                                                exist_ok=True)

    folder = os.path.join(ARCHIVE,
                          datetime.datetime.now().strftime("%Y"),
                          datetime.datetime.now().strftime("%B"))

    pathlib.Path(folder).mkdir(exist_ok=True)
    
    filename = '%s-%s' %(timestamp,
                         os.path.basename(sys.argv[-1]))

    shutil.copy(sys.argv[-1], 
                os.path.join(folder, filename))

    print("""
        archiving '%s' as:
            %s 
          """ % (sys.argv[-1],
                 os.path.join(folder, filename)))

    repo.index.add(os.path.join(folder, filename))
    repo.index.commit('add '+filename) 
    try:
        repo.remotes.origin.push()
        print('  [ok] successfully pushed')
    except BaseException as be:
        print('  [xx] not pushed ...')

