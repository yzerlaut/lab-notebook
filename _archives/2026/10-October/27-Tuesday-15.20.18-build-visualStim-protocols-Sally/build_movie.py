import os

def build_movie(X, name='temp', rm=True):
    """Common function to build a movie from a JSON configuration."""
    with open('%s.json' % name, 'w') as f:
        f.write(X)
    os.system('cd physion/src; python -m physion.visual_stim.build ../../%s.json; cd ../..' % name)
    if rm:
        os.remove('%s.json' % name)
