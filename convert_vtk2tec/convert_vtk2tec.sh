#!/bin/bash

   . convert_vtk2tec.h

   cp ${HISTORY_FILE_VTK} ${HISTORY_FILE_TEC}

# 行頭に追加
   sed -i -e "1s/^/VARIABLES=/" ${HISTORY_FILE_TEC}

# 重複行の削除
   cat ${HISTORY_FILE_TEC} | tac | awk '!a[$1]++' | tac > ${HISTORY_FILE_TEC}_tmp
   mv ${HISTORY_FILE_TEC}_tmp ${HISTORY_FILE_TEC}

   exit
