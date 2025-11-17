import itertools, os, pathlib, shutil

def single_protocol(spatial, temporal, contrast, size, realisation):

    if spatial=='high':
        if realisation==1:
            image = 0
        elif realisation==2:
            image = 3
    else:
        if realisation==1:
            orientation = 0
        elif realisation==2:
            orientation = 90

    if (spatial=='high') and (temporal=='high'):
        protocol = """{
  "Presentation": "Single-Stimulus",
  "Stimulus": "natural-image+VSE",
  "presentation-prestim-period": 1.0,
  "presentation-interstim-period": 1.0,
  "presentation-duration": 4.0,
  "units": "deg",
  "_______________________________________________________________________1":0,
  "min-saccade-duration": 0.2,
  "max-saccade-duration": 1.0,
  "saccade-amplitude": 50.0,
  "seed": 0,
  "contrast": %.2f,
  "radius": %.2f,
  "Image-ID": %i,
  "_______________________________________________________________________2":0,
  "Screen": "Dell-2020-low-resolution"
}""" % (contrast, size, image)
    elif (spatial=='high') and (temporal=='low'):
        protocol = """{
  "Presentation": "Single-Stimulus",
  "Stimulus": "natural-image",
  "presentation-prestim-period": 1.0,
  "presentation-interstim-period": 1.0,
  "presentation-duration": 2.0,
  "units": "deg",
  "_______________________________________________________________________1":0,
  "contrast": %.2f,
  "radius": %.2f,
  "Image-ID": %i,
  "_______________________________________________________________________2":0,
  "Screen": "Dell-2020-low-resolution"
}""" % (contrast, size, image)
    elif (spatial=='low') and (temporal=='low'):
        protocol = """{
  "Presentation": "Single-Stimulus",
  "Stimulus": "grating",
  "presentation-duration": 2.0,
  "presentation-prestim-period": 1.0,
  "presentation-interstim-period": 1.0,
  "units": "deg",
  "_______________________________________________________________________1":0,
  "contrast": %.2f,
  "radius": %.2f,
  "spatial-freq":0.04,
  "angle":%.2f,
  "_______________________________________________________________________2":0,
  "Screen": "Dell-2020-low-resolution"
}""" % (contrast, size, orientation)
    elif (spatial=='low') and (temporal=='high'):
        protocol = """{
  "Presentation": "Single-Stimulus",
  "Stimulus": "grating-VSE",
  "presentation-duration": 4.0,
  "presentation-prestim-period": 1.0,
  "presentation-interstim-period": 1.0,
  "units": "deg",
  "_______________________________________________________________________1":0,
  "min-saccade-duration": 0.2,
  "max-saccade-duration": 1.0,
  "saccade-amplitude": 50.0,
  "seed": 0,
  "contrast": %.2f,
  "radius": %.2f,
  "angle":%.2f,
  "_______________________________________________________________________2":0,
  "Screen": "Dell-2020-low-resolution"
}""" % (contrast, size, orientation)
    else:
        print('protocol not recognized !!')
        protocol = ''

    return protocol 

i = 1 # protocol counter

pathlib.Path('./protocols').mkdir(exist_ok=True)

for spatial, temporal, contrast, size, realisation in itertools.product(\
   ['low', 'high'], ['low', 'high'], [0.2, 1.0], [25., 300.], [1]):
    protocol = single_protocol(spatial, temporal, contrast, size, realisation) 
    if protocol!='':
        with open('temp.json', 'w') as f:
            f.write(protocol)
        os.system('cd physion/src; python -m physion.visual_stim.build ../../temp.json --mp4; cd ../..')
        os.rename('movies/temp/movie.mp4', 'protocols/S-%s_T-%s-C-%.1f_R-%i_#%i.mp4'\
                    % (spatial, temporal, contrast, size, realisation))
    i += 1

os.remove('temp.json')
shutil.rmtree('./movies')
