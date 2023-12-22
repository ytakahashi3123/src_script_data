#!/usr/bin/env python3

import numpy as np
import os as os
import shutil as shutil
import yaml as yaml

rad2deg = 180.0/np.pi
deg2rad = np.pi/180.0


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



if __name__ == '__main__':

  # Read and set controlfile
  file_control="read_aero_static.yml"
  config = read_config_yaml(file_control)


  # Read input data
  filename_tmp = config['file_names_aero']['dir_input'] + '/' + config['file_names_aero']['file_hist']
  # --Header setting
  with open(filename_tmp) as f:
    lines = f.readlines()
  
  # リストとして取得 
  lines_strip = [line.strip() for line in lines]

  # カンマとスペースを削除
  words = lines_strip[1].replace(',', ' ').replace('"', ' ').split()

  post_var   = config['post_process']['post_var']
  post_index = []
  for i in range( 0,len(post_var) ):
    for n in range( 0,len(words) ):
      if post_var[i] == words[n] :
        post_index.append(n)
        #print( post_var[i], words[n], i, n)
        break

  # --Data
  data_aero = np.loadtxt(filename_tmp,comments=('#'),delimiter=',',skiprows=2)

  #config['post_process']['post_var']['0']
  post_list = []
  for n in range( 0,len(post_var) ):
    post_list.append( data_aero[:,post_index[n] ] )

  step_aero     = post_list[0]
  aerocoef_cd   = post_list[1]
  aerocoef_cl   = post_list[2]
  aerocoef_cs   = post_list[3]
  aerocoef_cmx  = post_list[4]
  aerocoef_cmy  = post_list[5]
  aerocoef_cmz  = post_list[6]

  time  = step_aero * config['cfd_condition']['dt_cfd']
  #time_ins  = time[:] - time[0] + dt_cfd

  #len_data = len(time_ins)
  #time_s = np.zeros(len_data+1).reshape(len_data+1)
  #time_s[0] = 0
  #time_s[1:len_data+1] = time_ins[0:len_data]

  #aerocoef = np.zeros(6*(len_data+1)).reshape(6,len_data+1)
  #for j in range(1,len_data+1):
  #  aerocoef[0,j] = aerocoef_cl[j-1]
  #  aerocoef[1,j] = aerocoef_cd[j-1]
  #  aerocoef[2,j] = aerocoef_cs[j-1]
  #  aerocoef[3,j] = aerocoef_cmx[j-1]
  #  aerocoef[4,j] = aerocoef_cmy[j-1]
  #  aerocoef[5,j] = aerocoef_cmz[j-1]
  
  #omegax = post_list[7]
  #omegay = post_list[8]
  #omegaz = post_list[9]

  # Integration omega to calculate angle
  #angle_init = config['gridrot_condition']['angle_init']
  #angle = np.zeros(3*len(time)).reshape(3,len(time))
  #angle[0,0] = angle_init[0]
  #angle[1,0] = angle_init[1]
  #angle[2,0] = angle_init[2]
  #for n in range( 1,len(time) ):
  #  dt = (time[n] - time[n-1])
  #  angle[0,n] = angle[0,n-1] + 0.5*(omegax[n]+omegax[n-1])*dt
  #  angle[1,n] = angle[1,n-1] + 0.5*(omegay[n]+omegay[n-1])*dt
  #  angle[2,n] = angle[2,n-1] + 0.5*(omegaz[n]+omegaz[n-1])*dt
  #  #print(time[n],angle[2,n]*rad2deg)

  # Calculate mean and STD
  index_start_tmp = getNearestIndex(time, config['data_mean_std']['time_start'])
  index_end_tmp   = getNearestIndex(time, config['data_mean_std']['time_end'])      
  print("Calculate mean and STD values between",time[index_start_tmp],"to",time[index_end_tmp],"s")

  mean_list = []
  std_list  = []
  for n in range( 0,len(post_var) ):
    mean_list.append( np.mean( post_list[n][index_start_tmp:index_end_tmp] ) )
    std_list.append( np.std( post_list[n][index_start_tmp:index_end_tmp] ) )

  for n in range( 1,len(post_var) ):
    print("Name   : ", post_var[n])
    print("--Mean : ", mean_list[n])
    print("--STD  : ",std_list[n])

  # Output
  dir_result_path = config['file_names_result']['dir_result'] 
  if not os.path.exists(dir_result_path):
    os.mkdir(dir_result_path)
  else:
    shutil.rmtree(dir_result_path)
    os.mkdir(dir_result_path)
    
  # Tecplot
  filename_tmp = config['file_names_result']['dir_result'] +'/'+ config['file_names_result']['file_result']
  print('Writing tecplot file: ',filename_tmp)
  #header  = 'variables=Time[s],CD,CL,CSF,CMx,CMy,CMz,OmegaX[rad/s],OmegaY[rad/s],OmegaZ[rad/s],AngleX[deg],AngleY[deg],AngleZ[deg]'
  header  = 'variables=Time[s],CD,CL,CSF,CMx,CMy,CMz'
  cp_data = np.c_[ time,
                   aerocoef_cd,
                   aerocoef_cl,
                   aerocoef_cs,
                   aerocoef_cmx,
                   aerocoef_cmy,
                   aerocoef_cmz,
                   #omegax,
                   #omegaz,
                   #omegaz,
                   #angle[0,:]*rad2deg,
                   #angle[1,:]*rad2deg,
                   #angle[2,:]*rad2deg
                  ]
  #cp_data = post_list 
  np.savetxt(filename_tmp, cp_data, header=header, delimiter='\t', comments='' )
