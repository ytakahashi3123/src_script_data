#!/usr/bin/env python3

# Scriptto extract forces from SU2 breakdown file
# Version: v1.0
# Author: Yusuke Takahashi, Hokkaido University
# Contact: ytakahashi@eng.hokudai.ac.jp
# Date: 2024/01/12

import numpy as np
import yaml as yaml
import sys as sys
import re as re

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

def main():

  # Read controlfile
  file_control = "extract_force_breakdownfile.yml"
  config = read_config_yaml(file_control)

  # ファイル名
  filename_base = config['filename_base']

  # Step information
  step_start    = config['step_start']
  step_end      = config['step_end']
  step_interval = config['step_interval']
  num_step      = (step_end-step_start)//step_interval+1

  step_digit    = config['step_digit']

  # Define time step
  #time_elapsed = config['time_step']*np.arange(0, num_step+1, 1)
  time_step    = config['time_step']*float(step_interval)
  time_elapsed = np.linspace(0, time_step*(num_step-1), num_step)

  # Set variables
  pattern_boundarygroup = re.escape(config['boundarygroup_extracted'])
  varname_extracted = config['varname_extracted']
  num_var = len(varname_extracted)

  # Extract data
  variable_extracted = np.zeros(num_step*num_var).reshape(num_step,num_var)
  for n in range(0, num_step):
    nstep        = step_start + n*step_interval
    filename_tmp = config['dirname_base'] + '/' + insert_suffix(filename_base,'_'+str(nstep).zfill(step_digit))
    print('Reading file:', filename_tmp)

    # ファイルを開いて中身を読み込む
    with open(filename_tmp, "r") as file:
      content = file.read()

    # パターン
    for m in range(0, num_var):
      pattern_varname = re.escape(varname_extracted [m])
      pattern = pattern_boundarygroup + r"[\s\S]*?" + pattern_varname + r"\s+\(\s*\d+%.*?\):\s+([-+]?\d*\.\d+|\d+)"

      # 正規表現を使ってTotal CDの値を抽出
      match = re.search(pattern, content)

      # 抽出した値を表示
      if match:
        variable_extracted[n,m] = match.group(1)
        #print(varname_extracted[m],':', variable_extracted[n,m])
      else:
        print(varname_extracted[m],"not found.")


  # Visualization
  make_directory(config['dirname_output'])
  if config['flag_output']:
    filename_tmp = config['dirname_output'] + '/' + config["filename_output"]
    file_output = open( filename_tmp , 'w')
    header_tmp  = 'Variables="Time[s]"'
    for n in range(0,num_var):
      header_tmp = header_tmp + ', ' + '"'+str(varname_extracted[n])+'"'
    header_tmp = header_tmp.rstrip(',') + '\n'
    file_output.write( header_tmp )

    text_tmp = ''
    for n in range(0,num_step):
      text_tmp = text_tmp + str(time_elapsed[n])
      for m in range(0,num_var):
        text_tmp = text_tmp + ', ' + str( variable_extracted[n,m] )
      text_tmp = text_tmp + '\n'
    file_output.write( text_tmp )
    file_output.close()

  return


if __name__ == '__main__':
  main()
  exit()
