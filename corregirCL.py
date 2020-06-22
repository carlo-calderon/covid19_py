# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 22:40:57 2020

@author: Carlo
"""
from os import listdir

def corregirCL():
    ## Eliminando acentos de archivo de totales acumulados por región
    print("Corrigiendo datos....!")
    f = open('../COVID19-Chile/output/producto3/CasosTotalesCumulativo.csv', encoding='utf-8')
    lines = f.readlines()
    f.close()
    f_out = open('../tmp/CasosTotalesCumulativo.csv', 'w', encoding='utf-8')
    for line in lines:
        l=line.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        l = l.replace('O’Higgins', "O'Higgins")
        f_out.write(l)
    f_out.close()
    
    ## Corrigiendo archivos diarios
    path_p4 = '../COVID19-Chile/output/producto4/'
    for f in listdir(path_p4):
        f_in = open(path_p4 + f, encoding='utf-8')
        lines = f_in.readlines()
        f_in.close()
        f_out = open('../tmp/cl_producto4/' + f, 'w', encoding='utf-8')
        for line in lines:
            l = line.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
            l = l.replace('   ', ' ')
            l = l.replace('  ', ' ')
            l = l.replace(', ', ',')
            l = l.replace(' ,', ',')
            l = l.replace('Casos fallecidos', 'Fallecidos')
            l = l.replace('Fallecidos totales', 'Fallecidos')
            l = l.replace('Metropolita,', 'Metropolitana,')
            l = l.replace('Arica y Paricota', 'Arica y Parinacota')
            l = l.replace('O’Higgins', "O'Higgins")
            l = l.replace('Nuble', "Ñuble")
            l = l.replace('\ufeffRegion', 'Region')
            l = l.replace('Región', 'Region')
            l = l.replace('Casos totales acumulados', 'Casos totales')
            f_out.write(l)
        f_out.close()
        
    ## Corrigiendo PCR
    f = open('../COVID19-Chile/output/producto7/PCR.csv', encoding='utf-8')
    lines = f.readlines()
    f.close()
    f_out = open('../tmp/PCR.csv', 'w', encoding='utf-8')
    for line in lines:
        l=line.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        l = l.replace('Del Libertador General Bernardo O’Higgins', "O'Higgins")
        l = l.replace('Nuble', 'Ñuble')
        l = l.replace('Magallanes y la Antartica', 'Magallanes')
        l = l.replace('O’Higgins', "O'Higgins")
        l = l.replace(',-', ',0')
        l = l.replace(',,', ',0,')
        l = l.replace(',\n', ',0\n')
        f_out.write(l)
    f_out.close()

    ## Corrigiendo UCI
    f = open('../COVID19-Chile/output/producto8/UCI.csv', encoding='utf-8')
    lines = f.readlines()
    f.close()
    f_out = open('../tmp/UCI.csv', 'w', encoding='utf-8')
    for line in lines:
        l=line.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        l = l.replace('Del Libertador General Bernardo O’Higgins', "O'Higgins")
        l = l.replace('Nuble', 'Ñuble')
        l = l.replace('Magallanes y la Antartica', 'Magallanes')
        l = l.replace('O’Higgins', "O'Higgins")
        l = l.replace(',-', ',0')
        l = l.replace(',,', ',0,')
        l = l.replace(',\n', ',0\n')
        f_out.write(l)
    f_out.close()

if __name__=="__main__":
    corregirCL()