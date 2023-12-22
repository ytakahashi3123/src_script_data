#!/bin/bash

dir_name=set_case_$(date "+%Y%m%d-%H%M%S")
mkdir $dir_name
cd $dir_name

mkdir fluid solid
cp -pri ../fluid/*cfg ./fluid/
cp -pri ../solid/*inp ./solid/
cp -prid ../config.yml ../log* ../*dat ../*vtk ../*log ../*sh ../precice-config* ./

exit
