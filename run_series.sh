#!/bin/bash

   . run_series.h

   DIR_CUR=$(pwd)
   LD1=$DIR_CUR/convert_vtk2tec/convert_vtk2tec.sh
   LD2=$DIR_CUR/read_aoa.py

   for (( i = 0; i < ${#MACH[*]}; i++ ))
   {
  	   for (( j = 0; j < ${#PRES[*]}; j++ ))
  	   {
  	       PRES_zeropad=$( printf "%05d" "${PRES[j]}" )
           DIR_CASE=${DIR_COMMON}_m${MACH[i]}_p${PRES_zeropad}
           echo $DIR_CASE

           cd $DIR_CASE
           cp $DIR_CUR/convert_vtk2tec/convert_vtk2tec.h ./
           cp $DIR_CUR/read_aoa.yml ./
           $LD1
           $LD2
           cd -
  	   }
   }

   exit
