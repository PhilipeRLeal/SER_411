
# coding: utf-8

"""
Created on Tue Oct 10 13:40:57 2017

@author: Philipe Leal
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 08:47:17 2017

@author: Philipe Leal
"""
try:
    import sys
except:
    print("Problemas na abertura do SYS")

try:
    import os
except:
    print("Problemas na abertura do OS")
try:
    import numpy as np
except:
    print("Problemas na abertura do numpy")
    
try:
    from osgeo import gdal, ogr, osr
except:
    sys.exit("Erro: a biblioteca GDAL não foi encontrada!")
    
try:
    
    from utils import *
except:
    print("Problemas na abertura de utils")
    
try:
    
    gdal.UseExceptions()
    ogr.UseExceptions()
    osr.UseExceptions()
    
except:
    print("Nao foi possivel usar excecoes pelo osgeo")

try:
    GDALDataset.ExecuteSQL()
except:
    print("Nao foi possível executar SQL pelo GDAL")
    
 


# In[ ]:


#Criando funcao utils:
 

import sys

# Carrega a Biblioteca GDAL/OGR
try:
 from osgeo import ogr
except:
 sys.exit("ERRO: Biblioteca GDAL/OGR não encontrada!")


def Geo2Grid(location, dimensions, resolution, extent):
 """
 Converts a geographic coordinate position to a regular grid coordinate.
 Args:
     location (Geometry): A geometric point with coordinates X and Y.
     dimensions (dict): The number of columns and rows in the grid.
     resolution (dict): The spatial resolution along the X and Y coordinates.
     extent (dict): The spatial extent associated to the grid.
 Returns:
     (int, int): the grid column and row where the point lies in.
 """

 x = location.GetX()
 y = location.GetY()

 col = int( ( x - extent['xmin'] ) / resolution['x'])

 row = int ( dimensions['rows'] - (y - extent['ymin']) / resolution['y'] )

 return col, row




# In[2]:


#definindo detalhes do gtiff:    
spatial_extent = { 'xmin': -89.975, 'ymin': -59.975,
                'xmax': -29.975, 'ymax': 10.025 }

spatial_resolution = { 'x': 0.05, 'y': 0.05 }

grid_dimensions = { 'cols': 1200, 'rows': 1400 }

file_format = "GTiff"

driver = gdal.GetDriverByName(file_format)

output_file_name = r"C:\Doutorado\3_Trimestre\PDI_2\focos\grade-2016.tiff"



# In[3]:


# Abrindo arquivo vetorial com focos de queimada
vector_file = "C:/Doutorado/3_Trimestre/PDI_2/focos/focos-2016.shp"
try:
    shp_focos = ogr.Open("C:/Doutorado/3_Trimestre/PDI_2/focos/focos-2016.shp")
except:
    print("Nao foi possivel abrir shapefile de focos")

try:
    layer_focos = shp_focos.GetLayer()
    print("atributos abertos com sucesso")
except:
    print("o conjunto de vetores nao foi atribuido a uma variavel")
    

#==============================================================================
#     #Descobrir a estrutura do shapefile
#     Lista_atributos = []
#     tipo = []
#     Definicao_camada = layer_focos.GetLayerDefn()
#     for n in range(Definicao_camada.GetFieldCount()):
#         
#         fdefn = Definicao_camada.GetFieldDefn(n)
#         Lista_atributos.append(fdefn.name)
#         tipo.append(fdefn.GetTypeName())
#         
#     print ("{0} : {1}\n".format(Lista_atributos, tipo))
#==============================================================================     

# opção 2 para leitura das propriedades do shapefile:

import fiona
shapefile =fiona.open(vector_file)
#read the original schema
schema = shapefile.schema
print schema

# adicionando novos atributos/propriedades ao esquema do shapefile:

schema['mes','string']= 'mes'

   


# In[28]:

layer_focos_filtro_sensor = layer_focos["satelite" == "AQUA_M-T"]

layer_focos_filtro_sensor_time = layer_focos["2016/02/12" in "timestamp"]



# In[37]:

print layer_focos_filtro_sensor_time.GetFieldCount


# In[5]:

print type(layer_focos_filtro_sensor_time)


print "keys: {0}\n".format(layer_focos_filtro_sensor_time.keys)

print "items: {0}\n".format(layer_focos_filtro_sensor_time.items)

print "numero de feições: {0}\n".format(layer_focos_filtro_sensor_time.GetFieldCount())

print "numero de feições: {0}\n".format(layer_focos_filtro_sensor.GetFieldCount())


#==============================================================================
# # In[12]: O geopandas é ruim para arquivos grandes. Causa pane de memória.
# 
# import pandas as pd
# import geopandas as gpd
# 
# 
# # In[38]:
# 
# # manipulação do shape via geopandas e matrizes de focos
# 
# Shapefile = gpd.read_file(vector_file)
# Shapefile.set_index('timestamp',inplace=True)
# Shapefile = fshp.sort_index()
# Shapefile_Agrupado = fshp.groupby('satelite')
# 
#==============================================================================

# In[ ]:

#Operando sobre os focos de queimada e atribuindo ao raster:


meses = ('2016/01','2016/02','2016/03','2016/04','2016/05','2016/06','2016/07','2016/08','2016/09','2016/10','2016/11','2016/12')
sensor = {'TERRA_M-M', 'TERRA_M-T', 'AQUA_M-T', 'AQUA_M-M'}


for s in sensor:
    layer_focos_fil = layer_focos
    matriz = np.zeros((grid_dimensions['rows'],grid_dimensions['cols']),np.uint16)
    layer_focos_fil.SetAttributeFilter("satelite = '{0}'".format(s))
    
    for m in meses: 
         
         
        counter = 0

        for foco in layer_focos_fil:

            data = str(foco.GetFieldAsString(7)[0:7])
            print data
            
            while data == m:
             
                counter = counter + 1
                location = foco.GetGeometryRef() 
                col, row = Geo2Grid(location, grid_dimensions, spatial_resolution, spatial_extent) 
                matriz[row, col] += 1


            else: 

                continue


        output_file_name = "C:/Doutorado/3_Trimestre/PDI_2/focos/output/{0}_{1}.tif".format(s,m) 
        raster = driver.Create(output_file_name,grid_dimensions['cols'],grid_dimensions['rows'],1,gdal.GDT_UInt16) 
        raster.SetGeoTransform((spatial_extent['xmin'],spatial_resolution['x'],0,spatial_extent['ymax'],0,-spatial_resolution['y'])) 
        srs_focos = layer_focos.GetSpatialRef() 
        raster.SetProjection(srs_focos.ExportToWkt()) 
        band = raster.GetRasterBand(1) 
        band.WriteArray(matriz,0,0) 
        band.FlushCache() 
        raster = None 
        print(output_file_name) 
        


        print ("Numero de feicoes selecionadas para o sensor {0}: {1}".format(s, counter))
