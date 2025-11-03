# %%
import os, sys , shutil 
import multiprocessing
import numpy as np

sys.path += ['./physion/src']
from physion.utils.parallel import process_datafiles

def example_func2(filename, i, output_folder):
    print(\
        os.path.join(output_folder,
                        '%i-%s.npy' % (i, filename)))

if __name__=='__main__':

    filenames = ['data-%i.nwb' % i for i in range(100, 150)]
    process_datafiles(example_func2,
                      filenames,
                      './temp/')