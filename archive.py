import datetime
import sys, os, shutil
import git # pip install gitpython

repo = git.Repo(os.path.dirname(__file__))

if os.path.isfile(sys.argv[-1]):
    timestamp = \
        datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    print(sys.argv[-1])
    filename = '%s-%s' %(timestamp,
                         os.path.basename(sys.argv[-1]))
    shutil.copy(sys.argv[-1], 
                os.path.join('_archives', filename))
    print("""
        archiving '%s' as:
            %s 
          """ % (sys.argv[-1],
                 os.path.join('_archives', filename)))
    repo.index.add(os.path.join('_archives', filename))
    repo.index.commit('add '+filename) 
    repo.remotes.origin.push()
