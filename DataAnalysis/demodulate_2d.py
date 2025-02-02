#External Imports
import numpy as np
import os
import matplotlib.pyplot as plt
from DataAnalysis.peak_find import indexes
from scipy.optimize import curve_fit

#Internal imports
from DataAnalysis.read_binary import load_binary

def get_images(filename):
    images = load_binary(filename, FLC=True)
    return images

def prepare_image(images, frame):
    image = images[:, :, frame]
    image = image/np.max(image)
    return image

def center_points(image):
    shape = np.shape(image)
    x_center = int(shape[0]/2)
    y_center = int(shape[1]/2)

    return x_center, y_center

def fft_2D(image):
    return np.fft.fft2(image, axes=(0,1))

def get_carrier_frequency(x_center, image):

    image_fft = fft_2D(image)
    shift_image = np.fft.fftshift(image_fft) #shift so DC frequency is in the center.

    center_slice = shift_image[x_center,:]

    fringe_peaks = indexes(abs(center_slice), thres=0.1, min_dist=1)

    carrier_peak_coord = [x_center, fringe_peaks[-1]]

    return carrier_peak_coord, shift_image

def createCircularMask(h, w, center=None, radius=None):

    if center is None: # use the middle of the image
        center = [int(w/2), int(h/2)]
    if radius is None: # use the smallest distance between the center and image walls
        radius = min(center[0], center[1], w-center[0], h-center[1])

    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)

    mask = dist_from_center <= radius

    mask = mask * 1.0

    #true_mask = np.argwhere(mask==1.0)

    #fi.gaussian_filter(mask[true_mask], sigma=2)

    return mask

def filter_image(mask, shift_image):

    filtered_image = shift_image*mask

    ifft_image = np.fft.ifft2(filtered_image)

    phase = np.arctan2(ifft_image.imag, ifft_image.real)

    return phase

def unwrap(phase_array):

    y_pix, x_pix = np.shape(phase_array)
    phase_contour = -np.unwrap(phase_array[int(np.round(y_pix / 2)), :])

    # sequentially unwrap image columns:
    phase_uw_col = np.zeros_like(phase_array)

    for i in range(0, x_pix):
        phase_uw_col[:, i] = np.unwrap(phase_array[:, i])

    phase_contour = phase_contour + phase_uw_col[int(np.round(y_pix / 2)), :]
    phase_0 = np.tile(phase_contour, [y_pix, 1])
    phase_uw = phase_uw_col - phase_0

    # wrap image centre into [-pi, +pi] (assumed projection of optical axis onto detector)
    y_centre_idx = np.round((np.size(phase_uw, 0) - 1) / 2).astype(np.int)
    x_centre_idx = np.round((np.size(phase_uw, 1) - 1) / 2).astype(np.int)
    phase_uw_centre = phase_uw[y_centre_idx, x_centre_idx]

    if phase_uw_centre > 0:
        while abs(phase_uw_centre) > np.pi:
            phase_uw -= 2*np.pi
            phase_uw_centre = phase_uw[y_centre_idx, x_centre_idx]
    else:
        while abs(phase_uw_centre) > np.pi:
            phase_uw += 2*np.pi
            phase_uw_centre = phase_uw[y_centre_idx, x_centre_idx]

    return phase_uw

def calculate_phase(n_frames, filename, frame):

    phase_differences = []
    phases = np.zeros((1280, 1080, n_frames))

    for i in range(n_frames):
        images = get_images(filename)
        image = prepare_image(images, frame[i])
        x_center, y_center = center_points(image)
        image_fft = fft_2D(image)
        carrier_peak_coord, shift_image = get_carrier_frequency(x_center, image)

        center = [carrier_peak_coord[1], carrier_peak_coord[0]]
        radius = 20
        h,w = np.shape(image)
        mask = createCircularMask(h, w, center=center, radius=radius)
        phase = filter_image(mask, shift_image)

        unwrapped_phase = unwrap(phase)

        phases[:,:,i] = unwrapped_phase

    for n in range(n_frames-1):
        phase_difference = phases[:,:,n+1] - phases[:,:,n]
        phase_differences.append(phase_difference)

    phase_diff = np.asarray(phase_differences)
    phase_diff = phase_diff[::2,:,:]

    return phases, phase_diff

def linear_fit(x, m, c):
    return m*x + c

def calculate_offset(ny, nx, phase_diff, start, end,flip):

    center_y = np.round((ny - 1) / 2).astype(np.int)
    center_x = np.round((nx - 1) / 2).astype(np.int)

    central_offsets = phase_diff[:,center_y, center_x]*(180./np.pi)

    rotary_stage_angles = np.arange(0,180,10)

    #Do a fit to calculate the offset!

    phase_offsets = central_offsets[start:end] #take first points before the phase jump
    polariser_angles = rotary_stage_angles[start:end]

    plt.figure()
    plt.plot(polariser_angles, phase_offsets)
    plt.show()

    guess = [1,1]
    popt, pcov = curve_fit(linear_fit, polariser_angles, phase_offsets, p0 = guess)
    y_fit = popt[0]*polariser_angles + popt[1]
    offset = (popt[1]/4)+flip
    print('Fitted offset is,', (popt[1]/4)+flip)
    print('Gradient is', popt[0])

    return polariser_angles, phase_offsets, y_fit, offset, central_offsets, rotary_stage_angles

