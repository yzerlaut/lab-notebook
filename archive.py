import datetime, pathlib
import sys, os
import git # pip install gitpython

ARCHIVE = '_archives'

repo = git.Repo(os.path.dirname(__file__))

# if os.path.isfile(sys.argv[-1]):
if True:

    timestamp = \
        datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

    pathlib.Path.mkdir(os.path.join(ARCHIVE,
                    datetime.datetime.now().strftime("%Y")))

    folder = os.path.join(ARCHIVE,
                          datetime.datetime.now().strftime("%Y"),
                          datetime.datetime.now().strftime("%B"))

    pathlib.Path.mkdir(folder, exist_ok=True)
    
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
    repo.remotes.origin.push()
