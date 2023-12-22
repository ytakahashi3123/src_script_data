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
#  global velo_inf, dens_inf, temp_inf
#  global visc_inf
#  global pres_inf
#  global length_ref, area_ref
#  global coord_ref, coord_axis_ref

#--Reading file--
  data_control = np.genfromtxt(file_control, comments=('#'), dtype='str')
  print("Reading control file...:", file_control)

#--Files--
  dir_input   = str( data_control[0] )
  file_input  = str( data_control[1] )
  num_case    = int( data_control[2] )
  file_hist   = str( data_control[3] )
  dir_result  = str( data_control[4] )
  file_result = str( data_control[5] )
  
#--CFD information--
  num_count_tmp  = 5
  dt_cfd      = float( data_control[num_count_tmp+1] )
  n_start_cfd = int( data_control[num_count_tmp+2] )
  
#--Freestream--
  num_count_tmp  = num_count_tmp + 2
  velo_inf = float( data_control[num_count_tmp+1] )
  dens_inf = float( data_control[num_count_tmp+2] )
  temp_inf = float( data_control[num_count_tmp+3] )
  
#--Viscosity--
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
  pres_inf  = dens_inf*air_const*temp_inf
  
# Reference
  num_count_tmp  = num_count_tmp + 3
  length_ref = float( data_control[num_count_tmp+1] )
  area_ref   = float( data_control[num_count_tmp+2] )

# Data proc
  num_count_tmp = num_count_tmp + 2
  coord_ref      = float( data_control[num_count_tmp+1] )
  coord_axis_ref = int( data_control[num_count_tmp+2] )


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


def set_parameter(config):

  global dir_input, file_input, num_case, file_hist, dir_result, file_result
  global flag_cycleprocess
  global dt_cfd, n_start_cfd
  global velo_inf, dens_inf, temp_inf
  global visc_inf
  global pres_inf
  global length_ref, area_ref
  global coord_ref, coord_axis_ref

  print("Setting control parameters...:")

  dir_input         = config['file_names_precicelog']['dir_input']
  file_input        = config['file_names_precicelog']['file_input']
  num_case          = config['file_names_precicelog']['num_case']
  flag_cycleprocess = config['file_names_precicelog']['flag_cycleprocess']
  file_hist         = config['file_names_aero']['file_hist']
  dir_result        = config['file_names_result']['dir_result']
  file_result       = config['file_names_result']['file_result']

  dt_cfd      = config['cfd_condition']['dt_cfd']
  n_start_cfd = config['cfd_condition']['n_start_cfd']

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
  pres_inf  = dens_inf*air_const*temp_inf

  length_ref = config['references']['length_ref']
  area_ref   = config['references']['area_ref']

  coord_ref      = config['coord_condition']['coord_ref']
  coord_axis_ref = config['coord_condition']['coord_axis_ref']


# ---FFT routine----
def fft_routine(n_start, n_end, time_step, var, outputfile, header):

  n_sample      = len(var[n_start:n_end])
  sampling_freq = 1.0/time_step

