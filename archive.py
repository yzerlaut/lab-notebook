import datetime, pathlib
import sys, os, shutil
import git # pip install gitpython

ARCHIVE = '_archives'

repo = git.Repo(os.path.dirname(__file__))

# if os.path.isfile(sys.argv[-1]):
if True:

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
        print('  successfully pushed')
    except BaseException as be:
        print('  not pushed ...')

