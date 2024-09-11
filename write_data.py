import sys
import pyuda
from mast.mast_client import MastClient
import numpy as np

diag_tag = 'xmi'
shot = 12345
pass_number = 0
status = 1
conventions = 'Fusion-1.1'
directory = '/home/sgibson/MAST-U/IMSE/'

tvals = np.linspace(-0.05, 0.65, 163)
px = np.arange(0, 1920, 1)
py = np.arange(0,1200,1)
r_vals = np.linspace(0,1, len(px))
z_vals = np.linspace(-0.2, 0.2, len(py))
n_times = len(tvals)

# Filename for diagnostics should be <diag_tag><shot_number>.nc
# Where shotnumber is a 6-digit number with leading zeros (eg. 040255)
filename = diag_tag+"{:06d}".format(shot)+'.nc'
client = MastClient(None)

try:
    client.put(filename, directory=directory, step_id='create',
    conventions='Fusion-1.1', shot=shot,
    data_class='analysed data', title='Example netcdf file',
    comment='Example MAST-U netcdf file written with putdata in python',
    code='write_data.py',
    pass_number=pass_number, status=1,
    verbose=True, debug=True)
except pyuda.UDAException:
    print("<< ERROR >> Failed to create NetCDF file")
    sys.exit()

try:
    client.put('FLIR', step_id='device',
    type='type of device', id='#1',
    serial='123a54', resolution=8,
    range=[0, 2**8-1], channels=1)
except pyuda.UDAException:
    print('<< ERROR >> Failed to write device to file')
    sys.exit()
    
#--------------------------------
# 3. Add dimension names and lengths
# Dimensions will be available to use in variables in a group or sub-group where they are created
#--------------------------------
# /xxx/time1
try:
    client.put(len(tvals), step_id='dimension', name='time', group=f'/{diag_tag}')
except pyuda.UDAException:
    print('/{diag_tag}')
    print('<< ERROR >> Failed to write dimension time to file')
    sys.exit()
    
# /xxx/group_a/major_radius
# major_radius will only be available for variables in group_a and sub-groups
try:
    client.put(len(r_vals), step_id='dimension', name='R', group=f'/{diag_tag}/geometry')
except pyuda.UDAException:
    print('<< ERROR >> Failed to write dimension major_radius to file')
    sys.exit()
    
try:
    client.put(len(z_vals), step_id='dimension', name='Z', group=f'/{diag_tag}/geometry')
except pyuda.UDAException:
    print('<< ERROR >> Failed to write dimension major_radius to file')
    sys.exit()
    
try:
    client.put(len(px), step_id='dimension', name='px', group=f'/{diag_tag}/geometry')
except pyuda.UDAException:
    print('<< ERROR >> Failed to write dimension px to file')
    sys.exit()

try:
    client.put(len(py), step_id='dimension', name='py', group=f'/{diag_tag}/geometry')
except pyuda.UDAException:
    print('<< ERROR >> Failed to write dimension py to file')
    sys.exit()
    
# #--------------------------------
# # 4. Add co-ordinate data corresponding to dimensions previously defined
# # For time axes set class='time'
# # units and label are required attributes
# #--------------------------------
# # /xxx/time1 : 0 -> 0.99 sec
try:
    client.put(tvals, step_id='coordinate', name='time', group=f'/{diag_tag}',
    units='s', label='time', comment='time axis',
    coord_class='time')
except pyuda.UDAException:
    print('<< ERROR >> Failed to write time data')
    sys.exit()

# # /xxx/group_a/major_radius
try:
    client.put(r_vals, step_id='coordinate', name='R', group=f'/{diag_tag}/geometry',
    units='m', label='Major Radius', comment='R values')
except pyuda.UDAException:
    print('<< ERROR >> Failed to write R data')
    sys.exit()
    
try:
    client.put(z_vals, step_id='coordinate', name='Z', group=f'/{diag_tag}/geometry',
    units='m', label='Major Radius', comment='Z values')
