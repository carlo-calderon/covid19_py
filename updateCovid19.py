# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 17:29:17 2020

@author: Carlo
"""
# data contiene la información por paises y fechas, es un dict
# data (nombre pais) -> datos por fecha
#                       fecha -> {'cases': 0, 'deaths': 0, 'recovered': 0,
#                                 'cases_acc': 0, 'deaths_acc': 0, 'recovered_acc': 0}
#Ejemplo: data['Chile'][3/25/20]['cases'] => Caosos confirmados acumulados en chile el 25 de marzo de 2020

import csv
from datetime import date, timedelta
from os import listdir
import pandas as pd
from collections import OrderedDict

def prevDate(f):
    sf = tuple(map(lambda x: int(x), f.split('/')))
    f_ant = date(2000+ sf[2], sf[0], sf[1]) - timedelta(days=1)
    return '{0:d}/{1:d}/{2:d}'.format(f_ant.month, f_ant.day, f_ant.year-2000)

def matrix2Table(filename_in, row_name, column_name, value_name, filename_out):
    f_writer = open(filename_out, 'w', newline='', encoding='utf-8')
    writer = csv.writer(f_writer)
    writer.writerow([row_name, column_name, value_name])
    with open(filename_in, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not(row_name in row.keys()):
                continue
            for key in row.keys():
                if key == row_name:
                    continue
                writer.writerow([row[row_name], key, row[key]])
    f_writer.close()
def matrix2MultiTable(filename_in, rows_names, column_name, value_name, filename_out):
    f_writer = open(filename_out, 'w', newline='', encoding='utf-8')
    writer = csv.writer(f_writer)
    writer.writerow(list(rows_names + [column_name, value_name]))
    with open(filename_in, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not(rows_names[0] in row.keys()):
                continue
            for key in row.keys():
                if key in rows_names:
                    continue
                new_row = []
                for row_name in rows_names:
                    new_row.append(row[row_name])
                new_row = new_row + [key, row[key]]
                writer.writerow(new_row)
    f_writer.close()
    
def prevDateCl(f):
    sf = tuple(map(lambda x: int(x), f.split('-')))
    f_ant = date(sf[0], sf[1], sf[2]) - timedelta(days=1)
    return f_ant.strftime('%Y-%m-%d')

def fillCountries(filename):
    countries = dict()
    with open(filename, newline='') as f_confirmed:
        reader = csv.DictReader(f_confirmed)
        for row in reader:
            if not(row['Country_Region'] in countries.keys()):
                countries[row['Country_Region']] = {'iso3': row['iso3'],'iso2': row['iso2'], 'Lat': row['Lat'], 'Long': row['Long_'], 'popData2018': 1}
    return countries

def fillData(filename, tag, countries, data):
    with open(filename, newline='') as f_confirmed:
        reader = csv.DictReader(f_confirmed)
        for row in reader:
            if not(row['Country/Region'] in data.keys()):
                data[row['Country/Region']] = dict()
            if not(row['Country/Region'] in countries.keys()):
                countries[row['Country/Region']] = dict()
                countries[row['Country/Region']]['Lat']=row['Lat']
                countries[row['Country/Region']]['Long']=row['Long']
                countries[row['Country/Region']]['iso3']=row['Country/Region'][0:3]
                countries[row['Country/Region']]['iso2']=row['Country/Region'][0:2]
                countries[row['Country/Region']]['popData2018']=1
    
            for key in row.keys():
                if key == 'Province/State' or key == 'Country/Region' or key == 'Lat' or key == 'Long':
                    continue
                if not(key in data[row['Country/Region']].keys()):
                    data[row['Country/Region']][key] = {'cases': 0, 'deaths': 0, 'recovered': 0,
                                                        'cases_acc': 0, 'deaths_acc': 0, 'recovered_acc': 0}
                data[row['Country/Region']][key][tag] = data[row['Country/Region']][key][tag] + int(row[key])
                
def fillDifferences(data, column, column_dif, prev_date = prevDate):
    for country in data.keys():
        for f in data[country].keys():
            #print(country, f)
            f_ant = prev_date(f)
            if not(f_ant in data[country].keys()):
                data[country][f][column_dif] = data[country][f][column]
            else:
                data[country][f][column_dif] = data[country][f][column] - data[country][f_ant][column]
    return data

def addRowToDict(data_dict, columns, row):
    for i in range(len(columns)):
        c = columns[i]
        if not c in data_dict.keys():
            data_dict[c] = []
        data_dict[c].append(row[i])
    
def createDataFrame(countries, data, header):
    print('Creando dataFrame...')
    data_dict = {}
    for country in countries.keys():
        if not(country in data.keys()):
            continue
        for d in data[country].keys():
            fecha = tuple(map(lambda x: int(x), d.split('/')))
            fecha = date(2000 + fecha[2], fecha[0], fecha[1])
            row= [fecha.strftime('%d/%m/%Y'), fecha.day, fecha.month, fecha.year, 
                  data[country][d]['cases'], data[country][d]['deaths'], data[country][d]['recovered'], 
                  data[country][d]['cases_acc'], data[country][d]['deaths_acc'], data[country][d]['recovered_acc'], 
                  country, countries[country]['iso2'], countries[country]['iso3'], countries[country]['popData2018']]
            addRowToDict(data_dict, header, row)
    df = pd.DataFrame(data_dict)
    print('... dataFrame OK.')
    return df

def corregirPeak(data, column, column_acc, date_peak, date_ini,
                 group='Region', c_date='Fecha', l_filtro=None, column_w=None):
    print('Corrigiendo peak: {}, {}, {}'.format(column, column_acc, date_peak))
    if column_w is None:
        column_w = column
    regiones = data[group].unique()
    data['ajuste'] = 0
    data['ajuste'] = data.ajuste.astype('int32')
    data['ajuste_acc'] = 0
    data['ajuste_acc'] = data.ajuste_acc.astype('int32')
    # print(regiones)
    for region in regiones:
        if not(l_filtro is None) and not(region in l_filtro):
            continue
        filtro = data[data[group] == region]
        npeak = filtro[filtro[c_date] == date_peak][column]
        nprev = filtro[filtro.index == npeak.index[0]-1][column]
        # if nprev.values[0] >= npeak.values[0]:
        #     continue
        filtro = filtro[filtro[c_date] < date_peak]
        filtro = filtro[filtro[c_date] >= date_ini]
        acumulados = filtro[column].sum()#filtro[filtro.index == nprev.index[0]][column_acc].values[0]
        if acumulados<1 and acumulados>-1:
            continue
        a_repartir = npeak.values[0] - nprev.values[0]
        filtro.ajuste = filtro[column_w] * (a_repartir / acumulados)
        filtro.ajuste = filtro.ajuste.astype('int32')
        filtro.ajuste_acc = filtro.ajuste.cumsum()
        agregados = filtro.ajuste.sum()
        print('\t {}: peak={}, acc={}, repartir={}, agregados={}'.format(region, npeak.values[0], acumulados, a_repartir, agregados))
        data.at[npeak.index[0], 'ajuste'] = -agregados
        # print(region, data.at[npeak.index[0], 'ajuste'])
        # print(filtro.cases.sum(), ':[', npeak.values[0], nprev.values[0], npeak.values[0]-agregados, ']', acumulados, a_repartir, agregados)
        data.update(filtro)
    data[column] = data[column] + data.ajuste
    data[column_acc] = data[column_acc] + data.ajuste_acc
    data = data.drop(columns=['ajuste', 'ajuste_acc'])
    return data

def addMovilMean(data, column, new_column, group, window=7):
    regiones = data[group].unique()
    data[new_column] = 0
    for region in regiones:
        data['temp'] = data[data[group] == region][column].rolling(window).mean().fillna(0)
        data['temp'] = data['temp'].fillna(0)
        data[new_column] = data[new_column] + data['temp']
    
def updateCovid19World():
    countries = fillCountries('../COVID-19/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv')
    data = dict()
    
    path_data = '../COVID-19/csse_covid_19_data/csse_covid_19_time_series/' 
    fillData(path_data + 'time_series_covid19_confirmed_global.csv', 'cases_acc', countries, data)
    fillData(path_data + 'time_series_covid19_deaths_global.csv', 'deaths_acc', countries, data)
    fillData(path_data + 'time_series_covid19_recovered_global.csv', 'recovered_acc', countries, data)
    
    fillDifferences(data, 'cases_acc', 'cases')
    fillDifferences(data, 'deaths_acc', 'deaths')
    fillDifferences(data, 'recovered_acc', 'recovered')
    
    header = ['dateRep', 'day', 'month', 'year', 'cases', 'deaths', 'recovered',
              'cases_acc', 'deaths_acc', 'recovered_acc', 'countriesAndTerritories',
              'geoId', 'countryterritoryCode', 'popData2018']
    
    df = createDataFrame(countries, data, header)
    df['Fecha'] = df.year.astype('str') + '-' + df.month.astype('str').str.zfill(2) + '-' + df.day.astype('str').str.zfill(2)
    addMovilMean(df, 'cases', 'cases_7d', 'countriesAndTerritories', 7)
    addMovilMean(df, 'deaths', 'deaths_7d', 'countriesAndTerritories', 7)
    header = header + ['cases_7d', 'deaths_7d']
    
    corregirPeak(df, 'cases', 'cases_acc', '2020-06-17', '2020-01-01',
                 group='countriesAndTerritories', l_filtro=['Chile'])
    corregirPeak(df, 'cases', 'cases_acc', '2020-04-12', '2020-01-01',
                 group='countriesAndTerritories', l_filtro=['France'])
    corregirPeak(df, 'cases', 'cases_acc', '2020-04-24', '2020-01-01',
                  group='countriesAndTerritories', l_filtro=['Spain'])
    corregirPeak(df, 'cases', 'cases_acc', '2020-07-18', '2020-01-01',
                  group='countriesAndTerritories', l_filtro=['Kyrgyzstan'])
    corregirPeak(df, 'cases', 'cases_acc', '2020-08-02', '2020-03-01', 
                  group='countriesAndTerritories', l_filtro=['Peru'], column_w='cases_7d')
    corregirPeak(df, 'cases', 'cases_acc', '2020-10-05', '2020-01-01', 
                  group='countriesAndTerritories', l_filtro=['Mexico'], column_w='cases_7d')
    
    corregirPeak(df, 'deaths', 'deaths_acc', '2020-06-08', '2020-01-01', 
                  group='countriesAndTerritories', l_filtro=['Chile'])
    corregirPeak(df, 'deaths', 'deaths_acc', '2020-07-17', '2020-01-01', 
                  group='countriesAndTerritories', l_filtro=['Chile'])
    corregirPeak(df, 'deaths', 'deaths_acc', '2020-05-25', '2020-01-01', 
                  group='countriesAndTerritories', l_filtro=['Spain'])
    corregirPeak(df, 'deaths', 'deaths_acc', '2020-06-19', '2020-01-01', 
                  group='countriesAndTerritories', l_filtro=['Spain'])
    corregirPeak(df, 'deaths', 'deaths_acc', '2020-06-16', '2020-01-01', 
                  group='countriesAndTerritories', l_filtro=['India'])
    corregirPeak(df, 'deaths', 'deaths_acc', '2020-06-25', '2020-01-01', 
                  group='countriesAndTerritories', l_filtro=['US'])
    corregirPeak(df, 'deaths', 'deaths_acc', '2020-07-23', '2020-01-01', 
                  group='countriesAndTerritories', l_filtro=['Peru'])
    corregirPeak(df, 'deaths', 'deaths_acc', '2020-07-22', '2020-01-01', 
                  group='countriesAndTerritories', l_filtro=['South Africa'])
    corregirPeak(df, 'deaths', 'deaths_acc', '2020-07-18', '2020-01-01', 
                  group='countriesAndTerritories', l_filtro=['Kyrgyzstan'])
    corregirPeak(df, 'deaths', 'deaths_acc', '2020-05-18', '2020-03-01',
                  group='countriesAndTerritories', l_filtro=['US'])
    corregirPeak(df, 'deaths', 'deaths_acc', '2020-06-14', '2020-03-01', 
                  group='countriesAndTerritories', l_filtro=['Peru'])
    corregirPeak(df, 'deaths', 'deaths_acc', '2020-07-27', '2020-03-01', 
                  group='countriesAndTerritories', l_filtro=['Peru'])
    corregirPeak(df, 'deaths', 'deaths_acc', '2020-08-14', '2020-03-01', 
                  group='countriesAndTerritories', l_filtro=['Peru'], column_w='deaths_7d')
    corregirPeak(df, 'deaths', 'deaths_acc', '2020-09-07', '2020-05-01', 
                  group='countriesAndTerritories', l_filtro=['Ecuador'], column_w='deaths_7d')
    corregirPeak(df, 'deaths', 'deaths_acc', '2020-09-07', '2020-05-01', 
                  group='countriesAndTerritories', l_filtro=['Bolivia'], column_w='deaths_7d')
    corregirPeak(df, 'deaths', 'deaths_acc', '2020-10-01', '2020-01-01', 
                  group='countriesAndTerritories', l_filtro=['Argentina'], column_w='deaths_7d')
    corregirPeak(df, 'deaths', 'deaths_acc', '2020-10-05', '2020-01-01', 
                  group='countriesAndTerritories', l_filtro=['Mexico'], column_w='deaths_7d')
    
    df = df.convert_dtypes()
    print(df)
    print(header)
    df.to_csv('../covid19.csv', index=False, columns=header)           
    print(list(df['countriesAndTerritories'].unique()))

## BD CHILE
data_empty = {'cases': 0, 'deaths': 0, 'recovered': 0, 'cases_acc': 0, 'deaths_acc': 0, 'recovered_acc': 0,
              'pcr': 0, 'uci': 0}

def fillDataCl(filename, data_cl, tag):
    with open(filename, newline='', encoding='utf-8') as f_confirmed_cl:
        reader = csv.DictReader(f_confirmed_cl)
        for row in reader:
            if not(row['Region'] in data_cl.keys()):
                if row['Region'] == 'Total':
                    continue
                data_cl[row['Region']] = dict()
            for key in row.keys():
                if key == 'Region' or key == 'Poblacion' or key =='Codigo region':
                    continue
                if not(key in data_cl[row['Region']].keys()):
                    data_cl[row['Region']][key] = dict(data_empty)
                value = 0
                if len(row[key])>0:
                    value = int(row[key])
                data_cl[row['Region']][key][tag] = value

def fillDataDetalleCl(filename, data_cl, fecha, tags):
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                if not(row['Region'] in data_cl.keys()):
                    if row['Region'] == 'Total' or row['Region'] == 'Se desconoce region de origen':
                        continue
                    data_cl[row['Region']] = dict()
                if not(fecha in data_cl[row['Region']].keys()):
                    data_cl[row['Region']][fecha] = dict(data_empty)
                for tag in tags:
                    if tag in row.keys():
                        if len(row[tag])>0:
                            n=int(float(row[tag]))
                        else:
                            n=0
                        data_cl[row['Region']][fecha][tags[tag]] = n
            except:
                print('ERROR:', fecha, row.keys())
                print(row['Region'], tags)
                    
def fillRecoveredCl(filename, data_cl, region, tag):
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Fecha'] != 'Casos recuperados':
                continue
            for key in row.keys():
                if key == 'Fecha' or not(key in data_cl[region].keys()):
                    continue
                # print(key, '"', row[key], '"', len(row[key]))
                if len(row[key])>0:
                    data_cl[region][key][tag] = int(float(row[key]))
                else:
                    data_cl[region][key][tag] = 0
                    
def fillPopCl(filename, data_cl, name_column, name_new_column):
    data = pd.read_csv(filename)
    for row in data.itertuples():
        pop = data[data.Region==row.Region].iloc[0][name_column]
        for f in data_cl[row.Region]:
            data_cl[row.Region][f][name_new_column] = pop
            
def createDataFrameCl(data, header):
    columnas = ['Region', 'Fecha', 'dateRep', 'day', 'month', 'year'] + header
    df = pd.DataFrame(columns=columnas)
    print('Creando dataFrame...')
    data_dict = {}
    for c in columnas:
        data_dict[c] = []
    for region, dates in data.items():
        for fecha, datos in dates.items():
            try:
                [year, month, day] = fecha.split('-')
                data_dict['Region'].append(region)
                data_dict['Fecha'].append(fecha)
                data_dict['dateRep'].append('{0:s}/{1:s}/{2:s}'.format(day, month, year))
                data_dict['day'].append(int(day))
                data_dict['month'].append(int(month))
                data_dict['year'].append(int(year))
                for h in header:
                    data_dict[h].append(datos[h])
            except:
                print('Error:', region, fecha)
                print(datos)
    df = pd.DataFrame(data_dict)
    print('... dataFrame OK.')
    return df

updateCovid19World()

#corregirCL()
path_p4 = '../tmp/cl_producto4/'
data_cl = dict()
matrix2Table('../COVID19-Chile/output/producto9/HospitalizadosUCIEtario.csv',
             'Grupo de edad', 'Fecha', 'UCI',
             '../tmp/HospitalizadosUCIEtario.csv')
matrix2Table('../COVID19-Chile/output/producto10/FallecidosEtario.csv',
             'Grupo de edad', 'Fecha', 'Fallecidos',
             '../tmp/FallecidosEtario.csv')
matrix2MultiTable('../COVID19-Chile/output/producto16/CasosGeneroEtario.csv',
                  ['Grupo de edad', 'Sexo'], 'Fecha', 'Cases',
                  '../tmp/CasosGeneroEtario.csv')

for f in listdir(path_p4):
    fecha=f[0:10]
    print(f, fecha, len(data_cl.keys()))
    if len(f)<10 or f[0:3] != '202':
        continue
    fillDataDetalleCl(path_p4 + f, data_cl, fecha,
                    {'Casos totales': 'cases_acc', 'Fallecidos': 'deaths_acc', 'Casos recuperados': 'recovered_acc'})

fillRecoveredCl('../COVID19-Chile/output/producto5/TotalesNacionales.csv', data_cl, 'Metropolitana', 'recovered_acc')
# print('recovered', len(data_cl.keys()), data_cl.keys())
fillPopCl('../tmp/PCR.csv', data_cl, 'Poblacion', 'popData2018')
# print('pop', len(data_cl.keys()), data_cl.keys())
fillDataCl('../tmp/PCR.csv', data_cl, 'pcr')
# print('pcr', len(data_cl.keys()), data_cl.keys())
fillDataCl('../tmp/UCI.csv', data_cl, 'uci')
# print('uci', len(data_cl.keys()), data_cl.keys())

fillDifferences(data_cl, 'cases_acc', 'cases', prevDateCl)
fillDifferences(data_cl, 'deaths_acc', 'deaths', prevDateCl)
fillDifferences(data_cl, 'recovered_acc', 'recovered', prevDateCl)
# print(data_cl['Metropolitana'])
# print(data_cl)


header = ['Region', 'dateRep', 'day', 'month', 'year', 'cases', 'deaths', 'recovered',
          'cases_acc', 'deaths_acc', 'recovered_acc', 'popData2018', 'pcr', 'uci']
df_cl = createDataFrameCl(data_cl, header[5:])
corregirPeak(df_cl, 'cases', 'cases_acc', '2020-06-17', '2020-01-01')
corregirPeak(df_cl, 'deaths', 'deaths_acc', '2020-06-07', '2020-01-01')
corregirPeak(df_cl, 'deaths', 'deaths_acc', '2020-07-17', '2020-01-01')
corregirPeak(df_cl, 'deaths', 'deaths_acc', '2020-07-17', '2020-05-01')
df_cl = df_cl.convert_dtypes()

print(df_cl.dtypes)
df_cl.to_csv('../covid19_cl_pd.csv', index=False)
df_cl.to_csv('../covid19_cl.csv', index=False, columns=header)
