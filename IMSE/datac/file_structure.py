"""_summary_
Collection of codes to set up appropriate file structures, increment shot number, get the current shot number etc.
"""

import os
import glob

def setup_file_structure(shotno, passno):
    """_If file directory structure doesn't exist, then make it_

    Args:
        shotno (_type_): _description_
        passno (_type_): _description_
    """
    
    cwd = os.getcwd()
    
    folder_path = os.path.join(cwd, "data", f"{shotno}", f"Pass{passno}")

    try:
        os.makedirs(folder_path)
    except FileExistsError:
        print('Directory for shot {} already exists! Incrementing pass number...')
        passno += passno
        new_folder_path = os.path.join(cwd, "data", f"{shotno}", f"Pass{passno}")
        os.makedirs(folder_path)
        
        
def get_last_directory(filepath):
    """Find the name of the directory which was created most recently.
    """
    list_of_directories = glob.glob(filepath)
    lastest_directory = max(list_of_directories, key=os.path.getctime)
    return lastest_directory

shotno = 123456
passno = 0
setup_file_structure(shotno, passno)