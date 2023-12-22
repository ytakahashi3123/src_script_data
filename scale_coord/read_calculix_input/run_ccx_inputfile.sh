#!/bin/bash

  . run_ccx_inputfile.h

# Convert unit of coordinates
  $LD > $LOG

# 準備
#---　コントロールファイルの1列目・2行目を取り出す: ex:FEMMeshNetgen.inp  
  COORD_FILE_ORIG=$(cat $INP | awk '{print $1}' | awk 'NR==2')
  echo ${COORD_FILE_ORIG}
#---　コントロールファイルの1列目・3行目を取り出す: ex: flap_coord.inp	
  COORD_FILE=$(cat $INP | awk '{print $1}' | awk 'NR==3')
  echo ${COORD_FILE}
#--- 行数
  NUM_COL=$(cat ${COORD_FILE} | wc -l)
  echo ${NUM_COL}

# 古い座標データを削除し置き換える
#---削除
  LINE_S=6
  LINE_E=$((${NUM_COL}+${LINE_S}))
#   CHAR_SED=$(echo \'${LINE_S},${LINE_E}d\')
  sed ${LINE_S},${LINE_E}d $COORD_FILE_ORIG > $CCX_FILE

#---追加
  COORD_NEW=$(echo *INCLUDE,INPUT=${CCX_WORKDIR_FSI}${COORD_FILE})
  sed -i '5a\'${COORD_NEW} $CCX_FILE


# 境界名を置き換える（FreeCADの仕様）
  BD_REP_S=FemConstraintFixed001
  BD_REP_E=Nsurface
#   echo \'s/${BD_REP_S}/${BD_:q!REP_E}/g\'
  sed -i -e s/${BD_REP_S}/${BD_REP_E}/g $CCX_FILE


# 最後に出現したBOUNDARYをCLOADに変更
  cat $CCX_FILE | tac | sed -e '1,/BOUNDARY/ s/BOUNDARY/CLOAD/' | tac > ${CCX_FILE}_tmp
  mv ${CCX_FILE}_tmp ${CCX_FILE}


# いくつかの置換・追加作業
#---ヤング率を変更する
  LINE_TMP=$(echo $(sed -n '/*ELASTIC/=' $CCX_FILE))
  LINE_TMP=$((${LINE_TMP}+1))
  sed -i ${LINE_TMP}d $CCX_FILE
  sed -i ${LINE_TMP}i\ ${young_module},${poisson_ratio} $CCX_FILE

  LINE_TMP=$((${LINE_TMP}+1))
  sed -i ${LINE_TMP}i\ '*DENSITY' $CCX_FILE
  LINE_TMP=$((${LINE_TMP}+1))
  sed -i ${LINE_TMP}i\ ${density_mat} $CCX_FILE

#---計算制御パラメータ
# FreeCADデフォルトの
#---------------
# *STEP
# *STATIC
#---------------
# をいかのように変更にする
#---------------
# *STEP,INC=1000000
# *DYNAMIC, DIRECT
# 5E-4, 1e-1
#---------------
  CHAR_PREV=$(echo *STEP)
  CHAR_NEW=$(echo *STEP,INC=1000000)
  sed -i -e s/${CHAR_PREV}/${CHAR_NEW}/g $CCX_FILE

  CHAR_PREV=$(echo *STATIC)
  CHAR_NEW=$(echo *DYNAMIC,DIRECT)
  sed -i -e s/${CHAR_PREV}/${CHAR_NEW}/g $CCX_FILE

  LINE_TMP=$(echo $(sed -n '/*DYNAMIC,DIRECT/=' $CCX_FILE))
  sed -i ${LINE_TMP}a\ ${time_step},${time_max} $CCX_FILE

  exit
