#!/usr/bin/env python
# coding: utf-8

# 
#  convert CSV file from google docs to yaml
# 

import pandas as pd
import numpy as np
import yaml

df = pd.read_csv('CM uC Sensor register map - V1 reformat.csv', sep=',')
# get rid of columns that are not in the core data
df.drop(["Unnamed: 7", "Unnamed: 8", "Unnamed: 9"], 1, inplace=True)

# this removes undefined devices 
df.dropna(axis=0, subset=['Device name'],inplace=True)

# set up the indices
df.set_index(['Device name', 'Desc1'])
df.reindex(pd.MultiIndex.from_tuples(zip(df['Device name'], df['Desc1'])))

# convert to a nested set of dictionaries
data = df.groupby('Device name').apply(
    lambda x: x.set_index('Sensor ID').to_dict(orient='index')).to_dict()

# add a top-level set of data with metadata
toplevel = {'name':'MCU to Zynq register list', 'version':1}
toplevel['sensors'] = data
with open(f"mcu_zynq_regist_v{toplevel['version']}.yaml", "w") as f:
    yaml.dump(toplevel, f, sort_keys=False)
