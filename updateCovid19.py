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
    
countries = fillCountries('../COVID-19/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv')
data = dict()

path_data = '../COVID-19/csse_covid_19_data/csse_covid_19_time_series/' 
fillData(path_data + 'time_series_covid19_confirmed_global.csv', 'cases_acc', countries, data)
fillData(path_data + 'time_series_covid19_deaths_global.csv', 'deaths_acc', countries, data)
fillData(path_data + 'time_series_covid19_recovered_global.csv', 'recovered_acc', countries, data)

fillDifferences(data, 'cases_acc', 'cases')
fillDifferences(data, 'deaths_acc', 'deaths')
fillDifferences(data, 'recovered_acc', 'recovered')
            
print(countries)
print('----------------CHILE----------------')
print(data['Chile'])
print('=====================================')

with open('../covid19.csv', 'w', newline='', encoding='utf-8') as f_writer:
    header = ['dateRep', 'day', 'month', 'year', 'cases', 'deaths', 'recovered',
              'cases_acc', 'deaths_acc', 'recovered_acc', 'countriesAndTerritories',
              'geoId', 'countryterritoryCode', 'popData2018']
    writer = csv.writer(f_writer)
    writer.writerow(header)
    for country in countries.keys():
        if not(country in data.keys()):
            continue
        for d in data[country].keys():
            fecha = tuple(map(lambda x: int(x), d.split('/')))
            fecha = date(2000 + fecha[2], fecha[0], fecha[1])
            try:
                row= [fecha.strftime('%d/%m/%Y'), fecha.day, fecha.month, fecha.year, 
                      data[country][d]['cases'], data[country][d]['deaths'], data[country][d]['recovered'], 
                      data[country][d]['cases_acc'], data[country][d]['deaths_acc'], data[country][d]['recovered_acc'], 
                      country, countries[country]['iso2'], countries[country]['iso3'], countries[country]['popData2018']]
                writer.writerow(row)
            except:
                print('ERROR: ', row)
                print(countries[country])

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
                    if row['Region'] == 'Total':
                        continue
                    data_cl[row['Region']] = dict()
                if not(fecha in data_cl[row['Region']].keys()):
                    data_cl[row['Region']][fecha] = dict(data_empty)
                for tag in tags:
                    if tag in row.keys():
                        if len(row[tag])>0:
                            n=int(row[tag])
                        else:
                            n=0
                        data_cl[row['Region']][fecha][tags[tag]] = n
            except:
                print('ERROR:', row.keys())
                    
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
                    
def fillPopCl(filename, data_cl, name_column):
    data = pd.read_csv(filename)
    for row in data.itertuples():
        pop = data[data.Region==row.Region].iloc[0][name_column]
        for f in data_cl[row.Region]:
            data_cl[row.Region][f]['popData2018'] = pop
            
def createDataFrame(data, header):
    columnas = ['Region', 'Fecha', 'dateRep', 'day', 'month', 'year'] + header
    df = pd.DataFrame(columns=columnas)
    print('Creando dataFrame...')
    data_dict = {}
    for c in columnas:
        data_dict[c] = []
    for region, dates in data.items():
        for fecha, datos in dates.items():
            [year, month, day] = fecha.split('-')
            data_dict['Region'].append(region)
            data_dict['Fecha'].append(fecha)
            data_dict['dateRep'].append('{0:s}/{1:s}/{2:s}'.format(day, month, year))
            data_dict['day'].append(int(day))
            data_dict['month'].append(int(month))
            data_dict['year'].append(int(year))
            for h in header:
                data_dict[h].append(datos[h])
    df = pd.DataFrame(data_dict)
    print('... dataFrame OK.')
    return df
        
def corregirPeak(data, column, date_peak, date_ini):
    regiones = data.Region.unique()
    data['other'] = 0
    for region in regiones:
        filtro = data[data.Region == region]
        npeak = filtro[filtro.Fecha == date_peak].cases
        nprev = filtro[filtro.index == npeak.index[0]-1].cases
        filtro = filtro[filtro.Fecha < date_peak]
        filtro = filtro[filtro.Fecha >= date_ini]
        print(filtro.cases.sum(), ':', npeak.index[0], npeak.values[0], nprev)
        filtro.other = filtro.cases_acc.diff()
        data.update(filtro)
        break

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
fillPopCl('../tmp/PCR.csv', data_cl, 'Poblacion')
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
df_cl = createDataFrame(data_cl, header[5:])
corregirPeak(df_cl, 'cases', '2020-06-17', '2020-01-01')
df_cl.to_csv('../covid19_cl_pd.csv', index=False)

with open('../covid19_cl.csv', 'w', newline='', encoding='utf-8') as f_writer:
    writer = csv.writer(f_writer)
    writer.writerow(header)
    for region in data_cl.keys():
        for d in data_cl[region].keys():
            sf = tuple(map(lambda x: int(x), d.split('-')))
            fecha = date(sf[0], sf[1], sf[2])
            try:
                row= [region, fecha.strftime('%d/%m/%Y'), fecha.day, fecha.month, fecha.year, 
                      data_cl[region][d]['cases'], data_cl[region][d]['deaths'], data_cl[region][d]['recovered'], 
                      data_cl[region][d]['cases_acc'], data_cl[region][d]['deaths_acc'], data_cl[region][d]['recovered_acc'], 
                      data_cl[region][d]['popData2018'],
                      data_cl[region][d]['pcr'], data_cl[region][d]['uci']]
                writer.writerow(row)
            except:
                print('ERROR CL:', row)
                print(region, d, data_cl[region][d])
                break