def offset_from_reference(phase_diff, nx, ny, n_frames):

    reference_image = phase_diff[0,:,:]
    offset_images = np.zeros((int(n_frames/2), ny, nx))

    for i in range(int(n_frames/2)-1):
        offset_images[i,:,:] = phase_diff[i,:,:] - reference_image

    return offset_images

def calculate_offset_from_reference(ny, nx, offset_images):

    center_y = np.round((ny - 1) / 2).astype(np.int)
    center_x = np.round((nx - 1) / 2).astype(np.int)

    central_offsets = offset_images[:,center_y, center_x]*(180./np.pi)

    print(central_offsets.shape)

    rotary_stage_angles = np.arange(0,190,10)

    plt.figure()
    plt.plot(rotary_stage_angles, central_offsets, 'x')
    plt.ylabel('4 $\Theta_{out}$ - $\Theta_{polariser}$')
    plt.xlabel('$\Theta_{polariser}$')
    plt.show()

    #Do a fit to calculate the offset!

    phase_offsets = central_offsets[0:7] #take first points before the phase jump
    polariser_angles = rotary_stage_angles[0:7]

    guess = [1,1]
    popt, pcov = curve_fit(linear_fit, polariser_angles, phase_offsets, p0 = guess)
    y_fit = popt[0]*polariser_angles + popt[1]

    print('Fitted offset is,', popt[1]/4)
    print('Gradient is', popt[0])

    return polariser_angles, phase_offsets, y_fit, central_offsets, rotary_stage_angles

def plot_spectrogram(image_fft):
    plt.figure()
    plt.imshow(np.log10(abs(np.fft.fftshift(image_fft.T))))
    plt.clim(0,6)
    plt.colorbar()
    plt.show()

def plot_image(image):

    plt.figure()
    plt.title('Ne $\lambda$ = 600nm')
    plt.imshow(image.T, cmap='gray')
    cbar = plt.colorbar()
    cbar.ax.set_ylabel('Normalised Intensity', rotation=90)
    plt.xlabel('x pixels')
    plt.ylabel('y pixels')
    plt.show()

    return

def plot_phase_diff(phase_diff):
    plt.figure()
    plt.title('Ne $\lambda$ = 600nm')
    plt.imshow(phase_diff[0,:,:])
    cbar = plt.colorbar()
    cbar.ax.set_ylabel('Phase (Radians)', rotation=90)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.show()
    return

def plot_image_slice(image):
    plt.figure()
    plt.title('Ne $\lambda$ = 600nm')
    plt.plot(image[500,:])
    plt.xlabel('X pixels')
    plt.ylabel('Intensity')
    plt.show()
    return

ny= 1280
nx= 1080
n_frames = 37
frame = np.arange(0,38,1)

filename = str(os.getcwd()) + '/sam_8.dat'

phases, phase_diff = calculate_phase(n_frames, filename, frame)

polariser_angles_set1, phase_offsets_set1, y_fit_set1, offset_set1,  central_offsets_set1, rotary_stage_angles_set1 = calculate_offset(ny, nx, phase_diff, start=0, end=7, flip=0)
polariser_angles_set2, phase_offsets_set2, y_fit_set2, offset_set2,  central_offsets_set2, rotary_stage_angles_set2 = calculate_offset(ny, nx, phase_diff, start=8, end=13, flip=np.pi/2)
polariser_angles_set3, phase_offsets_set3, y_fit_set3, offset_set3,  central_offsets_set3, rotary_stage_angles_set3 = calculate_offset(ny, nx, phase_diff, start=14, end=18, flip=np.pi)

#Calculate the offset using the first FLC state image as a reference

#offset_images = offset_from_reference(phase_diff, nx, ny, n_frames)
#polariser_angles, phase_offsets, y_fit = calculate_offset_from_reference(ny, nx, offset_images)

residual_offset_1 = (phase_offsets_set1/4 - polariser_angles_set1) - offset_set1
residual_offset_2 = (phase_offsets_set2/4 - polariser_angles_set2) - offset_set2
residual_offset_3 = (phase_offsets_set3/4 - polariser_angles_set3) - offset_set3

plt.figure()
plt.plot(residual_offset_1)
plt.plot(residual_offset_2+np.pi/2)
plt.plot(residual_offset_3+np.pi)
plt.show()

plt.figure()
plt.plot(polariser_angles_set1, y_fit_set1/4, '--', label='fitted')
plt.plot(polariser_angles_set1, phase_offsets_set1/4, 'x', label='Data')
plt.xlabel('Polariser angle (degrees)')
plt.ylabel('Phase offset (degrees)')
plt.legend()
plt.show()
#
#
plt.figure()
plt.plot(rotary_stage_angles_set1, central_offsets_set1/4, 'x')
plt.xlabel('Polariser Angle (degrees)')
plt.ylabel('Phase offset at image center (degrees)')
plt.show()