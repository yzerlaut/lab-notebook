# %%
import spikeinterface.sorters as ss
import spikeinterface.full as si
rec = si.read_openephys(\
    os.path.join(\
        os.path.expanduser('~'),
            'DATA/2026_04_24/2026-04-24_12-23-16'),
                stream_name='Record Node 101#OneBox-100.ProbeA')

# %%
ss.get_default_sorter_params('kilosort4')
# %%
ss.installed_sorters()
# %%
ss.install_package_in_container?
# %%
