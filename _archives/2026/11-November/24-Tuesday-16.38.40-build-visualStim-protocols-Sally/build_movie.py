import os
import sys
import shutil
import subprocess
import tempfile

# where the protocols (json files) and the built movies are created
OUTPUT_FOLDER = os.path.expanduser(
    '~/Documents/Notebook/Ressources/visualStim-protocols/Sally')

# physion sources (the relative paths of the protocols, e.g. "NI_FOLDER", start there)
PHYSION_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'physion', 'src')

# folder of Natural Images from the Allen Dataset
NI_FOLDER = os.path.expanduser(
    '~/Documents/Notebook/Ressources/visualStim-protocols/Natural-Images-Allen')


def build_movie(X, name='temp', rm=True, subprotocols={}):
    """
    Common function to build a movie from a JSON configuration.

    X:            json of the protocol
    subprotocols: {filename: json} of the sub-protocols of a multiprotocol,
                    written next to the protocol (the "Protocol-i" filenames of X)
    rm:           remove the json files after the build, otherwise they are kept in
                    OUTPUT_FOLDER/<name>-json/
                    (the built protocol folder keeps all the parameters in "protocol.json")
    """
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    files = {'%s.json' % name: X, **subprotocols}

    # the json files are written in a folder of this build only
    #    (protocols built in parallel can have sub-protocols with the same file names),
    # the movies are built on the local disk and moved once complete
    #    (ffmpeg writing directly in the OneDrive folder can fail: "Operation timed out")
    with tempfile.TemporaryDirectory() as json_folder,\
            tempfile.TemporaryDirectory() as build_folder:
        for filename, content in files.items():
            with open(os.path.join(json_folder, filename), 'w') as f:
                f.write(content)
        try:
            subprocess.run([sys.executable, '-m', 'physion.visual_stim.build',
                            os.path.join(json_folder, '%s.json' % name),
                            '-o', build_folder],
                           cwd=PHYSION_SRC, check=True)
        finally:
            if not rm:
                kept = os.path.join(OUTPUT_FOLDER, '%s-json' % name)
                shutil.rmtree(kept, ignore_errors=True)
                shutil.copytree(json_folder, kept)
                print(' --> json files kept in: "%s"' % kept)

        protocol_folder = os.path.join(OUTPUT_FOLDER, name)
        if os.path.isdir(protocol_folder):
            shutil.rmtree(protocol_folder)
        shutil.move(os.path.join(build_folder, name), protocol_folder)
        print(' --> moved to: "%s"' % protocol_folder)
