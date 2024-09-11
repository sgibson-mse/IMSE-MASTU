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
# Exposure_QuickSpin.py shows how to customize image exposure time
# using the QuickSpin API. QuickSpin is a subset of the Spinnaker library
# that allows for simpler node access and control.
#
# This example prepares the camera, sets a new exposure time, and restores
# the camera to its default state. Ensuring custom values fall within an
# acceptable range is also touched on. Retrieving and setting information
# is the only portion of the example that differs from Exposure.
#
# A much wider range of topics is covered in the full Spinnaker examples than
# in the QuickSpin ones. There are only enough QuickSpin examples to
# demonstrate node access and to get started with the API; please see full
# Spinnaker examples for further or specific knowledge on a topic.
#
# Please leave us feedback at: https://www.surveymonkey.com/r/TDYMVAPI
# More source code examples at: https://github.com/Teledyne-MV/Spinnaker-Examples
# Need help? Check out our forum at: https://teledynevisionsolutions.zendesk.com/hc/en-us/community/topics

import PySpin


def exposure_settings(cam, nodemap, exposure_time_user_defined, exposure_compensation_mode, exposure_compensation):
    """
        This function configures a custom exposure time. Automatic exposure is turned
        off in order to allow for the customization, and then the custom setting is
        applied.

        :param cam: Camera to configure exposure for.
        :type cam: CameraPtr
        :return: True if successful, False otherwise.
        :rtype: bool
    """

    print('*** CONFIGURING EXPOSURE ***')

    try:
        result = True

        # Turn off automatic exposure mode
        #
        # *** NOTES ***
        # Automatic exposure prevents the manual configuration of exposure
        # times and needs to be turned off for this example. Enumerations
        # representing entry nodes have been added to QuickSpin. This allows
        # for the much easier setting of enumeration nodes to new values.
        #
        # The naming convention of QuickSpin enums is the name of the
        # enumeration node followed by an underscore and the symbolic of
        # the entry node. Selecting "Off" on the "ExposureAuto" node is
        # thus named "ExposureAuto_Off".
        #
        # *** LATER ***
        # Exposure time can be set automatically or manually as needed. This
        # example turns automatic exposure off to set it manually and back
        # on to return the camera to its default state.

        if cam.ExposureAuto.GetAccessMode() != PySpin.RW:
            print('Unable to disable automatic exposure. Aborting...')
            return False

        cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        print('Automatic exposure disabled...')

        # Set exposure time manually; exposure time recorded in microseconds
        #
        # *** NOTES ***
        # Notice that the node is checked for availability and writability
        # prior to the setting of the node. In QuickSpin, availability and
        # writability are ensured by checking the access mode.
        #
        # Further, it is ensured that the desired exposure time does not exceed
        # the maximum. Exposure time is counted in microseconds - this can be
        # found out either by retrieving the unit with the GetUnit() method or
        # by checking SpinView.

        if cam.ExposureTime.GetAccessMode() != PySpin.RW:
            print('Unable to set exposure time. Aborting...')
            return False

        # Ensure desired exposure time does not exceed the maximum
        exposure_time_user_defined = min(cam.ExposureTime.GetMax(), exposure_time_user_defined)
        cam.ExposureTime.SetValue(exposure_time_user_defined)

        print(f'Max exposure time is: {(cam.ExposureTime.GetMax()/(1e6)):.4}s / {cam.ExposureTime.GetMax():.4}us')

        # Retrieve node value
        exposure_time_retrieved = cam.ExposureTime.GetValue()

        # Print retrieved exposure time
        print(f'Exposure time set to {exposure_time_retrieved/(1e6):.4}s / {exposure_time_retrieved:.4}us')

        ## Auto Exposure Compensation ##
        ExposureCompensationAuto_node = PySpin.CEnumerationPtr(nodemap.GetNode("pgrExposureCompensationAuto"))

        ExposureCompensationAuto_node_off = ExposureCompensationAuto_node.GetEntryByName(exposure_compensation_mode)

        ExposureCompensationAuto_node.SetIntValue(ExposureCompensationAuto_node_off.GetValue())

        # Retrieve exposure compensation auto value
        ExposureCompensationAuto = ExposureCompensationAuto_node.GetCurrentEntry().GetSymbolic()

        print(f'Exposure Compensation Mode: {ExposureCompensationAuto}')
        
        ## Retrieve exposure compensation node ##
        ExposureCompensationValue_node = PySpin.CFloatPtr(nodemap.GetNode("pgrExposureCompensation"))

        # Set exposure compensation
        ExposureCompensationValue_node.SetValue(exposure_compensation)

        # Retrieve value
        ExposureCompensationValue = ExposureCompensationValue_node.GetValue()
        print(f'Exposure Compensation: {ExposureCompensationValue}\n')
        

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result


