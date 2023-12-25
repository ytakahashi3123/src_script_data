#!/usr/bin/env python3

# Script to collect aerodynamic force data
# Author: Y.Takahashi, Hokkaido University
# Date; 2023/12/12

import numpy as np

def read_config_yaml(file_control):
  import yaml as yaml
  import sys as sys

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


if __name__ == '__main__':

  # Read and set controlfile
  file_control="collect_aerodynamicforce.yml"
  config = read_config_yaml(file_control)

  # Feature values
  feature_name  = config['feature_val']['name']
  feature_value = config['feature_val']['value']
  num_feature   = len(feature_value)

  # Directory name input
  directory_input = config['directory_input']

  # Checker
  if num_feature != len(directory_input) :
    print('Number of feature value does not corresposnd to number of directory.')
    print('Program stopped.')
    exit()

  # Read data
  for n in range(0, num_feature):

    # File name
    filename_read = directory_input[n] + '/' + config['filename_input']

    # Open file
    list_boundname = []
    with open(filename_read) as f:
      lines = f.readlines()
    lines_strip = [line.strip() for line in lines]
    txt_indentified  = 'Boundary name:'
    line_both        = [(i, line) for i, line in enumerate(lines_strip) if txt_indentified in line]
    i_line, str_line = list(zip(*line_both))

    num_component  = len(i_line)
    component_name = str_line
    
    if n == 0:
      # Elements: [Directory(case), Boundary, Force kind(total,pres,visc), Force direction(x,y,z) ]
      aerodynamic_force = np.zeros(num_feature*num_component*3*3).reshape(num_feature,num_component,3,3)

    # Extract aerodynamic force from files
    list_force = []
    for m in range(0,len(i_line)):
      #print(i_line[m], str_line[m])

      str_ftotal = lines_strip[i_line[m]+1]
      str_fpres  = lines_strip[i_line[m]+2]
      str_fvisc  = lines_strip[i_line[m]+3]

      words_ftotal = str_ftotal.split()
      words_fpres  = str_fpres.split()
      words_fvisc  = str_fvisc.split()

      force_total = [ words_ftotal[0], float(words_ftotal[1]),float(words_ftotal[2]),float(words_ftotal[3]) ]
      force_pres  = [ words_fpres[0],  float(words_fpres[1]), float(words_fpres[2]), float(words_fpres[3]) ]
      force_visc  = [ words_fvisc[0],  float(words_fvisc[1]), float(words_fvisc[2]), float(words_fvisc[3]) ]

      aerodynamic_force[n,m,0,0] = float(words_ftotal[1])
      aerodynamic_force[n,m,0,1] = float(words_ftotal[2])
      aerodynamic_force[n,m,0,2] = float(words_ftotal[3])
      aerodynamic_force[n,m,1,0] = float(words_fpres[1])
      aerodynamic_force[n,m,1,1] = float(words_fpres[2])
      aerodynamic_force[n,m,1,2] = float(words_fpres[3])
      aerodynamic_force[n,m,2,0] = float(words_fvisc[1])
      aerodynamic_force[n,m,2,1] = float(words_fvisc[2])
      aerodynamic_force[n,m,2,2] = float(words_fvisc[3])

  # Output data
  filename_tmp = config['directory_output']+'/'+config['filename_output']
  print('Writing data:',filename_tmp)
  file_output = open( filename_tmp, 'w')
  header_tmp = config['header_output']+'\n'
  file_output.write( header_tmp )

  for m in range(0,num_component):
    text_tmp='zone T="'+str(component_name[m])+'", i='+str(num_feature)+' f=point'+'\n'
    for n in range(0,num_feature):
      text_force = str(feature_value[n]) + ','
      for k in range(0,3):
        text_force = text_force + str( aerodynamic_force[n,m,0,k] ) + ','
      text_tmp = text_tmp + text_force.rstrip(',') + '\n'
    file_output.write( text_tmp )
  file_output.close()