#Window function
  kind_window = "hanning"
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
  var_fft       = np.fft.fft(var_window[n_start:n_end])
  var_fft_abs_native = np.abs(var_fft[0:n_sample//2])*window_correct

  var_fft_abs    = 2.0*var_fft_abs_native/(float(n_sample))
  var_fft_abs[0] =     var_fft_abs[0]/2.0

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

# Read and set controlfile
#  file_control="read_aoa.ctl"
#  read_controlfile(file_control)
  file_control="read_aoa.yml"
  config = read_config_yaml(file_control)
  set_parameter(config)

# ---File output---
  dir_result_path = dir_result
  if not os.path.exists(dir_result_path):
    os.mkdir(dir_result_path)
  else:
    shutil.rmtree(dir_result_path)
    os.mkdir(dir_result_path)

# ---Read aerodynamic data (Su2 History data)---
  filename_hist = dir_input+'/'+file_hist+'.dat'
  print('Reading SU2 history file...:', filename_hist)
  data_aero     = np.loadtxt(filename_hist,comments=('#'),delimiter=',',skiprows=2)
  step_aero     = data_aero[:,0]
  aerocoef_cl   = data_aero[:,9]
  aerocoef_cd   = data_aero[:,10]
  aerocoef_csf  = data_aero[:,11]
  aerocoef_cmx  = data_aero[:,12]
  aerocoef_cmy  = data_aero[:,13]
  aerocoef_cmz  = data_aero[:,14]

# ---Read displacement data---
  for i in range(0,num_case):
    filename_input = dir_input+'/'+file_input+str(i+1)+'.log'
    print('Reading preCICE watchpoint file...:', filename_input)
    data_input     = np.loadtxt(filename_input,comments=('#'),delimiter=None,skiprows=1)
    time     = data_input[:,0]
    delta_x  = data_input[:,3]
    delta_y  = data_input[:,4]
#    delta_z  = data_input[:,6]
    force_x  = data_input[:,5]
    force_y  = data_input[:,6]
#    force_z  = data_input[:,9]
  
    coord_x0 = data_input[0,1]
    coord_y0 = data_input[0,2]
#    coord_z0 = data_input[0,3]
  
# Input variables for vizualization
    print('Calculating displacements and coordinates...')

    len_data = len(time)
  
    time_s = np.zeros(len_data+1).reshape(len_data+1)
    time_s[0] = 0
    time_s[1:len_data+1] = time[0:len_data]
  
    coord = np.zeros(3*(len_data+1)).reshape(3,len_data+1)
    coord[0,0] = coord_x0
    coord[1,0] = coord_y0
#    coord[2,0] = coord_z0
    for j in range(1,len_data+1):
      coord[0,j] = coord[0,j-1] + delta_x[j-1]
      coord[1,j] = coord[1,j-1] + delta_y[j-1]
#      coord[2,j] = coord[2,j-1] + delta_z[j-1]
  
    disp = np.zeros(4*(len_data+1)).reshape(4,len_data+1)
    for j in range(1,len_data+1):
      disp[0,j] = coord[0,j] - coord_x0 
      disp[1,j] = coord[1,j] - coord_y0 
#      disp[2,j] = coord[2,j] - coord_z0 
#      disp[3,j] = np.sqrt( disp[0,j]**2 + disp[1,j]**2 + disp[2,j]**2 )
      disp[2,j] = np.sqrt( disp[0,j]**2 + disp[1,j]**2 )

    aerocoef = np.zeros(6*(len_data+1)).reshape(6,len_data+1)
    for j in range(1,len_data+1):
      aerocoef[0,j] = aerocoef_cl[j-1]
      aerocoef[1,j] = aerocoef_cd[j-1]
      aerocoef[2,j] = aerocoef_csf[j-1]
      aerocoef[3,j] = aerocoef_cmx[j-1]
      aerocoef[4,j] = aerocoef_cmy[j-1]
      aerocoef[5,j] = aerocoef_cmz[j-1]

# --Output for tecplot---
    filename_output = dir_result+'/'+file_result+str(i+1)+'.dat'
#    header  = 'variables=Time[s],x[m],y[m],z[m],disp_x[m],disp_y[m],disp_z[m],disp_mag[m],CL,CD,CSF,CMx,CMy,CMz'
    header  = 'variables=Time[s],x[m],y[m],disp_x[m],disp_y[m],disp_mag[m],CL,CD,CSF,CMx,CMy,CMz'
    cp_data = np.c_[ time_s[:],
                     coord[0,:],
                     coord[1,:],
#                     coord[2,:],
                     disp[0,:],
                     disp[1,:],
                     disp[2,:],
#                     disp[3,:],
                     aerocoef[0,:],
                     aerocoef[1,:],
                     aerocoef[2,:],
                     aerocoef[3,:],
                     aerocoef[4,:],
                     aerocoef[5,:]
                   ]
    np.savetxt(filename_output, cp_data, header=header, delimiter='\t', comments='' )

    print('End displacements and coordinates calculations...')

#--FFT
    print('Starting FFT routine...')
    n_start_fft    = 0
    n_end_fft      = len_data+1
    time_step_fft  = dt_cfd
    var_fft        = coord[coord_axis_ref,:]
    outputfile_fft = dir_result+'/'+file_result+'_fft_'+str(i+1)+'.dat'
    header_fft     =  'variables=frequency[Hz], fft_var(Disp.)'
    fft_routine( n_start_fft, n_end_fft, time_step_fft, var_fft, outputfile_fft, header_fft )
    print('End FFT routine...')

# 基準AoAで一周期とする
#--半周期の数・ステップを取得
    if(flag_cycleprocess):
      index_min = 0
      index_max = len_data+1
      print(index_min,index_max)
  
      num_period_twice  = 0
      step_period_twice = []
      for j in range(index_min, index_max-1):
        if np.sign( coord[coord_axis_ref,j+1]-coord_ref ) != np.sign( coord[coord_axis_ref,j]-coord_ref ) :
          num_period_twice = num_period_twice + 1
          step_period_twice.append(j)
#          print(step_period_twice[num_period_twice-1])
  
  # --周期の数、ステップを取得
      step_period      = step_period_twice[::2]
      step_period_half = step_period_twice[1::2]
      num_period       = num_period_twice//2
      for j in range(0,num_period):
        print( "Period ID, Step (FSI):",j, step_period[j],step_period_half[j] )
    
      time_start = time[index_min]
      time_mod   = time - time_start
  
  # 周期ごとの処理
      with open(dir_result+'/'+'log_perioddata', 'w') as f:
        for j in range(0,num_period):
          step_period_start = step_period[j]
          step_period_end   = step_period[j+1]
    #    step_period_half  = step_period_half[i]
  
    # AoA decrease, AoA increase
          list_tmp = coord[coord_axis_ref,step_period_start:step_period_end]
          step_aoa_max = np.argmax( list_tmp ) + step_period_start
          step_aoa_min = np.argmin( list_tmp ) + step_period_start

#-- variables
          time_period     = time_mod[step_period_end] - time_mod[step_period_start]
          freq_period     = 1.0/time_period
          coord_min_period = coord[coord_axis_ref,step_aoa_min]
          coord_max_period = coord[coord_axis_ref,step_aoa_max]

  # Monitoring
  # --Zero padding
          number_padded = '{0:03d}'.format(j+1)

          print("------------")
          print( "Cycle          ", number_padded )
          print( "Step          :", step_period_start, ":", step_period_end )
          print( "Time [s]      :", time_mod[step_period_start], ":", time_mod[step_period_end] )
          print( "Period [s]    :", time_period )
          print( "Frequency [Hz]:", freq_period )
          print( "Min disp. [m] :", coord_min_period )
          print( "Max disp. [m] :", coord_max_period )
          print("------------")
  
          print("------------", file=f )
          print( "Cycle          ", number_padded, file=f )
          print( "Step          :", step_period_start, ":", step_period_end, file=f )
          print( "Time [s]      :", time_mod[step_period_start], ":", time_mod[step_period_end], file=f )
          print( "Period [s]    :", time_period, file=f )
          print( "Frequency [Hz]:", freq_period, file=f )
          print( "Min disp. [m] :", coord_min_period, file=f )
          print( "Max disp. [m] :", coord_max_period, file=f )
          print("------------", file=f )

  # Output data to Tecplot format
  # --Output 
#          header  = 'variables=Time[s],x[m],y[m],z[m],CL,CD,CSF,CMx,CMy,CMz'
          header  = 'variables=Time[s],x[m],y[m],CL,CD,CSF,CMx,CMy,CMz'
          cp_data = np.c_[ time_s[step_period_start:step_period_end],
                           coord[0,step_period_start:step_period_end],
                           coord[1,step_period_start:step_period_end],
#                           coord[2,step_period_start:step_period_end],
                           aerocoef[0,step_period_start:step_period_end],
                           aerocoef[1,step_period_start:step_period_end],
                           aerocoef[2,step_period_start:step_period_end],
                           aerocoef[3,step_period_start:step_period_end],
                           aerocoef[4,step_period_start:step_period_end],
                           aerocoef[5,step_period_start:step_period_end]
#                           aerocoef_cl[step_period_start:step_period_end],
#                           aerocoef_cd[step_period_start:step_period_end],
#                           aerocoef_csf[step_period_start:step_period_end],
#                           aerocoef_cmx[step_period_start:step_period_end],
#                           aerocoef_cmy[step_period_start:step_period_end],
#                           aerocoef_cmz[step_period_start:step_period_end]
                          ]
          np.savetxt(dir_result+'/'+file_result+'_cycle'+str(number_padded)+'.dat', cp_data, header=header, delimiter='\t', comments='' )

