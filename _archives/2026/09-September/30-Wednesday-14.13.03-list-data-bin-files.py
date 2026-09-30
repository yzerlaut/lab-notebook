"""
List all `data.bin` datafiles in the raw data folder

usage:
    python list-data-bin-files.py
    python list-data-bin-files.py --root "\\\\iss\\rebola\\raw_data" --output data-bin-list.txt
"""
import os, argparse

ROOT = r'\\iss\rebola\raw_data'

def find_data_bin(root, filename='data.bin'):
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        if filename in filenames:
            files.append(os.path.join(dirpath, filename))
    return sorted(files)

if __name__=='__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default=ROOT)
    parser.add_argument('--filename', default='data.bin')
    parser.add_argument('--output', default='',
                        help='optional text file to save the list')
    args = parser.parse_args()

    files = find_data_bin(args.root, args.filename)

    for f in files:
        print(f)
    print('\n--> found %i "%s" files in "%s"' % (len(files), args.filename, args.root))

    if args.output:
        with open(args.output, 'w') as o:
            o.write('\n'.join(files))
        print('    list saved as "%s"' % args.output)
