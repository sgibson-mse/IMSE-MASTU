import numpy as np
from scipy.interpolate import interp2d
import pandas as pd

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

def make_image(delay_thickness, delay_cut_angle, delay_orientation, displacer_thickness, displacer_cut_angle, displacer_orientation, material_name, savart_thickness, savart_cut, savart_orientation):

    alpha, beta, delta = project_light(orientation=90)

    S_out = np.zeros((len(camera.x), len(camera.y), len(light.wavelength)))

    for i, wavelength in enumerate(light.wavelength):

        S0_interp = interp2d(light.x, light.y, light.S0[:,:,i], kind='quintic')
        S1_interp = interp2d(light.x, light.y, light.S1[:,:,i], kind='quintic')
        S2_interp = interp2d(light.x, light.y, light.S2[:,:,i], kind='quintic')
        S3_interp = interp2d(light.x, light.y, light.S3[:,:,i], kind='quintic')

        S0 = S0_interp(camera.x, camera.y)
        S1 = S1_interp(camera.x, camera.y)
        S2 = S2_interp(camera.x, camera.y)
        S3 = S3_interp(camera.x, camera.y)

        savart_1 = Crystal(savart_thickness,savart_cut, material_name, savart_orientation[0], wavelength, alpha, delta)
        savart_2 = Crystal(savart_thickness,savart_cut, material_name, savart_orientation[1], wavelength, alpha, delta)
        delay = Crystal(delay_thickness, delay_cut_angle, material_name, delay_orientation, wavelength, alpha, delta)
        displacer = Crystal(displacer_thickness, displacer_cut_angle, material_name, displacer_orientation, wavelength, alpha, delta)

        S_out[:, :, i] = 2 * S0 + 2 * S2 * np.cos(delay.phi + displacer.phi) +\
                            S1 * (np.cos(displacer.phi + delay.phi + savart_1.phi - savart_2.phi) - np.cos(delay.phi + displacer.phi - savart_1.phi + savart_2.phi)) -\
                            S3 * (np.sin(displacer.phi + delay.phi + savart_1.phi - savart_2.phi) + np.sin(displacer.phi + delay.phi - savart_1.phi + savart_2.phi))

    image = np.sum(S_out, axis=2)

    return image

def save_image(image, filename):

    #save image as a HDF file

    x = pd.HDFStore(filename)

    x.append("a", pd.DataFrame(image))
    x.close()

    return


filepath = '/work/sgibson/msesim/runs/imse_2d_edgecurrent_largejphi/output/data/MAST_24409_imse.dat'

light = Light(filepath, dimension=2)

lens_focal_length = 85*10**-3

material_name = 'alpha_bbo'

delay_L = 15*10**-3
delay_cut = 0.
delay_orientation = 90.

displacer_L = 3*10**-3
displacer_cut = 45.
displacer_orientation = 90.

savart_thickness = 2*10**-3
savart_orientation = [45, 135]
savart_cut = 45.

camera = Camera(name='photron-sa4')
lens = Lens(lens_focal_length)
image = make_image(delay_L, delay_cut, delay_orientation, displacer_L, displacer_cut, displacer_orientation, material_name, savart_thickness, savart_cut, savart_orientation)
save_image(image, filename='ash.hdf')
