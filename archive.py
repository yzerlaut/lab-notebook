import datetime
import sys, os, shutil
import git # pip install gitpython

path = os.path.join(os.path.dirname(__file__),
                    os.path.pardir)
repo = git.Repo(path)

if os.path.isfile(sys.argv[-1]):
    timestamp = \
        datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    print(sys.argv[-1])
    filename = '%s-%s' %(timestamp,
                         os.path.basename(sys.argv[-1]))
    shutil.copy(sys.argv[-1], 
                os.path.join('archive', filename))
    repo.index.add(os.path.join('archive', filename))
    repo.index.commit('add '+filename) 
    repo.remotes.origin.push()
