#!/bin/bash
   #module load oneapi/2021.3
   #module load BaseCPU
   #source /opt/intel/oneapi/setvars.sh

   SOURCE=read_calculix_input.f90
   BIN_NAME=read_calculix_input
#   COMP=ifort
   COMP=gfortran
   OPT=
   
   $COMP $OPT -o $BIN_NAME $SOURCE

   exit
