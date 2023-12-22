#!/usr/bin/env python3

# Program to read history data
# Version: v1.0
# Author: Yusuke Takahashi, Hokkaido University
# Contact: ytakahashi@eng.hokudai.ac.jp
# Date: 2023/05/02

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


def main():

  # Read controlfile
  file_control = "read_history.yml"
  config = read_config_yaml(file_control)

  case_aoa       = config['aoa']
  dirname_base   = config['dirname_base']
  filename_base  = config['filename_base']
  varname_target = config['varname_target']
  
  num_case = len(case_aoa)
  num_var  = len(varname_target)

  aerodynamic_coef= np.zeros(num_case*num_var).reshape(num_case,num_var)
  for n in range(0,num_case):
    # Open file
    addfile = str( case_aoa[n] ).zfill(2)
    print(addfile,n)
    filename_tmp = dirname_base+addfile +'/'+ filename_base
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
      aerodynamic_coef[n,m] = data_input[-1,variableindex[m]]

  variable_dict={}
  for m in range(0,num_var):
    variable_dict[varname_target[m]] = aerodynamic_coef[:,m]

  # Output
  filename_tmp = config["filename_output"]
  file_output = open( filename_tmp , 'w')
  header_tmp  = 'Variables=AOA[deg]'
  for m in range(0,num_var):
    header_tmp = header_tmp + ', ' + str(varname_target[m])
  header_tmp = header_tmp.rstrip(',') + '\n'
  file_output.write( header_tmp )
  for n in range(0,num_case):
    text_tmp = str( case_aoa[n] )
    for m in range(0,num_var):
      text_tmp = text_tmp + ', ' + str( variable_dict[varname_target[m]][n] )
    text_tmp = text_tmp + '\n'
    file_output.write( text_tmp )
  file_output.close()

  return


if __name__ == '__main__':
  main()
  exit()
