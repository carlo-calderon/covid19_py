# -*- coding: utf-8 -*-
"""
Created on Thu May 14 23:34:05 2020

@author: Carlo
"""

import pandas as pd
import numpy as np

data = pd.read_csv('../COVID19-Chile/output/producto1/Covid-19.csv', index_col=2)
print(data)
print(data.columns)
cases = data[data.columns[4:-2]]

tot = pd.core.frame.DataFrame()
comunas = []
for row in data.iterrows():
    name = row[0]
    #print('agregando:', name)
    m = row[1][4:-1].to_frame()
    m['Fecha'] = m.index
    m=m.rename(columns={name:'cases'})
    m['Region'] = row[1]['Region']
    m['Comuna'] = name
    m['Poblacion'] = row[1]['Poblacion']
    s = m['cases']
    m['new_cases'] = s.subtract(s.shift(1), fill_value=0)
    
    #print(m)
    #break
    comunas.append(m)
    
#    break

tot = pd.concat(comunas)    
print('Total------')
print(tot)
tot.to_csv('./tot.csv', index=False)   
#print(data)
#print(data.iloc[0:1, 4:-1].T)
#print(type(data), data.columns)