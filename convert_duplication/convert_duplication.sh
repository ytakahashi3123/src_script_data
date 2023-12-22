#!/bin/bash

   . convert_duplication.h

   cp ${HISTORY_FILE_ORG} ${HISTORY_FILE_MOD}

# 行頭に追加
#   sed -i -e "1s/^/VARIABLES=/" ${HISTORY_FILE_MOD}

# 重複行の削除
   cat ${HISTORY_FILE_MOD} | tac | awk '!a[$1]++' | tac > ${HISTORY_FILE_MOD}_tmp
   mv ${HISTORY_FILE_MOD}_tmp ${HISTORY_FILE_MOD}

   exit
