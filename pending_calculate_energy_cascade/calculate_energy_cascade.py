#!/usr/bin/env python3

# Program to calculate enegy spectrum
# Version: v1.0
# Author: Yusuke Takahashi, Hokkaido University
# Contact: ytakahashi@eng.hokudai.ac.jp
# Date: 2023/12/22

import numpy as np
import yaml as yaml
import sys as sys

# Read control file
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


def make_directory(dir_path):
  import os as os
  import shutil as shutil
  if not os.path.exists(dir_path):
    os.mkdir(dir_path)
  #else:
  #  shutil.rmtree(dir_path)
  #  os.mkdir(dir_path)
  return


def insert_suffix(filename, suffix):
  parts = filename.split('.')
  if len(parts) == 2:
    new_filename = f"{parts[0]}{suffix}.{parts[1]}"
    return new_filename
  else:
    # ファイル名が拡張子を含まない場合の処理
    return filename + suffix


def zero_pad_number(number, length=3):
    """
    Zero-pad the given number to the specified length.

    Parameters:
    - number: The number to be zero-padded.
    - length: The desired length of the resulting string, including zero-padding.

    Returns:
    - Zero-padded string representation of the number.
    """
    return f"{number:0{length}d}"


def energy_spectrum(config, str_tail, var):

  n_start     = config['fft_step_start']
  n_end       = config['fft_step_end']
  time_step   = config['time_step']
  outputfile  = config['fft_filename_output']
  kind_window = config['fft_kind_window']
  velocity    = config['flow_velocity']
  kvisccosity = config['flow_kinetic_viscosity']
  length      = config['flow_length']

  # Energy dissipation (=energy input rate)
  eps = (velocity**3)/length 
  # --Kolmogorov time
  time_kolmogorov = np.sqrt((kvisccosity)/eps)
  # --Kolmogorov length
  length_kolmogorov = ((kvisccosity)**3/eps)**(1/4)
  # --Kolmogorov velocity
  velocity_kolmogorov = (kvisccosity*eps)**(1/4)
  # --Kolmogorov wavenumber
  wavenumber_kolmogorov = eps**(1/4)*kvisccosity**(-3/4)

  print('Kolmogorov scale:')
  print('Time:      ',time_kolmogorov)
  print('Length:    ',length_kolmogorov)
  print('Velocity:  ',velocity_kolmogorov)
  #print('Wavenumber:',wavenumber_kolmogorov)

  n_sample      = len(var[n_start:n_end])
  sampling_freq = 1.0/time_step

  #Window function
  if kind_window == "hamming":
    window  = np.hamming(n_sample)   # ハミング窓
  elif kind_window == "hanning":
    window  = np.hanning(n_sample)   # ハニング窓
  elif kind_window == "blackman":
    window = np.blackman(n_sample)  # ブラックマン窓
  elif kind_window == "bartlett":
    window = np.bartlett(n_sample)  # バートレット窓
  else :
    print("Error: kind of window function is not sapported:", kind_window)
    print("Hanning window function is used.")
    window  = np.hanning(n_sample)   # ハニング窓

  #窓補正
  window_correct=1.0/(sum(window)/n_sample)

  #FFT (入力波とフーリエ変化した振幅を対応させるために，フーリエ変換後の振幅をデータ数/2で割っている)
  freqlist = np.fft.fftfreq(n=n_sample, d=time_step)
  wavenumb = 2*np.pi*freqlist

  var_window    = window*var[n_start:n_end]
  var_fft       = np.fft.fft(var_window)
  var_fft_abs_native = np.abs(var_fft[0:n_sample//2])*window_correct

  var_fft_abs    = 2.0*var_fft_abs_native/(float(n_sample))
  var_fft_abs[0] =     var_fft_abs[0]/2.0

#  var_fft_power = (var_fft_abs)**2
#  var_fft_power =  ((var_fft_abs)**2)/(float(n_sample))

  # Factor for normilization
  factor_normalize = eps**(1/4)*kvisccosity**(5/4)
  # Universal function
  curve_univ_turb = config['kolmogorov_constant']*eps**(2/3)*(wavenumb/wavenumber_kolmogorov)**(-5/3)

  filename_tmp = config['dirname_output'] + '/' + insert_suffix(outputfile, "_"+str_tail)
  print('Writing FFT file...:', filename_tmp)
  header = 'variables=Wavenumber, Energyspectrum, Wavenumber_5by3, Frequency[Hz], '
  fft_data = np.c_[
                    wavenumb[1:n_sample//2]/wavenumber_kolmogorov,
                    var_fft_abs[1:n_sample//2]/factor_normalize,
                    curve_univ_turb[1:n_sample//2],
                    freqlist[1:n_sample//2]
                  ]
  np.savetxt(filename_tmp, fft_data, header=header, delimiter='\t', comments='' );


def main():

  # Read controlfile
  file_control = "calculate_energy_cascade.yml"
  config = read_config_yaml(file_control)

#  case_aoa       = config['aoa']
  dirname_base   = config['dirname_base']
  filename_base  = config['filename_base']
  varname_target = config['varname_target']
  
#  num_case = len(case_aoa)
  num_var  = len(varname_target)

  aerodynamic_coef= np.zeros(num_var).reshape(num_var)

  # Open file
  filename_tmp = dirname_base +'/'+ filename_base
  print('Reading file: ', filename_tmp)

  # Check header
  with open(filename_tmp) as f:
    lines = f.readlines()[1]
  variablename = [char.strip() for char in lines.split(',') ]
  variablename_slim = []
  for m in range(0,len(variablename) ):
    variablename_slim.append(variablename[m].strip('"'))
  # Check index matching target name
  variableindex=[]
  for m in range(0,num_var):
    variableindex.append( variablename_slim.index(varname_target[m]) )

  # Reading variables
  data_input = np.loadtxt(filename_tmp,comments=('#'),delimiter=',',skiprows=2)
  variable_list = []
  for m in range(0,num_var):
    variable_list.append( data_input[:,variableindex[m] ] ) 

  # Set elasped time
  num_step = len(data_input[:,0])
  print('Number of step: ', num_step)
  #time_elapsed = np.zeros(num_step).reshape(num_step)
  time_elapsed = config['time_step']*np.arange(0, num_step+1, 1)

  # Input variable data
  variable_dict={}
  for m in range(0,num_var):
    variable_dict[varname_target[m]] = variable_list[m]

  # Make directory for result output
  make_directory(config['dirname_output'])

  # Energy spectrum
  for m in range(0,num_var):
    str_tail=str(varname_target[m])
    var_fft = variable_dict[varname_target[m]]
    energy_spectrum( config, str_tail, var_fft )

  # Output history
  filename_tmp = config['dirname_output'] + '/' + config["filename_output"]
  file_output = open( filename_tmp , 'w')
  header_tmp  = 'Variables=Time[s]'
  for m in range(0,num_var):
    header_tmp = header_tmp + ', ' + str(varname_target[m])
  header_tmp = header_tmp.rstrip(',') + '\n'
  file_output.write( header_tmp )

  text_tmp = ''
  for n in range(0,num_step):
    text_tmp = text_tmp + str(time_elapsed[n])
    for m in range(0,num_var):
      text_tmp = text_tmp + ', ' + str( variable_dict[varname_target[m]][n] )
    text_tmp = text_tmp + '\n'
  file_output.write( text_tmp )
  file_output.close()

  return


if __name__ == '__main__':
  main()
  exit()
