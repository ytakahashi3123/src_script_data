#!/usr/bin/env python3

# Script to replace nan or inf

import numpy as np
import yaml as yaml
import re as re

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


def case_insensitive_replace(input_str, target_str, replacement_str):
    # target_strを小文字に変換
    target_str_lower = target_str.lower()
    
    # input_str内のtarget_str（大文字・小文字を区別せず）をreplacement_strで置換
    result_str = input_str.replace(target_str_lower, replacement_str)
    
    return result_str


def main():

# Read controlfile
  file_control="remove_naninf.yml"
  config = read_controlfile_yaml(file_control)

  # ファイル名リスト
  list_files = config['files']
  print( len( list_files) )

  value_replaced = config['value_replaced']
  taregt_replaced = config['taregt_replaced']

  # Replaced
  for i in range(0, len( list_files) ):
    input_file  = list_files[i][0]
    output_file = list_files[i][1]
    print('Rading file:',input_file)
    with open(input_file, "r") as f_input:
      data_lines = f_input.read()
      for j in range(0,len(taregt_replaced)):
        data_lines = data_lines.replace(taregt_replaced[j], str(value_replaced))
      #data_lines = case_insensitive_replace(data_lines, "nan", str(value_replaced))

    with open(output_file, "w") as f_output:
      f_output.write(data_lines)

    print('Done:', output_file)


if __name__ == '__main__':
  
  main()

  exit()