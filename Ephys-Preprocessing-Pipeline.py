# %%
import os
import spikeinterface.sorters as ss
import spikeinterface.full as si

# 1) finish to run the transfer:
# rsync -avhP --exclude "*.bin" ~/DATA/Sally/2026_04_24 user@10.0.0.1:DATA/Sally

rec = si.read_openephys(\
    os.path.join(\
        os.path.expanduser('~'),
            'DATA/Sally/2026_04_24/2026-04-24_12-23-16'),
                stream_name='Record Node 101#OneBox-100.ProbeA')

# 2) subselect channels nicely here 
#   - remove bad channels
#   - focus on interesting part of the probe
rec = rec.select_channels(rec.get_channel_ids()[::8])

# here just for speed
rec = rec.frame_slice(1000000, 1300000) # 300k frames


# 4) here add the compression if possible !
#   ideally we would only store this...
rec = rec.save(folder='/tmp')

# %%
# 5) run the spike sorting through docker
# https://spikeinterface.readthedocs.io/en/stable/modules/sorters.html#running-sorters-in-docker-singularity-containers 
sorting = ss.run_sorter(sorter_name='kilosort4', 
                        recording=rec,
                        folder="/tmp/", 
                        docker_image=True)

# spike interface quickstart:
# https://spikeinterface.readthedocs.io/en/stable/get_started/quickstart.html