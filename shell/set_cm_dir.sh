#!/bin/bash
cd /nfs/cms/hw/apollo/
mkdir CM$1
weekly="$(date '+week%W-%m-%Y')"
cd ./CM$1
mkdir $weekly
mv /mnt/scratch/pk568/Cornell_CM_Production_Scripts/mcu_tools/data/dump_*_${2}_apollo${3}_${4}.txt ./${weekly}/
mv /mnt/scratch/pk568/Cornell_CM_Production_Scripts/mcu_tools/data/es_*_apollo${3}_${4}.log ./${weekly}/
mv /mnt/scratch/pk568/Cornell_CM_Production_Scripts/mcu_tools/data/es_*_apollo${3}_${4}.png ./${weekly}/  
cd /mnt/scratch/pk568/Cornell_CM_Production_Scripts/mcu_tools/shell/
