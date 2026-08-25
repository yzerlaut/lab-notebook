import os
import itertools

def build_protocol(image_id=0, 
                   saccades='fast',
                   contrast=1.0,
                   seed=1,
                   Nrepeat=60):

  if saccades=='fast':
      min_saccade_duration=0.2
      max_saccade_duration=0.6
      duration=5.
  else:
      min_saccade_duration=0.4
      max_saccade_duration=0.8
      duration=5.

  return """
{
            "Presentation": "Stimuli-Sequence",
            "Stimulus": "natural-image-VSE",
            "Screen": "LN-2screens",
            "presentation-duration": %.1f,
            "presentation-prestim-period": 5,
            "presentation-poststim-period": 5,
            "presentation-interstim-period": 15,
            "N-repeat": %i,
            "_______________________________________________________________________1":0,
            "saccade-amplitude":200.0, 
            "contrast": %.1f,
            "Image-ID": %i,
            "radius": 70,
            "min-saccade-duration":%.1f,
            "max-saccade-duration":%.1f,
            "x-center":45.0,
            "y-center":20.0,
            "seed": %i
}
""" % (duration, Nrepeat, contrast, image_id,
       min_saccade_duration, max_saccade_duration, seed)

P = build_protocol(1)
name='protocol'

# for image, speed, contrast, seed in itertools.product(\
#     [0, 1], ['fast', 'slow'], [0.5, 1.0], [1]):
for image, speed, contrast, seed in itertools.product(\
    [0], ['mid'], [0.7], [1]):
  filename = 'Plasticity-Im%i-%s-c%.1f-#%i.json' % (image+1, speed, contrast, seed)
  protocol = build_protocol(image, speed, contrast, seed+10.*image)
  with open(filename, 'w') as f:
    f.write(protocol)
  os.system('cd physion/src; python -m physion.visual_stim.build ../../%s ; cd ../..' % filename)
os.system('rm *.json')

