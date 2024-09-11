# coding=utf-8
# =============================================================================
# Copyright (c) 2024 FLIR Integrated Imaging Solutions, Inc. All Rights Reserved.
#
# This software is the confidential and proprietary information of FLIR
# Integrated Imaging Solutions, Inc. ("Confidential Information"). You
# shall not disclose such Confidential Information and shall use it only in
# accordance with the terms of the license agreement you entered into
# with FLIR Integrated Imaging Solutions, Inc. (FLIR).
#
# FLIR MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE
# SOFTWARE, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE, OR NON-INFRINGEMENT. FLIR SHALL NOT BE LIABLE FOR ANY DAMAGES
# SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING OR DISTRIBUTING
# THIS SOFTWARE OR ITS DERIVATIVES.
# =============================================================================
#
# Acquisition.py shows how to acquire images. It relies on
# information provided in the Enumeration example. Also, check out the
# ExceptionHandling and NodeMapInfo examples if you haven't already.
# ExceptionHandling shows the handling of standard and Spinnaker exceptions
# while NodeMapInfo explores retrieving information from various node types.
#
# This example touches on the preparation and cleanup of a camera just before
# and just after the acquisition of images. Image retrieval and conversion,
# grabbing image data, and saving images are all covered as well.
#
# Once comfortable with Acquisition, we suggest checking out
# AcquisitionMultipleCamera, NodeMapCallback, or SaveToAvi.
# AcquisitionMultipleCamera demonstrates simultaneously acquiring images from
# a number of cameras, NodeMapCallback serves as a good introduction to
# programming with callbacks and events, and SaveToAvi exhibits video creation.
#
# Please leave us feedback at: https://www.surveymonkey.com/r/TDYMVAPI
# More source code examples at: https://github.com/Teledyne-MV/Spinnaker-Examples
# Need help? Check out our forum at: https://teledynevisionsolutions.zendesk.com/hc/en-us/community/topics

import os
import csv
import PySpin
import sys
from datetime import datetime
import time
from camera_settings import exposure_settings, gain_settings, frame_rate_settings, buffer_settings, acquisition_mode_settings

NUM_IMAGES = 1  # number of images to grab
folder_path = f"/home/sfv514/Documents/Project/Camera/Saved Images/{today_date}"

def setup_file_structure(shotno, passno):
    #Find current working directory
    #Check for folder setup
    #If not there, make the folder setup
    
    cwd = os.getcwd()
    
    folder_path = os.path.join(cwd, "data", f"{shotno}", f"Pass{passno}")
        
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    


