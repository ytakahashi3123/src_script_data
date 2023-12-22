#!/usr/bin/env python3

# Author: Y.Takahashi, Hokkaido University
# Date; 2021/06/18

import numpy as np
import os as os
import shutil as shutil
import yaml as yaml
import sys as sys


def read_config_yaml(file_control):

  print("Reading control file...:", file_control)

  try:
    with open(file_control) as file:
      config = yaml.safe_load(file)
      print(config)
  except Exception as e:
    print('Exception occurred while loading YAML...', file=sys.stderr)
    print(e, file=sys.stderr)
    sys.exit(1)

  return config


def getNearestValue(list, num):
    # copied from https://qiita.com/icchi_h/items/fc0df3abb02b51f81657
    """
    概要: リストからある値に最も近い値を返却する関数
    @param list: データ配列
    @param num: 対象値
    @return 対象値に最も近い値
    """
    # リスト要素と対象値の差分を計算し最小値のインデックスを取得
    idx = np.abs(np.asarray(list) - num).argmin()
    return list[idx]
  
  
def getNearestIndex(list, num):
    # リスト要素と対象値の差分を計算し最小値のインデックスを取得し返す
    idx = np.abs(np.asarray(list) - num).argmin()
    return idx


def getNearestIndex_multivar(list, num):
    # 最短距離要素のインデクスを取る
 
    distance = []
    for i in range(len(list[0])):
      distance_tmp = 0.0
      for j in range(len(num)):
        distance_tmp = distance_tmp + ( list[j][i] - num[j] )**2
      distance.append(distance_tmp)

    idx = np.argmin( distance )
    return idx



if __name__ == '__main__':

# Read and set controlfile
  file_control="read_surfacedata.yml"
  config = read_config_yaml(file_control)


# Set parameters
  print("Setting control parameters...:")

  dir_input        = config['surfacedata']['dir_input']
  file_input       = config['surfacedata']['file_input']
  file_ext         = config['surfacedata']['file_ext']
  num_case         = config['surfacedata']['num_case']
  target_coord_x   = config['surfacedata']['target_coord_x']
  target_coord_y   = config['surfacedata']['target_coord_y']
  target_coord_z   = config['surfacedata']['target_coord_z']
  interval_message = config['surfacedata']['interval_message']
  
  num_tcoord = len(target_coord_x)
  print("Number of target cootdinate cases:",num_tcoord)

  # Referec
  dir_input_ref  = config['surfacedata']['dir_input_ref']
  file_input_ref = config['surfacedata']['file_input_ref']
  file_ext_ref   = config['surfacedata']['file_ext_ref']

  # Aerodyanmic history data
  flag_hist     = config['aero_history']['flag_hist']
  file_hist     = config['aero_history']['file_hist']
  file_hist_ext = config['aero_history']['file_hist_ext']

  # Result data
  dir_result      = config['result']['dir_result']
  file_result     = config['result']['file_result']
  file_result_ext = config['result']['file_result_ext']

  dt_cfd      = config['cfd_condition']['dt_cfd']
#  n_start_cfd = config['cfd_condition']['n_start_cfd']

  velo_inf = config['freestream_condition']['velo_inf']
  dens_inf = config['freestream_condition']['dens_inf']
  temp_inf = config['freestream_condition']['temp_inf']

  mu0_sut = config['viscosity']['mu0_sut']
  t0_sut  = config['viscosity']['t0_sut']
  c_sut   = config['viscosity']['c_sut']
  visc_inf = mu0_sut*(t0_sut + c_sut)/(temp_inf + c_sut)*(temp_inf/t0_sut)**1.5

  gamma                = config['gas_properties']['gamma']
  gas_const            = config['gas_properties']['gas_const']
  molecular_weight_air = config['gas_properties']['molecular_weight_air']
  air_const = gas_const/molecular_weight_air
  press_inf  = dens_inf*air_const*temp_inf

  length_ref = config['references']['length_ref']
  area_ref   = config['references']['area_ref']


# File output
  dir_result_path = dir_result
  if not os.path.exists(dir_result_path):
    os.mkdir(dir_result_path)
#  else:
#    shutil.rmtree(dir_result_path)
#    os.mkdir(dir_result_path)


# Read aerodynamic data (Su2 History data)
  if(flag_hist):
    filename_hist = file_hist+file_hist_ext
    print('Reading SU2 history file...:', filename_hist)
    data_aero     = np.loadtxt(filename_hist,comments=('#'),delimiter=',',skiprows=1)
    step_aero     = data_aero[:,0]
    aerocoef_cl   = data_aero[:,1]
    aerocoef_cd   = data_aero[:,2]
    aerocoef_csf  = data_aero[:,3]
    aerocoef_cmx  = data_aero[:,4]
    aerocoef_cmy  = data_aero[:,5]
    aerocoef_cmz  = data_aero[:,6]


