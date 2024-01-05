#!/usr/bin/env python3

# Script to merge files

import numpy as np
import yaml as yaml

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


def main():

# Read controlfile
  file_control="merge_files.yml"
  config = read_controlfile_yaml(file_control)

  # 入力ファイル名リスト
  #input_files = ["history_00000.dat", "history_00001.dat", ..., "history_01000.dat"]
  input_files = config['input_files']

  # それぞれ何行目まで読むか
  input_numlines = config['input_numlines']

  # 出力ファイル名
  output_file = config['output_file']

  # Fileの行数をチェック
  for i, input_file in enumerate(input_files):
    # 入力ファイルを開く
    with open(input_file, "r") as input:
      lines = input.readlines()
      line_count = len(lines)
      print(f"The number of lines in {input_file} is: {line_count}")

  # 出力ファイルを開く
  with open(output_file, "w") as output:
    # 各入力ファイルを順に処理
    for i, input_file in enumerate(input_files):
      # 入力ファイルを開く
      with open(input_file, "r") as input:
        # 最初のファイルの場合、最初の2行をそのまま出力
        if i == 0:
          header = next(input)  # ヘッダーの1行目を読み取る
          output.write(header)  # ヘッダーの1行目を出力
          header = next(input)  # ヘッダーの2行目を読み取る
          output.write(header)  # ヘッダーの2行目を出力
        # それ以外のファイルは最初の2行を無視して内容を出力
        else:
          next(input)  # ヘッダーの1行目を読み飛ばす
          next(input)  # ヘッダーの2行目を読み飛ばす
        #for _ in range(100):
        #    output.write(next(input))
        # データ部分を読み込み、NaNやInfを0.0に置換して出力
        for line in input:
          data = np.fromstring(line, sep=",") # スペースで区切られた数値をNumPy配列に変換
          data_cleaned = np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0)  # NaNやInfを0.0に置換
          output.write(",".join(map(str, data_cleaned)) + "\n")  # 置換後のデータを出力
        #output.write(input.read())  # ファイルの内容を出力
        #for _ in range(100)
        #  line = next(input)
        #  data = np.fromstring(line, sep=",") # スペースで区切られた数値をNumPy配列に変換
        #  data_cleaned = np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0)  # NaNやInfを0.0に置換
        #  output.write(",".join(map(str, data_cleaned)) + "\n")  # 置換後のデータを出力

    print("Combined history files into", output_file)


if __name__ == '__main__':
  
  main()

  exit()