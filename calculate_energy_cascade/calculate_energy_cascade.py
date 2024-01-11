#!/usr/bin/env python3

# Program to calculate enegy spectrum
# Version: v1.0
# Author: Yusuke Takahashi, Hokkaido University
# Contact: ytakahashi@eng.hokudai.ac.jp
# Date: 2024/01/11

import numpy as np
import matplotlib.pyplot as plt
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


def get_file_extension(filename):
  # ドットで分割し、最後の要素が拡張子となる
  parts = filename.split(".")
  if len(parts) > 1:
    return parts[-1].lower()
  else:
    # ドットが含まれていない場合は拡張子が存在しない
    return None


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


def energy_spectrum(config, n_start, n_end, time_step, kind_window, str_tail, velocity, kvisccosity,length, var):

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

  # Tecplot data
  if config['fft_flag_output_tecplot'] :
    filename_tmp = config['dirname_output'] + '/' + insert_suffix(config['fft_filename_output_tecplot'], "_"+str_tail)
    print('Writing FFT file in Tecplot format...:', filename_tmp)
    header = 'variables=Wavenumber, Energyspectrum, Wavenumber_5by3, Frequency[Hz], '
    fft_data = np.c_[
                      wavenumb[1:n_sample//2]/wavenumber_kolmogorov,
                      var_fft_abs[1:n_sample//2]/factor_normalize,
                      curve_univ_turb[1:n_sample//2],
                      freqlist[1:n_sample//2]
                    ]
    np.savetxt(filename_tmp, fft_data, header=header, delimiter='\t', comments='' );


  # Image file
  if config['fft_flag_output_image'] :
    filename_tmp = config['dirname_output'] + '/' + insert_suffix(config['fft_filename_output_image'], "_"+str_tail)

    x  = wavenumb[1:n_sample//2]/wavenumber_kolmogorov
    y1 = var_fft_abs[1:n_sample//2]/factor_normalize
    y2 = curve_univ_turb[1:n_sample//2]

    # 変数プロット
    plt.plot(x, y1, label='CFD')
    plt.plot(x, y2, label='Wavenumber_5by3')
 
    # Scale
    plt.xscale('log')
    plt.yscale('log')

    # Grids
    plt.grid(which='major',color='black',linestyle='-')
    plt.grid(which='minor',color='gray',linestyle='-')

    # Title and legend
    plt.xlabel("Wavenumber")
    plt.ylabel("Energy")
    plt.title('Energy spectrum')
    plt.legend()

    # 画像を保存
    plt.savefig(filename_tmp)

    plt.close()

  return


def main():

  # Read controlfile
  file_control = "calculate_energy_cascade.yml"
  config = read_config_yaml(file_control)

#  case_aoa       = config['aoa']
  dirname_base   = config['dirname_base']
  filename_base  = config['filename_base']
  #varname_target = config['varname_target']
  varname_kind   = config['varname_kind']
  
#  num_case = len(case_aoa)
  #num_var  = len(varname_target)

  #aerodynamic_coef= np.zeros(num_var).reshape(num_var)

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
  # --Target variables
  variableindex=[]
  #for m in range(0,num_var):
  #  variableindex.append( variablename_slim.index(varname_target[m]) )
  varname_group = config['varname_group']
  num_group   = len(varname_group)
  for n in range(0,num_group):
    num_ele = len( varname_group[n] )
    for m in range(0,num_ele-1):
      variableindex.append( variablename_slim.index( varname_group[n][m] ) )
  # --Time step
  varname_timestep = config['vername_timestep']
  variableindex_timestep = variablename_slim.index( varname_timestep )

  # Reading variables
  data_input = np.loadtxt(filename_tmp,comments=('#'),delimiter=',',skiprows=2)
  #variable_list = []
  #for m in range(0,num_var):
  #  variable_list.append( data_input[:,variableindex[m] ] ) 
  #for n in range(0,num_group):
  #  num_ele = len( varname_group[n] )
  #  for m in range(0,num_ele-1):
  #    k = variablename_slim.index( varname_group[n][m] )
  #    variable_list.append( data_input[:,k ] )

  # Set elasped time
  data_step = data_input[:,variableindex_timestep]
  num_step = len( data_step )
  print('Number of step: ', num_step)
  #time_elapsed = np.zeros(num_step).reshape(num_step)
  #time_elapsed = config['time_step']*np.arange(0, num_step+1, 1)
  time_elapsed = config['time_step']*data_step

  # Input variable data
  variable_dict={}
  #for m in range(0,num_var):
  #  variable_dict[varname_target[m]] = variable_list[m]
  for n in range(0,num_group):
    num_ele = len( varname_group[n] )
    for m in range(0,num_ele-1):
      k = variablename_slim.index( varname_group[n][m] )
      variable_dict[ varname_group[n][m] ] = data_input[:,k]

  # Grouped (only varname_kind == 'velocity')
  #if varname_kind == 'velocity' :
  #  varname_group = config['varname_group']
  #  num_group   = len(varname_group)
  #  strings_group = np.zeros((num_group*3),dtype=object).reshape(num_group,3)
  #  #velocity_group = np.zeros(num_group*3).reshape(num_group,3)
  #  for n in range(0,num_group):
  #    num_ele = len( varname_group[n] )
  #    for m in range(0,num_var):
  #      for k in range(0,num_ele-1):
  #        if varname_group[n][k] == varname_target[m] :
  #          strings_group[n,k] = varname_target[m]

  # Make directory for result output
  make_directory(config['dirname_output'])

  # Energy spectrum
  if varname_kind == 'energy' :
    n_start     = config['fft_step_start']
    n_end       = config['fft_step_end']
    time_step   = config['time_step']
    kind_window = config['fft_kind_window']

    kvisccosity_ref = config['flow_kinetic_viscosity']
    length_ref      = config['flow_length']

    for n in range(0,num_group):
      str_tail = str(varname_group[n][-1])
      var_tmp  = variable_dict[ varname_group[n][0] ]
      # Energy fluctuation (approximation)
      # E = 1/2*(u*u+v*v+w*w)
      # E = var{E}+E^{\prime} = mean(E) + sqrt( var(E) ) and u = var{u}+u^{\prime}
      # Approximation: u^{\prime} is scaling to sqrt( var(E) ) -->  u^{\prime} ~ sqrt( var(E) )
      energy_fluctuation_ref = np.sqrt( np.var( var_tmp[n_start:n_end] ) )
      velocity_ref = np.sqrt( energy_fluctuation_ref )
      # Energy spectrum
      energy_spectrum( config, n_start, n_end, time_step, kind_window, str_tail, velocity_ref, kvisccosity_ref, length_ref, var_tmp )

  elif varname_kind == 'velocity' :
    n_start     = config['fft_step_start']
    n_end       = config['fft_step_end']
    time_step   = config['time_step']
    kind_window = config['fft_kind_window']

    kvisccosity_ref = config['flow_kinetic_viscosity']
    length_ref      = config['flow_length']

    # Reconstruct energy 
    for n in range(0,num_group):
      str_tail = str(varname_group[n][-1])
      u = variable_dict[ varname_group[n][0] ]
      v = variable_dict[ varname_group[n][1] ]
      w = variable_dict[ varname_group[n][2] ]
      u_ave = np.mean( u[n_start:n_end] )
      v_ave = np.mean( v[n_start:n_end] )
      w_ave = np.mean( w[n_start:n_end] )
      u_var = np.var( u[n_start:n_end] )
      v_var = np.var( v[n_start:n_end] )
      w_var = np.var( w[n_start:n_end] )
      u_fluctuation = u - u_ave
      v_fluctuation = v - v_ave
      w_fluctuation = w - w_ave
      velocity_ref = np.sqrt( u_var + v_var + w_var )
      energy_fluctuation = 0.5*( u_fluctuation**2 + v_fluctuation**2 + w_fluctuation**2 )
      energy_spectrum( config, n_start, n_end, time_step, kind_window, str_tail, velocity_ref, kvisccosity_ref, length_ref, energy_fluctuation )

  else :
    print('varname_kind is not valid, please check configuration file.')
    exit()

  # Output history
  if config['flag_output_probe']:
    filename_tmp = config['dirname_output'] + '/' + config["filename_output"]
    file_output = open( filename_tmp , 'w')
    header_tmp  = 'Variables=Time[s]'
    for n in range(0,num_group):
      num_ele = len( varname_group[n] )
      for m in range(0,num_ele-1):
        header_tmp = header_tmp + ', ' + str(varname_group[n][m])
    header_tmp = header_tmp.rstrip(',') + '\n'
    file_output.write( header_tmp )

    text_tmp = ''
    for k in range(0,num_step):
      text_tmp = text_tmp + str(time_elapsed[k])
      for n in range(0,num_group):
        num_ele = len( varname_group[n] )
        for m in range(0,num_ele-1):
          text_tmp = text_tmp + ', ' + str( variable_dict[ varname_group[n][m]][k] )
      text_tmp = text_tmp + '\n'
    file_output.write( text_tmp )
    file_output.close()

  return


if __name__ == '__main__':
  main()
  exit()
