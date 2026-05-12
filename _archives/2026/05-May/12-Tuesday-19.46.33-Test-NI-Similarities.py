# %%
import numpy as np
from PIL import Image
import matplotlib.pylab as plt

def phase_scramble(img_array, alpha):  # alpha in [0,1]: 0=original, 1=fully scrambled

    # norm --> (center in 0, unit std)
    img_array = np.array(img_array, dtype=float)
    std = img_array.std()
    img_array -= img_array.mean()
    img_array /= std
    
    # FFT 
    F = np.fft.fft2(img_array)
    amplitude = np.abs(F)
    phase = np.angle(F)
    random_phase = np.random.uniform(-np.pi, np.pi, phase.shape)
    mixed_phase = (1 - alpha) * phase + alpha * random_phase
    F_new = amplitude * np.exp(1j * mixed_phase)
    output = np.real(np.fft.ifft2(F_new))

    return np.array(\
        np.clip(std*output+255/2., 0, 255), dtype=int)

def load_img(scene):
    return np.array(\
        Image.open("Natural-Images-Allen/%i.jpeg" % (scene+1)).convert('L'))

scene = 1
im = load_img(scene)
# %%
im2 = phase_scramble(im, 0.2)
im2
# %%
plt.imshow(im2, cmap=plt.cm.grey)
# %%
im
# %%
def mixture(im1, im2, alpha):  # alpha in [0,1]: 0=original, 1=fully scrambled

    return im1*(1-alpha/2.)+alpha*im2/2.,\
                im2*(1-alpha/2.)+alpha*im1/2.,


fig, AX = plt.subplots(2,2)

im1 = load_img(1)
im2 = load_img(2)
AX[0][0].imshow(im1, cmap=plt.cm.grey)
AX[0][1].imshow(im2, cmap=plt.cm.grey)

im1, im2 = mixture(im1, im2, 1.) 
AX[1][0].imshow(im1, cmap=plt.cm.grey)
AX[1][1].imshow(im2, cmap=plt.cm.grey)

# %%
F = np.fft.fft2(im1)
amplitude = np.abs(F)[300,:]
plt.loglog(amplitude)

# %%
im1.shape
# %%