# Read reference data to identify the target indexes on surface grid.
  filename_input = dir_input_ref+'/'+file_input_ref+file_ext_ref
  print('Reading surface data (ref.)...:', filename_input)
  data_input = np.loadtxt(filename_input,comments=('#'),delimiter=',',skiprows=1)
  coord_x    = data_input[:, 9]
  coord_y    = data_input[:,10]
  coord_z    = data_input[:,11]
  coord = [coord_x,coord_y,coord_z]

  index_nearest = []
  coord_x_ref   = []
  coord_y_ref   = []
  coord_z_ref   = []
  for n in range(0,num_tcoord):
    target_coord = [target_coord_x[n],target_coord_y[n],target_coord_z[n]]

    index_nearest_tmp = getNearestIndex_multivar(coord,target_coord)
    index_nearest.append(index_nearest_tmp)
    coord_x_ref.append(coord[0][index_nearest_tmp])
    coord_y_ref.append(coord[1][index_nearest_tmp])
    coord_z_ref.append(coord[2][index_nearest_tmp])

    print("ID target coordinate:                 ",n)
    print("Indexes of target coordinate:         ",index_nearest_tmp)
    print("Target coordinate:                    ",coord_x_ref[n],coord_y_ref[n],coord_z_ref[n])
    print("Target coordinate set in control file:",target_coord)


# Read displacement data
  for n in range(0,num_tcoord):
    index_nearest_tmp = index_nearest[n]

    time_series    = []
    coord_x_series = []
    coord_y_series = []
    coord_z_series = []
    press_series   = []
    cp_series      = []
    csf_x_series   = []
    csf_y_series   = []
    csf_z_series   = []
#  data_input_series = []

    for i in range(0,num_case):
      filename_input = dir_input+'/'+file_input+'_'+str(i)+file_ext_ref
      if( i % interval_message == 0 ): 
        print('Reading surface data...:', filename_input)
      data_input     = np.loadtxt(filename_input,comments=('#'),delimiter=',',skiprows=1)
      step     = data_input[:, 0]+1
      coord_x  = data_input[:, 9]
      coord_y  = data_input[:,10]
      coord_z  = data_input[:,11]
      press    = data_input[:,12]
#    cp       = data_input[:,13]
      csf_x    = data_input[:,14]
      csf_y    = data_input[:,15]
      csf_z    = data_input[:,16]
  
      time = dt_cfd*step
      cp   = (press - press_inf)/(0.5*dens_inf*velo_inf**2)

# Input variables for vizualization
      len_data = len(time)
      coord = [coord_x,coord_y,coord_z]

    
      time_series.append( time[0] )
      coord_x_series.append( coord_x[index_nearest_tmp] )
      coord_y_series.append( coord_y[index_nearest_tmp] )
      coord_z_series.append( coord_z[index_nearest_tmp] )
      press_series.append( press[index_nearest_tmp] )
      cp_series.append( cp[index_nearest_tmp] )
      csf_x_series.append( csf_x[index_nearest_tmp] )
      csf_y_series.append( csf_y[index_nearest_tmp] )
      csf_z_series.append( csf_z[index_nearest_tmp] )


# --Output for tecplot---
    str_x = str("{:.2e}".format(target_coord_x[n]))
    str_y = str("{:.2e}".format(target_coord_y[n]))
    str_z = str("{:.2e}".format(target_coord_z[n]))
    filename_output = dir_result+'/'+file_result+'_x'+str_x+'_y'+str_y+'_z'+str_z+file_result_ext
    print('Writing tecplot data...:', filename_output)
    header  = 'variables=Time[s],x[m],y[m],z[m],delx[m],dely[m],delz[m],Pressure[Pa],Cp,Csf_x,Csf_y,Csf_z'
    cp_data = np.c_[ time_series,
                     coord_x_series,
                     coord_y_series,
                     coord_z_series,
                     coord_x_series-coord_x_ref[n],
                     coord_y_series-coord_y_ref[n],
                     coord_z_series-coord_z_ref[n],
                     press_series,
                     cp_series,
                     csf_x_series,
                     csf_y_series,
                     csf_z_series
                   ]
    np.savetxt(filename_output, cp_data, header=header, delimiter='\t', comments='' )
