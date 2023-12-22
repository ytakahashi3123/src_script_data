#!/bin/bash
   module load oneapi/2021.3

   SOURCE=read_calculix_input.f90
   BIN_NAME=read_calculix_input
   COMP=ifort
   OPT=

   #source /opt/intel/compilers_and_libraries/linux/bin/compilervars.sh intel64
   
   $COMP $OPT -o $BIN_NAME $SOURCE

   exit