def gain_settings(cam, nodemap, gain, gainauto):
    """
        This function configures a custom exposure time. Automatic exposure is turned
        off in order to allow for the customization, and then the custom setting is
        applied.

        :param cam: Camera to configure exposure for.
        :type cam: CameraPtr
        :return: True if successful, False otherwise.
        :rtype: bool
    """

    print('*** CONFIGURING GAIN ***')

    try:
        result = True

        ## Set auto gain to off ##
        
        # Retrieve node (Enumeration node in this case)

        GainAuto_node = PySpin.CEnumerationPtr(nodemap.GetNode("GainAuto"))

        # EnumEntry node (always associated with an Enumeration node)
        GainAuto_node_set = GainAuto_node.GetEntryByName(gainauto)

        # Turn off Auto Gain
        GainAuto_node.SetIntValue(GainAuto_node_set.GetValue())

        ## Set gain
        cam.Gain.SetValue(gain)

        # Retrieve gain settings
        GainAuto = GainAuto_node.GetCurrentEntry().GetSymbolic()

        Gain_node = PySpin.CFloatPtr(nodemap.GetNode('Gain'))
        Gain = Gain_node.GetValue()

        print('Auto Gain:', GainAuto)
        print(f'Gain: {Gain}\n')

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result


def frame_rate_settings(nodemap, FrameRateAuto, FrameRateEnable):

    print('*** CONFIGURING FRAME RATE ***')

    #Frame rate, retrieve node (boolean)
    FrameRateEnable_node = PySpin.CBooleanPtr(nodemap.GetNode("AcquisitionFrameRateEnabled"))

    # Set value to True first to enable changing of Frame Rate Auto node
    FrameRateEnable_node.SetValue(True)

    try:
        print('Accessing FrameRateAuto node...')
        FrameRateAuto_node = PySpin.CEnumerationPtr(nodemap.GetNode("AcquisitionFrameRateAuto"))
        
        # or not PySpin.IsWritable(FrameRateAuto_node):
        if not PySpin.IsAvailable(FrameRateAuto_node):
            raise Exception("FrameRateAuto node is not available or writable.")

        print('Setting FrameRateAuto node to:', FrameRateAuto)
        FrameRateAuto_node_off = FrameRateAuto_node.GetEntryByName(FrameRateAuto)
        
        if not PySpin.IsAvailable(FrameRateAuto_node_off) or not PySpin.IsReadable(FrameRateAuto_node_off):
            raise Exception(f"FrameRateAuto entry '{FrameRateAuto}' is not available or readable.")
        
        FrameRateAuto_node.SetIntValue(FrameRateAuto_node_off.GetValue())
        print(f"Successfully set FrameRateAuto to {FrameRateAuto}.")
    
    except PySpin.SpinnakerException as ex:
        print(f"SpinnakerException: {ex}")
    except Exception as ex:
        print(f"Exception: {ex}")


    #Frame rate, retrieve node (boolean)
    FrameRateEnable_node = PySpin.CBooleanPtr(nodemap.GetNode("AcquisitionFrameRateEnabled"))

    # Set value to False to disable the frame rate enable
    FrameRateEnable_node.SetValue(FrameRateEnable)

    FrameRateEnabled_retreived = FrameRateEnable_node.GetValue()

    print(f'Frame rate enabled? {FrameRateEnabled_retreived}\n')



def buffer_settings(tl_nodemap, handling_mode):
    """
    Configures buffer settings for the camera by setting the stream buffer handling mode.
    
    Parameters:
    - tl_nodemap: The node map for the transport layer.
    - handling_mode: The desired buffer handling mode as a string.
    """
    print('*** CONFIGURING BUFFER SETTINGS ***')

    try:
        print('Accessing Stream Buffer Handling node...')
        # Retrieve buffer node
        handling_mode_node = PySpin.CEnumerationPtr(tl_nodemap.GetNode('StreamBufferHandlingMode'))

        # Check if the node is available and writable
        if not PySpin.IsAvailable(handling_mode_node) or not PySpin.IsWritable(handling_mode_node):
            raise Exception("Stream Buffer Handling node is not available or writable.")
        
        print(f'Setting node to {handling_mode}...')
        
        # Set the desired handling mode
        handling_mode_entry = handling_mode_node.GetEntryByName(handling_mode)
        if not PySpin.IsAvailable(handling_mode_entry) or not PySpin.IsReadable(handling_mode_entry):
            raise Exception(f"Handling mode entry '{handling_mode}' is not available or readable.")
        
        handling_mode_node.SetIntValue(handling_mode_entry.GetValue())

        # Verify that the handling mode was successfully set
        handling_mode_retrieved = handling_mode_node.GetCurrentEntry().GetSymbolic()
        if handling_mode == handling_mode_retrieved:
            print(f'Handling mode successfully set to {handling_mode_retrieved}.\n')
        else:
            raise Exception("Handling mode was not successfully set.\n")
    
    except PySpin.SpinnakerException as ex:
        print(f"SpinnakerException: {ex}")
    except Exception as ex:
        print(f"Exception: {ex}")


