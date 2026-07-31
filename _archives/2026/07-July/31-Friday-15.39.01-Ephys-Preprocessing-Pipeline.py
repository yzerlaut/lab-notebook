# %%
import os
import spikeinterface.sorters as ss
import spikeinterface.full as si
import spikeinterface.exporters as sexp
import spikeinterface.widgets as sw

##
# sudo -i # to turn root ()
# /home/user/miniforge3/bin/python /home/user/lab-notebook/sally/Ephys-Preprocessing-Pipeline.py



# 1) finish to run the transfer:
# rsync -avhP --exclude "*.bin" ~/DATA/Sally/2026_04_24 user@10.0.0.1:DATA/Sally

rec = si.read_openephys(\
    os.path.join(\
        # os.path.expanduser('~'),
            '/media/user/DATA2/2026-06-09_17-24-45'),
                stream_name='Record Node 101#OneBox-100.ProbeA')

# 2) subselect channels nicely here 
#   - remove bad channels
#   - focus on interesting part of the probe
rec = rec.select_channels(rec.get_channel_ids()[::8])

# here just for speed
#rec = rec.frame_slice(100000, 1100000) # 10M frames

# 4) here add the compression if possible !
#   ideally we would only store this...
rec = rec.save(folder='/tmp/test',
                   overwrite=True)

# if already existing, just do: "rm -rf /tmp/test"

# %%
# 5) run the spike sorting through docker
# https://spikeinterface.readthedocs.io/en/stable/modules/sorters.html#running-sorters-in-docker-singularity-containers 
sorting = ss.run_sorter(sorter_name='kilosort4', 
                        recording=rec,
                        verbose=True,
                        docker_image=True)

analyzer = si.create_sorting_analyzer(\
        sorting=sorting,
        recording=rec,
        format='binary_folder',
        overwrite=True,
        folder='analyzer_binary')
        
extensions_to_compute = [
    "random_spikes",
    "waveforms",
    "noise_levels",
    "templates",
    "spike_amplitudes",
    "unit_locations",
    "spike_locations",
    "correlograms",
    "template_similarity"
]

extension_params = {
    "unit_locations": {"method": "center_of_mass"},
    "spike_locations": {"ms_before": 0.1},
    "correlograms": {"bin_ms": 0.1},
    "template_similarity": {"method": "cosine_similarity"}
}

analyzer.compute(extensions_to_compute,
                 extension_params=extension_params)

if os.path.isdir("./phy_folder"):
    os.path.rmdir("./phy_folder")

sexp.export_to_phy(analyzer, "./phy_folder",
                    verbose=True)

# spike interface quickstart:
# https://spikeinterface.readthedocs.io/en/stable/get_started/quickstart.html