def acquire_single_image(cam, nodemap, ExposureTime, Temperature):
    """
    Acquires a single image from the camera and saves it along with recording metadata to a CSV file.

    :param cam: Camera to acquire images from.
    :param nodemap: Device nodemap.
    :param nodemap_tldevice: Transport layer device nodemap.
    :type cam: CameraPtr
    :type nodemap: INodeMap
    :type nodemap_tldevice: INodeMap
    :return: True if successful, False otherwise.
    :rtype: bool
    """

    print('*** IMAGE ACQUISITION ***')

    try:
        result = True

        # Set acquisition mode
        acquisition_mode = 'SingleFrame'

        acquisition_mode_settings(nodemap, acquisition_mode)

        ## Begin Acquisition ##
        cam.BeginAcquisition()

        print('Acquiring image...\n')

        # Time and date
        now = datetime.now()
        time_6_digit = now.strftime("%H%M%S")
        today_date = now.strftime("%d-%m-%y")

        print('*** SETTING TIMEOUT ***')

        timeout = int(cam.ExposureTime.GetValue() / 1000 + 3000)
        print(f'Timeout: {timeout}ms\n')

        # Define folder path
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Prepare CSV file for metadata    
        csv_file_path = os.path.join(folder_path, "image_metadata.csv")
        with open(csv_file_path, mode='a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            if os.stat(csv_file_path).st_size == 0:
                # Write header only if file is empty
                csv_writer.writerow(['Image Name', 'Timestamp', 'Exposure Time (us)', 'Acquisition Time(us)', 'Temperature (C)'])

            try:
                start_time = time.time()

                # Acquire single image
                image_result = cam.GetNextImage(timeout)

                acquisition_time = time.time() - start_time

                exposure_time_retrieved = cam.ExposureTime.GetValue()

                print(f'Exposure time set to {exposure_time_retrieved/(1e6):.4}s / {exposure_time_retrieved:.4}us')
                print(f'Acquisition Time: {acquisition_time:.3}s / {acquisition_time*1e6:.3}us\n')

                if acquisition_time > exposure_time_retrieved/(1e6):
                    print('Acquisition took longer than the set exposure time, as expected :)\n')
                else:
                    print('** Acquisition time less than the set exposure time! ** :(\n')
                    return False


                if image_result.IsIncomplete():
                    print(f'Image incomplete with image status {image_result.GetImageStatus()} ...')
                else:
                    width = image_result.GetWidth()
                    height = image_result.GetHeight()
                    print(f'Grabbed Image, width = {width}, height = {height}')

                    # Save image
                    filename = f'Acquisition_{time_6_digit}'
                    image_path = os.path.join(folder_path, filename)
                    image_result.Save(image_path, PySpin.SPINNAKER_IMAGE_FILE_FORMAT_RAW)
                    print(f'Image saved at {image_path}')

                    # Save metadata to CSV
                    csv_writer.writerow([filename, now.strftime("%Y-%m-%d %H:%M:%S"), ExposureTime, acquisition_time*1e6, Temperature])

                    image_result.Release()
                    print('')

            except PySpin.SpinnakerException as ex:
                print(f'Error: {ex}')
                return False

        cam.EndAcquisition()

    except PySpin.SpinnakerException as ex:
        print(f'Error: {ex}')
        return False

    return result

def print_device_info(nodemap):
    """
    This function prints the device information of the camera from the transport
    layer; please see NodeMapInfo example for more in-depth comments on printing
    device information from the nodemap.

    :param nodemap: Transport layer device nodemap.
    :type nodemap: INodeMap
    :returns: True if successful, False otherwise.
    :rtype: bool
    """

    print('*** DEVICE INFORMATION ***')

    try:
        result = True
        node_device_information = PySpin.CCategoryPtr(nodemap.GetNode('DeviceInformation'))

        if PySpin.IsReadable(node_device_information):
            features = node_device_information.GetFeatures()
            for feature in features:
                node_feature = PySpin.CValuePtr(feature)
                print('%s: %s' % (node_feature.GetName(),
                node_feature.ToString() if PySpin.IsReadable(node_feature) else 'Node not readable'))

        else:
            print('Device control information not readable.')

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result


def run_single_camera(cam):
    """"
    :param cam: Camera to run on.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Retrieve TL device nodemap and print device information. **Uncomment if you want to display device information**

        # nodemap_tldevice = cam.GetTLDeviceNodeMap()
        # result &= print_device_info(nodemap_tldevice)

        # Initialize camera
        cam.Init()

        # Retrieve GenICam nodemap
        nodemap = cam.GetNodeMap()
        tl_nodemap = cam.GetTLStreamNodeMap()

        Device_Temp_node = PySpin.CFloatPtr(nodemap.GetNode('DeviceTemperature'))
        Device_Temp = Device_Temp_node.GetValue()
        print(f'Device Temperature (C): {Device_Temp:.4}\n')

        # GAIN SETTINGS # 
        # Set autogain: 'Off', 'Once', 'Continuous'
        Gain = 0.0
        AutoGain = "Off"

        gain_settings(cam, nodemap, Gain, AutoGain)

        # FRAME RATE SETTINGS # 
        # For single image turn FrameRateAuto to 'Off' and FrameRateEnable to False
        FrameRateAuto = 'Off'
        FrameRateEnable = False

        frame_rate_settings(nodemap, FrameRateAuto, FrameRateEnable)

        # EXPOSURE TIME SETTINGS #
        # Set exposure time in microseconds (us)
        exposure_time = 1e6
        exposure_compensation_mode = "Off"
        exposure_compensation = 0.0

        exposure_settings(cam, nodemap, exposure_time, exposure_compensation_mode, exposure_compensation)

        # BUFFER SETTINGS #
        # Determines how to retrieve data from camera buffer. 'NewestOnly', 'OldestFirst', 'OldestFirstOverwrite', 'NewestFirst'.
        handling_mode = 'NewestOnly'

        buffer_settings(tl_nodemap, handling_mode)

        # Acquire images
        result &= acquire_single_image(cam, nodemap, exposure_time, Device_Temp)

        # Deinitialize camera
        cam.DeInit()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result


def print_all_nodes(cam):

    # Retrieve GenICam nodemap
    nodemap = cam.GetNodeMap()

    # print all nodes
    nodes = nodemap.GetNodes()

    for node in nodes:
        print(node.GetName())


def main():
    """
    Example entry point; please see Enumeration example for more in-depth
    comments on preparing and cleaning up the system.

    :return: True if successful, False otherwise.
    :rtype: bool
    """

    # Since this application saves images in the current folder
    # we must ensure that we have permission to write to this folder.
    # If we do not have permission, fail right away.

    # Record the initial time
    initial_time = time.time()

    try:
        test_file = open('test.txt', 'w+')
    except IOError:
        print('Unable to write to current directory. Please check permissions.')
        input('Press Enter to exit...')
        return False

    test_file.close()
    os.remove(test_file.name)

    result = True

    # Retrieve singleton reference to system object
    system = PySpin.System.GetInstance()

    # Get current library version
    version = system.GetLibraryVersion()
    print('Library version: %d.%d.%d.%d' % (version.major, version.minor, version.type, version.build))

    # Retrieve list of cameras from the system
    cam_list = system.GetCameras()

    num_cameras = cam_list.GetSize()

    print('Number of cameras detected: %d' % num_cameras)

    # Finish if there are no cameras
    if num_cameras == 0:

        # Clear camera list before releasing system
        cam_list.Clear()

        # Release system instance
        system.ReleaseInstance()

        print('Not enough cameras!')
        input('Done! Press Enter to exit...')
        return False

    # Run example on each camera
    for i, cam in enumerate(cam_list):
        print('Running example for camera %d...\n' % i)

        result &= run_single_camera(cam)
        print('Camera %d example complete... \n' % i)

    # Release reference to camera
    # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
    # cleaned up when going out of scope.
    # The usage of del is preferred to assigning the variable to None.

    cam.DeInit()
    del cam

    # Clear camera list before releasing system
    cam_list.Clear()

    # Release system instance
    system.ReleaseInstance()

    # Record the final time
    final_time = time.time()

    # Calculate the time difference
    elapsed_time = final_time - initial_time

    # Print the elapsed time in seconds
    print(f'Code run time: {elapsed_time}s')

    input('Done! Press Enter to exit...')
    return result



if __name__ == '__main__':
    if main():
        
        sys.exit(0)
    else:
        sys.exit(1)