except pyuda.UDAException:
    print('<< ERROR >> Failed to write Z data')
    sys.exit()
    
# try:
#     client.put(px, step_id='coordinate', name='p_x', group=f'/{diag_tag}/geometry',
#     units='num', label='px', comment='x pixel numbers')
# except pyuda.UDAException:
#     print('<< ERROR >> Failed to write x pixel data')
#     sys.exit()
    
# try:
#     client.put(py, step_id='coordinate', name='p_y', group=f'/{diag_tag}/geometry',
#     units='num', label='py', comment='y pixel numbers')
# except pyuda.UDAException:
#     print('<< ERROR >> Failed to write y pixel data')
#     sys.exit()

# #--------------------------------
# # 5. Write error data
# # Error data must be put in the same group as the variable it corresponds to will go
# # Error data must be written before other variables so it can be referenced.
# # units and label are required attributes
# #--------------------------------
# # Example errors /xxx/group_b/error_variable1

# try:
#     client.put(np.arange(100, dtype=np.float32) * 20.0, step_id='variable', name='error_variable1', group='/xxx/group_b',
#     dimensions='time1', units='kA', label='Errors for variable1', comment='Estimate of errors for variable 1 of')
# except pyuda.UDAException:
#     print('<< ERROR >> Failed to write error data error_variable1')
#     sys.exit()
    
# #--------------------------------
# # 6. Write signal data
# #--------------------------------
# # Example of variable with associated errors /xxx/group_b/variable1

# try:
#     client.put(np.arange(100, dtype=np.float32) * 200.0, step_id='variable', name='variable1', group='/xxx/group_b',
#     dimensions='time1', units='kA', errors='error_variable1',
#     label='variable 1', comment='example variable 1 with associated errors error_variable1')
# except pyuda.UDAException:
#     print('<< ERROR >> Failed to write data for variable1')
#     sys.exit()
# # Example of 2D variable data with associated device
# try:
#     client.put(np.arange(50*30, dtype=np.float32).reshape((50,30)), step_id='variable', name='variable2',
#     group='/xxx/group_a',
#     dimensions='time2,major_radius', units='kA', device='device_name',
#     label='variable 2', comment='example variable 2 with associated device device_name')
# except pyuda.UDAException:
#     print('<< ERROR >> Failed to write data for variable2')
#     sys.exit()
    
# #--------------------------------
# # 7. Use attributes to attach additional information to groups or variables
# # Attributes can be strings, numbers or arrays and should be
# # for additional documentation/meta-data on groups, variables and decies
# #--------------------------------
# # Attach additional attributes to a device

# try:
#     client.put('Extra information about device_name', step_id='attribute',
#     group='/devices/device_name', name='notes')
# except pyuda.UDAException as err:
#     print('<< ERROR >> Failed to write notes attribute {}'.format(err))
#     sys.exit()
# # Attach information attribute to /xxx/group_a
# try:
#     client.put('This example group contains a 2D data trace', step_id='attribute',
#     group='/xxx/group_a', name='comment')
# except pyuda.UDAException:
#     print('<< ERROR >> Failed to write comment attribute for /xxx/group_a')
#     sys.exit()
# # Attach a float attribute to /xxx/group_b/variable1
# try:
#     client.put(np.float32(100), step_id='attribute',
#     group='/xxx/group_b', varname='variable1', name='float_attribute')
# except pyuda.UDAException:
#     print('<< ERROR >> Failed to write float attribute for /xxx/group_a/variable1')
#     sys.exit()
#--------------------------------
# 8. Close file
#--------------------------------
try:
    client.put(step_id='close')
except pyuda.UDAException:
    print("<< ERROR >> Failed to close file")
    sys.exit()
#--------------------------------
# 9. Re-open file for update
# Example is changing status of file
#--------------------------------
try:
    client.put(filename, directory=directory, step_id='update', status=2)
except pyuda.UDAException:
    print("<< ERROR >> Failed to update file")
    sys.exit()

