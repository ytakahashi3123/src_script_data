#!/bin/bash

DIR=~/source/sample_precice/src_script/src_script/scale_coord/read_calculix_input
LD=${DIR}/run_ccx_inputfile.sh
LOG=log_scale

$LD > $LOG
