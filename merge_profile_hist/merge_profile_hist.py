#!/usr/bin/env python3
##!/usr/bin/python3
##!/usr/local/python3.6.2/bin/python3
##!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3
import numpy as np
import os as os
import shutil as shutil
import yaml as yaml
import sys as sys

# ---Function---
def str2bool(s):
     return s.lower() in ["true", "t", "yes", "1"]


# ---Read control file----
def read_controlfile(file_control):

#  global dir_input, file_input, num_case, file_hist, dir_result, file_result
#  global dt_cfd, n_start_cfd

#--Reading file--
  data_control = np.genfromtxt(file_control, comments=('#'), dtype='str')
  print("Reading control file...:", file_control)

#--Files--
  dir_input   = str( data_control[0] )
  file_input  = str( data_control[1] )
  num_case    = int( data_control[2] )
  dir_result  = str( data_control[3] )
  file_result = str( data_control[4] )
  
#--CFD information--
  num_count_tmp  = 4
  dt_cfd      = float( data_control[num_count_tmp+1] )
  n_start_cfd = int( data_control[num_count_tmp+2] )


def read_controlfile_yaml(file_control):

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


def set_parameter(config):

  global dir_input, file_input, num_case, file_hist, dir_result, file_result
  global dt_cfd, n_start_cfd

  print("Setting control parameters...:")

  print(yaml.dump(config))

  dir_input   = config['file_names_surface']['dir_input']
  file_input  = config['file_names_surface']['file_input']
  num_case    = config['file_names_surface']['num_case']
  dir_result  = config['file_names_surface']['dir_result']
  file_result = config['file_names_surface']['file_result']

  dt_cfd      = config['cfd_condition']['dt_cfd']
  n_start_cfd = config['cfd_condition']['n_start_cfd']

# ---FFT routine----
def fft_routine(n_start, n_end, time_step, var, outputfile, header):

  n_sample      = len(var[n_start:n_end])
  sampling_freq = 1.0/time_step

#Window function
  hammingWindow  = np.hamming(n_sample)   # ハミング窓
  hanningWindow  = np.hanning(n_sample)   # ハニング窓
  blackmanWindow = np.blackman(n_sample)  # ブラックマン窓
  bartlettWindow = np.bartlett(n_sample)  # バートレット窓

#FFT (入力波とフーリエ変化した振幅を対応させるために，フーリエ変換後の振幅をデータ数/2で割っている)
  freqlist = np.fft.fftfreq(n=n_sample, d=time_step)
  wavenumb = 2*np.pi*freqlist

  var_window    = hammingWindow*var[n_start:n_end]
  var_fft       = np.fft.fft(var_window[n_start:n_end])
  var_fft_abs   = np.abs(var_fft[0:n_sample//2])
  var_fft_power = (var_fft_abs)**2

  print('Writing FFT file...:', outputfile)
  fft_data = np.c_[
                    freqlist[0:n_sample//2], 
                    var_fft_abs[0:n_sample//2]
                  ]
  np.savetxt(outputfile, fft_data, header=header, delimiter='\t', comments='' );

# -----------------------------------------------------------
# -----Main routine -----------------------------------------
# -----------------------------------------------------------
if __name__ == '__main__':

# Read controlfile
  file_control="merge_profile_hist.yml"
  config = read_controlfile_yaml(file_control)
  set_parameter(config)

# ---File output---
  dir_result_path = dir_result
  if not os.path.exists(dir_result_path):
    os.mkdir(dir_result_path)
  else:
    shutil.rmtree(dir_result_path)
    os.mkdir(dir_result_path)

# ---Read displacement data---
# ファイルの行数を取得する
  filename_input = dir_input+'/'+file_input+'_0'+'.csv'
  count_lines = 0
  with open(filename_input) as f:
    for line in f:
      count_lines += 1

  count_lines = count_lines - 1 #ヘッダをスキップ
  print('Number of lines of CSV file', count_lines)

# ファイル読み込み＆時系列データ格納
  filename_output = dir_result+'/'+file_result+'.dat'
  with open(filename_output, 'a') as file_object:
    header = 'variables=x[m],Cp\n'
    file_object.write(header)

    for i in range(0,num_case):
      filename_input = dir_input+'/'+file_input+'_'+str(i)+'.csv'
      print('Reading surface profile file...:', filename_input)
  
      data_input  = np.loadtxt(filename_input,comments=('#'),delimiter=',',skiprows=1)
      step      = data_input[:, 0]
      len_array = len(step)
      time      = dt_cfd*(step+1)
  
      density   = data_input[:, 1]
      energy    = data_input[:, 2]
      gridvel_x = data_input[:, 3]
      gridvel_y = data_input[:, 4]
      gridvel_z = data_input[:, 5]
      headflux  = data_input[:, 6]
      viscos_l  = data_input[:, 7]
      machnum   = data_input[:, 8]
      coord_x   = data_input[:, 9]
      coord_y   = data_input[:,10]
      coord_z   = data_input[:,11]
      pres      = data_input[:,12]
      pres_coef = data_input[:,13]
      skinfric_coef_x = data_input[:,14]
      skinfric_coef_y = data_input[:,15]
      skinfric_coef_z = data_input[:,16]
      temperature = data_input[:,17]
      moment_x    = data_input[:,18]
      moment_y    = data_input[:,19]
      moment_z    = data_input[:,21]
      yplus       = data_input[:,20] # なぜか順番がいれかわっている模様
      length_arc  = data_input[:,22]
  
      list_tmp = []
      for j in range(0,len_array):
        list_tmp.append(coord_x[j])
        list_tmp.append(pres_coef[j])
#      print(str( list_tmp)[1:-1] )

# Output
      file_object.write( 'zone t="'+str(time[0])+'s"\n' )
      file_object.write( str( list_tmp )[1:-1]  )
      file_object.write( '\n' )
