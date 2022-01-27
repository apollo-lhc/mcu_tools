#!/bin/bash
cd /nfs/cms/hw/apollo/
mkdir CM$1
weekly="$(date '+week%W-%m-%Y')"
cd ./CM$1
mkdir $weekly
cd /mnt/scratch/pk568/Cornell_CM_Production_Scripts/mcu_tools/python 