def acquisition_mode_settings(nodemap, acquisition_mode):
    """
    Sets the acquisition mode of the camera.
    
    Parameters:
    - nodemap: The node map from which to retrieve the AcquisitionMode node.
    - acquisition_mode: The desired acquisition mode as a string (e.g., 'Continuous', 'SingleFrame').
    
    Returns:
    - True if the acquisition mode was successfully set.
    - False if there was an error.
    """
    try:
        # Retrieve the AcquisitionMode node
        acquisition_mode_node = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
        if not PySpin.IsReadable(acquisition_mode_node) or not PySpin.IsWritable(acquisition_mode_node):
            print('Unable to set acquisition mode (enum retrieval). Aborting...')
            return False

        # Retrieve the specific entry corresponding to the desired acquisition mode
        acquisition_mode_node_set = acquisition_mode_node.GetEntryByName(acquisition_mode)
        if not PySpin.IsReadable(acquisition_mode_node_set):
            print('Unable to set acquisition mode. Aborting...')
            return False

        # Set the acquisition mode
        acquisition_mode_node.SetIntValue(acquisition_mode_node_set.GetValue())

        # Verify the acquisition mode was successfully set
        acquisition_mode_retrieved = acquisition_mode_node.GetCurrentEntry().GetSymbolic()

        if acquisition_mode_retrieved == acquisition_mode:
            print(f'Acquisition mode successfully set to: {acquisition_mode_retrieved}\n')
            return True
        else:
            print('Error: Acquisition mode was not set correctly. Aborting...')
            return False

    except PySpin.SpinnakerException as ex:
        print(f"SpinnakerException: {ex}")
        return False
    except Exception as ex:
        print(f"Exception: {ex}")
        return False

        
        

def get_all_node_values(nodemap, nodemap_tldevice):
    nodes = nodemap.GetNodes()
    
    # Retrieve Stream Parameters device nodemap
    
    for node in nodes:
        try:
            node_name = node.GetName()
            node_type = node.GetPrincipalInterfaceType()
            
            # Check node availability and readability
            if not PySpin.IsAvailable(node) or not PySpin.IsReadable(node):
                print(f'{node_name} is not available or not readable.')
                continue
            
            # Retrieve value based on node type
            if node_type == PySpin.intfIInteger:
                value = PySpin.CIntegerPtr(node).GetValue()
            elif node_type == PySpin.intfIFloat:
                value = PySpin.CFloatPtr(node).GetValue()
            elif node_type == PySpin.intfIBoolean:
                value = PySpin.CBooleanPtr(node).GetValue()
            elif node_type == PySpin.intfIEnumeration:
                value = PySpin.CEnumerationPtr(node).GetCurrentEntry().GetSymbolic()
            elif node_type == PySpin.intfIString:
                value = PySpin.CStringPtr(node).GetValue()
            elif node_type == PySpin.intfICommand:
                value = "Command node (no value)"
            else:
                value = "Unknown node type or not supported in this context"
            
            print(f'{node_name}: {value}')
        
        except PySpin.SpinnakerException as ex:
            print(f'Error retrieving value for {node_name}: {ex}')



def reset_exposure(cam):
    """
    This function returns the camera to a normal state by re-enabling automatic exposure.

    :param cam: Camera to reset exposure on.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Turn automatic exposure back on
        #
        # *** NOTES ***
        # Automatic exposure is turned on in order to return the camera to its
        # default state.

        if cam.ExposureAuto.GetAccessMode() != PySpin.RW:
            print('Unable to enable automatic exposure (node retrieval). Non-fatal error...')
            return False

        cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Continuous)

        print('Automatic exposure enabled...')

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result

