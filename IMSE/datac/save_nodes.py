import PySpin
import csv
import numpy as np


def print_all_nodes(cam):

    try:
        # Initialize camera
        cam.Init()

        # Retrieve GenICam nodemap
        nodemap = cam.GetNodeMap()

        # print all nodes
        nodes = nodemap.GetNodes()

        for node in nodes:
            print(node.GetName())

        cam.DeInit()

    except PySpin.SpinnakerException as ex:
        print(f"Error: {ex}")


def save_nodes_to_csv(cam, filepath=None, filename=None):
    """
    This function saves all available nodes (and their information) from the camera's
    GenICam nodemap to a CSV file.

    :param cam: The camera object.
    :type cam: CameraPtr
    :param filename: The name of the CSV file to save the nodes to.
    :type filename: str
    """

    try:
        # Initialize camera
        cam.Init()

        # Retrieve GenICam nodemap
        nodemap = cam.GetNodeMap()
        nodemap_tldevice = cam.GetTLDeviceNodeMap()

        # Get all nodes
        nodes = nodemap.GetNodes() 
        nodes_tldevice = nodemap_tldevice.GetNodes()

        nodes_all = np.concatenate((nodes, nodes_tldevice))

        # Open CSV file for writing
        with open(f'{filepath}{filename}', mode='w', newline='') as file:
            writer = csv.writer(file)

            for node in nodes_all:
                node_name = node.GetName()

                # Write node information to the CSV file
                writer.writerow([node_name])

        print(f"Node information saved to {filename}")

    except PySpin.SpinnakerException as ex:
        print(f"Error: {ex}")
    
    finally:
        # Deinitialize camera
        cam.DeInit()


def main():

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
        print('Running example for camera %d...' % i)

        #print_all_nodes(cam)
        save_nodes_to_csv(cam)

        print('Camera %d example complete... \n' % i)

    del cam

    # Clear camera list before releasing system
    cam_list.Clear()

    # Release system instance
    system.ReleaseInstance()

    input('Done! Press Enter to exit...')

if __name__ == '__main__':
    main()
    