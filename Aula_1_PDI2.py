# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 14:15:07 2017

@author: Philipe Leal
"""

import sys
import os
import numpy as np
try:
    from osgeo import gdal, ogr, osr
except:
    sys.exit("Erro: a biblioteca GDAL não foi encontrada!")
    
try:
    from utils import Geo2Grid
except:
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



gdal.UseExceptions()
ogr.UseExceptions()
osr.UseExceptions()

vector_file = "C:/Doutorado/3_Trimestre/PDI_2/focos/focos-2016.shp"
vector_file_base_name = os.path.basename(vector_file)  # retorna "focos_2016.shp"
layer_name = os.path.splitext(vector_file_base_name)[0]  # retorna ('focos_2016','.shp') #ou seja, retorna um tupla
                                                        # (imutável, ou seja não se pode alterar, apenas visualizar)

spatial_extent = {'xmin': -89.975, 'ymin': -59.975, 'xmax': -29.975, 'ymax': 10.025}
spatial_resolution = {'x': 0.05, 'y': 0.05}
grid_dimensions = {'cols': 1200, 'rows': 1400}

file_format = "GTiff"



shp_focos = ogr.Open(vector_file)
if shp_focos is None:
    sys.exit("Erro: não foi possível abrir o arquivos '{0}'".format(vector_file))

layer_focos2 = shp_focos.GetLayer(layer_name)
if layer_focos2 is None:
    sys.exit("Erro: não foi possível acessar a camada '{0}' no arquivo '{1}'!".format(layer_name, vector_file))

sensores = {'TERRA_M-M', 'TERRA_M-T', 'AQUA_M-T', 'AQUA_M-M'}
meses = ('2016/01','2016/02','2016/03','2016/04','2016/05','2016/06','2016/07','2016/08','2016/09','2016/10','2016/11','2016/12')

for sensor in sensores:
    for m in meses:
        layer_focos = layer_focos2 #apenas para manter uma referência

        if m != '2016/12':
            query = "satelite = '%s' and timestamp > '%s' and timestamp < '%s'" % (sensor, m, m + 1)

        else:
            query = "satelite = '%s' and timestamp > '%s' and timestamp < '2017/01'" % (sensor, m)

        layer_focos.SetAttributeFilter(query)
        nfocos = layer_focos.GetFeatureCount()
        """print(nfocos) #query no argis resulta em 2960 para primeiro satélite e mes=1
                        # "timestamp" > '2016/01' AND "timestamp" < '2016/02' AND "satelite" ='TERRA_M-M'
                        #Resultados (TERRA_M-M): jar 2960, fev 786, mar 2023, abr 845, mai 829, jun 1510,
                        # jul 3976, ago 10797, set 12683, out 7320, nov 4836, dez 1948
        """
        # Criando uma matriz numérica
        matriz = np.zeros((grid_dimensions['rows'], grid_dimensions['cols']), np.int16)

        # calcular o número de focos associado a cada célula
        # Itera por cada um dos focos calculando sua localização na grade:
        for foco in layer_focos:
            location = foco.GetGeometryRef()
            col, row = Geo2Grid(location, grid_dimensions, spatial_resolution, spatial_extent)
            matriz[row, col] += 1

        # criando raster de saída usando GDAL
        
        output_file_name = "C:/Doutorado/3_Trimestre/PDI_2/focos/output/{0}_{1}.tif".format(sensor, m) 
        
        try:
            try:
                driver = gdal.GetDriverByName(file_format)
            except:
                print("Erro: não foi possível identificar o driver '{0}.".format(file_format))
            try:
                raster = driver.Create(output_file_name,grid_dimensions['cols'],grid_dimensions['rows'],1,gdal.GDT_UInt16) 
            except:
                print("nao foi possivel criar o arquivo '{0}'".format(output_file_name))
            try:
                raster.SetGeoTransform((spatial_extent['xmin'],spatial_resolution['x'],0,spatial_extent['ymax'],0,-spatial_resolution['y'])) 
            except:
                print("Nao foi possivel atribuir Geotransformação ao raster de saída {0}". format(output_file_name))
            
            try:
                srs_focos = layer_focos.GetSpatialRef()
            except:
                print("Nao foi possivel atribuir referência espacial ao raster de saída {0}". format(output_file_name))
            
            try:
                raster.SetProjection(srs_focos.ExportToWkt())
            except:
                print("Não foi possível atribuir Projeção ao raster de saída {0}". format(output_file_name))
            
            try:
                band = raster.GetRasterBand(1)
                band.WriteArray(matriz,0,0) 
            except:
                print("Não foi possível atribuir valores aos píxeis do raster de saída {0}". format(output_file_name))
            try:
                band.FlushCache() 
                raster = None 
                print(output_file_name)
            except:
                print("Não foi possível liberar memória entre os rasters de saída")
            
            print("Criação e atribuição de valores ao arquivo {0} realizados com sucesso!".format(output_file_name))
        
        except:
            print("Problemas na criacao do arquivo {0}. Ver detalhes nas exceções específicas:".format(output_file_name))

del raster, band
