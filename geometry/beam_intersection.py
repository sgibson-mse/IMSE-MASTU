import numpy as np
import matplotlib.pyplot as plt
import pickle

### solve a quadratic equation
def solvequad(A, B, C):
    root1 = (-B + np.sqrt(B**2 - (4. * A * C))) / (2. * A)
    root2 = (-B - np.sqrt(B**2 - (4. * A * C))) / (2. * A)
    return max(root1, root2)

### return element index from array closest to wanted value
def find_nearest(arr, val):
    return np.abs(arr - val).argmin()

### radius of vessel wall, SS beam port location, metres
radiusWall = 2.033
### radius of centre column, metres
radiusCC = 0.260841



### information for xspaceSS, the xrange the SS beam acts over
x0 = 0.543 # metres
x1 = 0.862 # metres
xn = 1001 # number points for xplot
xlen = int(((x1 - x0) * 1e3) + 2)
xplot = np.linspace(-radiusWall, radiusWall, xn)

### load beam data
with open('beam_geometry_data.pkl', 'rb') as handle:
    data =  pickle.load(handle)
### SS beam data
ss = data['ss_beam']
beamSS = ss['axis']
sourceSS = ss['src'] / 100.
### gradient of line describing SS
mSS = beamSS[1] / beamSS[0]
### intercept of line describing SS
CSS = sourceSS[1] - (sourceSS[0] *
      beamSS[1] / beamSS[0])
### y co-ordinates of SS beam
ySS = mSS * xplot + CSS

### space SS beam acts over
xspaceSS = np.linspace(x0, x1, xlen)
yspaceSS = mSS * xspaceSS + CSS
xstep = np.diff(xspaceSS).mean()
### radius of the SS beam
RspaceSS = np.sqrt(xspaceSS**2 + yspaceSS**2)
### lower half of beam, before tangency point
boo = yspaceSS < 0.
Rbeam = np.sqrt(xspaceSS[boo]**2 + yspaceSS[boo]**2)

fig, ax = plt.subplots(1, 1)

### ticks on the SS colourbar
SSticks = np.arange(0.7, 2.09, 0.1)

### adding beams
sc=ax.scatter(xspaceSS, yspaceSS, c=RspaceSS, marker='o',
              vmin=0.7, vmax=RspaceSS.max(),
              cmap=plt.cm.Purples, label='SS beam', zorder=2)
fig.colorbar(sc, ax=ax, label='South-south beam radius (m)', ticks=SSticks)



### rest of plotting
ax.grid(zorder=1)
ax.legend(fancybox=True, framealpha=1, loc='upper center', ncol=2)
ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.set_aspect('equal')
ax.set_xlabel('x (m)')
ax.set_ylabel('y (m)')
plt.show()


