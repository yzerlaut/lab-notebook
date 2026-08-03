import os, sys

for dirpath, dirnames, _ in os.walk(sys.argv[-1]):

    if 'plane0' in dirnames:

        folder = os.path.join(dirpath, 'plane0')

        reg_outputs = np.load(os.path.join(folder, 'reg_outputs.npy')).item()
        detect_outputs = np.load(os.path.join(folder, 'detect_outputs.npy')).item()
        db = np.load(os.path.join(folder, 'db.npy')).item()
        settings = np.load(os.path.join(folder, 'settings.npy')).item()

        ops = {**db, **settings, **reg_outputs, **detect_outputs}
        np.save(os.path.join(folder, "ops.npy"), ops)