#!/usr/bin/env python
import numpy as np
from scipy.interpolate import interp2d
import pandas as pd

import matplotlib.pyplot as plt


from IMSE.Model.Light import Light
from IMSE.Model.Observer import Camera
from IMSE.Model.Optics import Lens
from IMSE.Model.Crystal import Crystal

def project_light(orientation):
    """
    :param lens: Lens object containing info about the focussing lens
    :param camera: Camera object, contains information about the camera sensor.
    :return:  Alpha (array): Angle light hits the sensor at, given that the rays exiting the crystal are non-axial
              Beta (Array): Azimuthal angle around the camera sensor
    """

    # Find out where the light will focus onto the sensor.
    # We need to do this first as the shift between ordinary/extraordinary rays exiting the crystal depends on
    # the incident angle when the optical axis is not parallel to the plate surface.

    alpha = np.arctan(np.sqrt((camera.xx)**2 + (camera.yy)**2)/(lens.focal_length))
    beta = np.arctan2(camera.yy,camera.xx)
    delta = beta - (orientation*np.pi/180.)

    return alpha, beta, delta

def make_image(delay_thickness, delay_cut_angle, delay_orientation, displacer_thickness, displacer_cut_angle, displacer_orientation, material_name, FLC):

    alpha, beta, delta = project_light(orientation=90)

    S_out = np.zeros((len(camera.x), len(camera.y), len(light.wavelength)))

    for i, wavelength in enumerate(light.wavelength):

        print(i, 'out of', len(light.wavelength))

        S0_interp = interp2d(light.x, light.y, light.S0[:,:,i], kind='linear')
        S1_interp = interp2d(light.x, light.y, light.S1[:,:,i], kind='linear')
        S2_interp = interp2d(light.x, light.y, light.S2[:,:,i], kind='linear')

        S0 = S0_interp(camera.x, camera.y)
        S1 = S1_interp(camera.x, camera.y)
        S2 = S2_interp(camera.x, camera.y)

        delay = Crystal(delay_thickness, delay_cut_angle, material_name, delay_orientation, wavelength, alpha, delta)
        displacer = Crystal(displacer_thickness, displacer_cut_angle, material_name, displacer_orientation, wavelength, alpha, delta)

        phi = delay.phase_offset(wavelength) + delay.phase_shear(wavelength, lens.focal_length)*camera.yy + displacer.phase_offset(wavelength) + displacer.phase_shear(wavelength, lens.focal_length)*camera.yy
        S_out[:,:,i] = light.interact(phi, S0.T, S1.T, S2.T, FLC)

    image = np.sum(S_out, axis=2)

    return image

def save_image(image, filename):

    #save image as a HDF file

    x = pd.HDFStore(filename)

    x.append("a", pd.DataFrame(image))
    x.close()

    return

filepath='/home/sgibson/work/msesim/runs/imse_2d_mastu_grasshopper_hm07c_f50mm/output/data/imse_2d_mastu_grasshopper_hm07c_f50mm.dat'

light = Light(filepath, dimension=2)

FLC = 90

lens_focal_length = 50*10**-3

material_name = 'alpha_bbo'

delay_L = 15*10**-3 #15mm for MAST plasmas #5*10**-3
delay_cut = 0.
delay_orientation = 90.

displacer_L = 3*10**-3 #4.5*10**-3 #3mm for MAST plasmas
displacer_cut = 45. #45 deg for MAST plasmas # 30deg for DIII-D
displacer_orientation = 90.

lens = Lens(lens_focal_length)
camera = Camera(name='grasshopper', lens=lens)


image = make_image(delay_L, delay_cut, delay_orientation, displacer_L, displacer_cut, displacer_orientation, material_name, FLC)
#image2 = make_image(delay_L, delay_cut, delay_orientation, displacer_L, displacer_cut, displacer_orientation, material_name, FLC=45)

save_image(image.T, filename='imse_2d_mastu_grasshopper_hm07c_f50mm_state1_100kAECCD.hdf')
#save_image(image2.T, filename='imse_2d_mastu_grasshopper_hm07c_f50mm_state2.hdf')
