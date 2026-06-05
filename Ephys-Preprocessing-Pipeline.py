# %%
import spikeinterface.sorters as ss
import spikeinterface.full as si

rec = si.read_openephys(\
    os.path.join(\
        os.path.expanduser('~'),
            'DATA/2026_04_24/2026-04-24_12-23-16'),
                stream_name='Record Node 101#OneBox-100.ProbeA')

rec = rec.select_channels(rec.get_channel_ids()[::8])
rec = rec.frame_slice(1000000, 1300000) # 300k frames
rec = rec.save(folder='/tmp')

# %%
# %%
sorting = ss.run_sorter(sorter_name='kilosort4', 
                        recording=rec,
                        folder="/tmp/", 
                        docker_image=True)

