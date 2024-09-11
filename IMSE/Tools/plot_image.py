from Demodulate_TSSSH import load_image
import matplotlib.pyplot as plt

filename = '/home/sgibson/MAST-U/IMSE/IMSE/Tools/images/imse_2d_mastu_grasshopper_hm07c_f50mm_state1_100kAECCD.hdf'
image = load_image(filename)

plt.figure()
plt.imshow(image)
plt.colorbar()
plt.show()
