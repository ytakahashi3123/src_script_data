#!/usr/bin/python3
##!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3
##!/usr/local/python3.6.2/bin/python3
import numpy as np
import os as os
import shutil as shutil
#import module_functions as mf

def str2bool(s):
     return s.lower() in ["true", "t", "yes", "1"]

# ------------------------------------
# ---Read control file----------------
data_control = np.genfromtxt("read_aero.ctl", comments=('#'), dtype='str')
dir_input      = str( data_control[0] )
file_input     = str( data_control[1] )
dir_result     = str( data_control[2] )
file_result    = str( data_control[3] )

# CFD information
dt_cfd             = float( data_control[4] )
n_moving_start_cfd = int( data_control[5] )
mass_cfd           = float( data_control[6] )
moi_cfd            = float( data_control[7] )

# Freestream
num_count_tmp  = 7
velo_inf = float( data_control[num_count_tmp+1] )
dens_inf = float( data_control[num_count_tmp+2] )
temp_inf = float( data_control[num_count_tmp+3] )

# Viscosity
num_count_tmp  = num_count_tmp + 3
mu0_sut = float( data_control[num_count_tmp+1] )
t0_sut  = float( data_control[num_count_tmp+2] )
c_sut   = float( data_control[num_count_tmp+3] )
visc_inf = mu0_sut*(t0_sut + c_sut)/(temp_inf + c_sut)*(temp_inf/t0_sut)**1.5

# Gas properties
num_count_tmp  = num_count_tmp + 3
gamma                = float( data_control[num_count_tmp+1] )
gas_const            = float( data_control[num_count_tmp+2] )
molecular_weight_air = float( data_control[num_count_tmp+3] )
air_const = gas_const/molecular_weight_air
pres_inf = dens_inf*air_const*temp_inf

# Reference
num_count_tmp  = num_count_tmp + 3
length_ref = float( data_control[num_count_tmp+1] )
area_ref   = float( data_control[num_count_tmp+2] )

# Data proc
num_count_tmp = num_count_tmp + 2
aoa_ref       = float( data_control[num_count_tmp+1] )

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
data_aero = np.loadtxt(dir_input+'/'+file_input,comments=('#'),delimiter=',',skiprows=2)
#step  = data_input[:,0]
#aoa   = data_input[:,1]
#omega = data_input[:,2]
#fx    = data_input[:,3]
#y    = data_input[:,4]
#fz    = data_input[:,5]
#cx    = data_input[:,6]
#cy    = data_input[:,7] # CM
#cz    = data_input[:,8]
#Cd     = data_input[:, 8]
#Cl     = data_input[:, 9]
#Cm     = data_input[:,12]
step_aero     = data_aero[:,0]
aerocoef_cl   = data_aero[:,1]
aerocoef_cd   = data_aero[:,2]
aerocoef_csf  = data_aero[:,3]
aerocoef_cmx  = data_aero[:,4]
aerocoef_cmy  = data_aero[:,5]
aerocoef_cmz  = data_aero[:,6]

time      = step_aero*dt_cfd
time_ins  = time[:] - time[0] + dt_cfd

len_data = len(time_ins)
time_s = np.zeros(len_data+1).reshape(len_data+1)
time_s[0] = 0
time_s[1:len_data+1] = time_ins[0:len_data]

aerocoef = np.zeros(6*(len_data+1)).reshape(6,len_data+1)
for j in range(1,len_data+1):
  aerocoef[0,j] = aerocoef_cl[j-1]
  aerocoef[1,j] = aerocoef_cd[j-1]
  aerocoef[2,j] = aerocoef_csf[j-1]
  aerocoef[3,j] = aerocoef_cmx[j-1]
  aerocoef[4,j] = aerocoef_cmy[j-1]
  aerocoef[5,j] = aerocoef_cmz[j-1]

#aoa_deg   = aoa*180.0/np.pi
#omega_deg = omega*180.0/np.pi
#Cm        = (cy)/(0.5*dens_inf*velo_inf**2*area_ref*length_ref)
#aoa_deg = - amplitude * np.sin( angularVelocity * time )
#aoa     =   aoa_deg * np.pi/180

# Tecplot
# --Output 
#header  = 'variables=Time[s],AoA[deg],AngularVelocity[deg/s],CD,CL,CM'
header  = 'variables=Time[s],CL,CD,CSF,CMx,CMy,CMz'
#cp_data = np.c_[ time[index_min:index_max]-time[index_min],
#                 aoa_deg[index_min:index_max],
#                 omega_deg[index_min:index_max],
#                 Cd[index_min:index_max],
#                 Cl[index_min:index_max],
#                 Cm[index_min:index_max],
#                ]
cp_data = np.c_[ time_s,
                 aerocoef[0,:],
                 aerocoef[1,:],
                 aerocoef[2,:],
                 aerocoef[3,:],
                 aerocoef[4,:],
                 aerocoef[5,:]
                ]
np.savetxt(dir_result+'/'+file_result+'.dat', cp_data, header=header, delimiter='\t', comments='' )
