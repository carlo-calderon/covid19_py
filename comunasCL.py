# -*- coding: utf-8 -*-
"""
Created on Thu May 14 23:34:05 2020

@author: Carlo
"""

import pandas as pd
import numpy as np

data = pd.read_csv('./COVID19-Chile/output/producto1/Covid-19.csv', index_col=2)
print(data)
print(data.columns)
data['Comuna'] = data.index
cases = data[data.columns[4:-2]]

tot = pd.core.frame.DataFrame()
comunas = []
for i in range(cases.shape[0]):
    name = cases.index[i]
    #print('agregando:', i, name)
    m = cases[i:i+1].T
    m['Fecha'] = m.index
    m=m.rename(columns={name:'cases'})
    row = data[data['Comuna']==name]
    m['Region'] = row['Region'].iloc[0]
    m['Comuna'] = name
    m['Poblacion'] = row['Poblacion'].iloc[0]
    s = m['cases']
    m['new_cases'] = s.subtract(s.shift(1), fill_value=0)
    
    comunas.append(m)
    
#    break

tot = pd.concat(comunas)    
print('Total------')
print(tot)
tot.to_csv('./tot.csv', index=False)   
#print(data)
#print(data.iloc[0:1, 4:-1].T)
#print(type(data), data.columns)