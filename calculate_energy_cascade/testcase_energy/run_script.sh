#!/bin/bash -x

PYTHON_RUN=python3.9
DIR=..
LD=$DIR/calculate_energy_cascade.py
LOG=log_calculate_energy_cascade

$PYTHON_RUN $LD > $LOG

