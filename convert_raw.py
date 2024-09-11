import matplotlib.pyplot as plt
import numpy as np

path = 'first_fringes.raw'

A = np.fromfile("first_fringes.raw", dtype='uint8', sep="")

px = 1920
py = 1200

A = np.reshape(A, (1200,1920, 1))

plt.imshow(A, cmap="gray", origin='lower')
plt.xlabel('px')
plt.ylabel('py')
plt.show()
