import numpy as np
import multiprocessing, time


cpus = multiprocessing.cpu_count()-1 # leaving 1 cpu for the rest

def print_task(filename='test'):
    print(filename)

filenames = ['file-%i' % i for i in range(143)]

nproc_tot = len(filenames)
nruns = int(nproc_tot/cpus)

if __name__ == "__main__":  # confirms that the code is under main function
    for r in range(nruns):
        i0 = r*nruns
        imax = np.min([i0+nruns, nproc_tot]) 
        print(' - running set of files %i:%i' % (i0, imax))

        procs = []
        # start the processes
        for i in range(i0,imax):
            proc = multiprocessing.Process(\
                                target=print_task, 
                                args=(filenames[i],))
            time.sleep(0.2)
            procs.append(proc)
            proc.start()

        # complete the processes
        for proc in procs:
            proc.join()