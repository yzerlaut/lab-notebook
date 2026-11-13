import os
import sys
import subprocess

# where the protocols (json files) and the built movies are created
OUTPUT_FOLDER = os.path.expanduser(
    '~/Library/CloudStorage/OneDrive-ICM/Lab-Notebook/visualStim-protocols/Sofia')

# natural images of the protocols: 1280x720 copies (see prepare_images.py)
NI_FOLDER = os.path.join(OUTPUT_FOLDER, 'NI_bank')

# physion sources (the relative paths of the protocols, e.g. "NI_FOLDER", start there)
PHYSION_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'physion', 'src')


def build_movie(X, name='temp', rm=True, subprotocols={}):
    """
    Common function to build a movie from a JSON configuration.

    X:            json of the protocol
    subprotocols: {filename: json} of the sub-protocols of a multiprotocol,
                    written next to the protocol (the "Protocol-i" filenames of X)
    rm:           remove the json files after the build
                    (the built protocol folder keeps all the parameters in "protocol.json")
    """
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    files = {'%s.json' % name: X, **subprotocols}
    for filename, content in files.items():
        with open(os.path.join(OUTPUT_FOLDER, filename), 'w') as f:
            f.write(content)

    subprocess.run([sys.executable, '-m', 'physion.visual_stim.build',
                    os.path.join(OUTPUT_FOLDER, '%s.json' % name),
                    '-o', OUTPUT_FOLDER],
                   cwd=PHYSION_SRC)

    if rm:
        for filename in files:
            os.remove(os.path.join(OUTPUT_FOLDER, filename))
