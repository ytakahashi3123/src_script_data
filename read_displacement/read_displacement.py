#!/usr/bin/python3
##!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3
##!/usr/local/python3.6.2/bin/python3
import numpy as np
import os as os
import shutil as shutil

def str2bool(s):
     return s.lower() in ["true", "t", "yes", "1"]

# ------------------------------------
# ---Read control file----------------
data_control = np.genfromtxt("read_displacement.ctl", comments=('#'), dtype='str')
dir_input      = str( data_control[0] )
file_input     = str( data_control[1] )
num_case       = int( data_control[2] )
dir_result     = str( data_control[3] )
file_result    = str( data_control[4] )

# Scale factor
scale_factor   = float( data_control[5] )

# ------------------------------------
# -----Main routine ------------------
# ---File output---
dir_result_path = dir_result
if not os.path.exists(dir_result_path):
  os.mkdir(dir_result_path)
else:
  shutil.rmtree(dir_result_path)
  os.mkdir(dir_result_path)

# Read input data
for i in range(0,num_case):
  filename_input = dir_input+'/'+file_input+str(i+1)+'.log'
  print('Reading file...:', filename_input)
  data_input     = np.loadtxt(filename_input,comments=('#'),delimiter=None,skiprows=1)
  time     = data_input[:,0]
  delta_x  = data_input[:,4]
  delta_y  = data_input[:,5]
  delta_z  = data_input[:,6]
  force_x  = data_input[:,7]
  force_y  = data_input[:,8]
  force_z  = data_input[:,9]

  coord_x0 = data_input[0,1]
  coord_y0 = data_input[0,2]
  coord_z0 = data_input[0,3]

# Input variables for vizualization
  len_data = len(time)

  time_s = np.zeros(len_data+1).reshape(len_data+1)
  time_s[0] = 0
  time_s[1:len_data+1] = time[0:len_data]

  coord = np.zeros(3*(len_data+1)).reshape(3,len_data+1)
  coord[0,0] = coord_x0
  coord[1,0] = coord_y0
  coord[2,0] = coord_z0
  for j in range(1,len_data+1):
    coord[0,j] = coord[0,j-1] + delta_x[j-1]
    coord[1,j] = coord[1,j-1] + delta_y[j-1]
    coord[2,j] = coord[2,j-1] + delta_z[j-1]

  disp = np.zeros(4*(len_data+1)).reshape(4,len_data+1)
  for j in range(1,len_data+1):
    disp[0,j] = coord[0,j] - coord_x0 
    disp[1,j] = coord[1,j] - coord_y0 
    disp[2,j] = coord[2,j] - coord_z0 
    disp[3,j] = np.sqrt( disp[0,j]**2 + disp[1,j]**2 + disp[2,j]**2 )

# Tecplot
# --Output 
  filename_output = dir_result+'/'+file_result+str(i+1)+'.dat'
  header  = 'variables=Time[s],x[m],y[m],z[m],disp_x[m],disp_y[m],disp_z[m],disp_mag[m]'
  cp_data = np.c_[ time_s,
                   coord[0,:],
                   coord[1,:],
                   coord[2,:],
                   disp[0,:],
                   disp[1,:],
                   disp[2,:],
                   disp[3,:]
                ]
  np.savetxt(filename_output, cp_data, header=header, delimiter='\t', comments='' )
