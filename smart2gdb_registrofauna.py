# -*- coding: utf-8 -*-
import arcpy
import pandas as pd
import json
import requests
import os
import numpy as np
import unicodedata
#################################### Inicio de Funciones ################################
# Función para quitar tildes de un texto
def quitar_tildes(texto):
    return ''.join((c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn'))
################################### Fin de Funciones ####################################

# URL del archivo GeoJSON
url_geojson = 'https://sernanpperuconnect.smartconservationtools.org/server/noa/sharedlink/?uuid=0211882e-b4fb-4425-814e-c08bfdea2584'

try:
    # Descargar el archivo GeoJSON desde la URL
    response = requests.get(url_geojson)
    
    # Verificar si la solicitud fue exitosa (codigo 200)
    if response.status_code == 200:
        geojson_data = json.loads(response.content.decode('utf-8'))

        # Crear una lista para almacenar los atributos y geometrias
        datos = []

        # Iterar a traves de las caracteristicas (features) en el GeoJSON
        for feature in geojson_data['features']:
            # Obtener los atributos y la geometria de cada caracteristica
            atributos = feature['properties']
            # Crear un diccionario con los atributos y geometria
            fila = atributos.copy()

            # Agregar la fila a la lista de datos
            datos.append(fila)

        # Convertir la lista de datos en un DataFrame de Pandas
        df = pd.DataFrame(datos)
        # Mostrar el DataFrame
    else:
        print("La solicitud no fue exitosa. Codigo de estado:", response.status_code)

except Exception as e:
    print("Ocurrio un error:", str(e))
df.columns = [quitar_tildes(column) for column in df.columns]
print(df)
df['anp_codi'] = "RN08"
df['Tipo_de_registro'] = df['Tipo_de_registro__fauna'].apply(
    lambda x: 'OD' if x in ['Visual', 'Auditivo'] else ('OI' if x and not pd.isnull(x) else None)
)
df['evidencia'] = df['Tipo_de_registro__fauna']
df['fuente'] = 1
df['Total_de_individuos__fauna'] = df['Total_de_individuos__fauna'].apply(lambda x: int(x) if not pd.isnull(x) else np.nan)
sistema_coordenada = arcpy.SpatialReference(32718)

# Crear una lista para almacenar los registros con geometria
registros_con_geometria = []

for index, row in df.iterrows():
    lat = row['Y']
    lon = row['X']
    punto = arcpy.Point(lon, lat)
    geometria = arcpy.PointGeometry(punto, sistema_coordenada)
    # Agregar la geometria como un par de coordenadas X, Y en el registro
    registro = (
        row['anp_codi'], row['Nombre_cientifico__fauna'], row['Nombre_comun__fauna'], row['Tipo_de_registro'],
        row['evidencia'], row['fuente'], row['Waypoint_Date'], row['Total_de_individuos__fauna'], row['X'], row['Y'],
        geometria  # Agregar la geometria aqui
    )

    # Agregar el registro a la lista
    registros_con_geometria.append(registro)

# Establecer la ruta de la geodatabase y el nombre del Feature Class
gdb_path = r'Database Connections\SERNANP.sde'
dataset = 'gdb.sde.RegistrosBiodiversidad'
feature_class_name = 'gdb.sde.RegistroPresenciaFauna'  # Reemplaza con el nombre deseado

# Combinar la ruta de la geodatabase con el nombre del Feature Class
fc = os.path.join(gdb_path, feature_class_name)

# Iniciar una sesion de edicion
edit = arcpy.da.Editor(r'Database Connections\SERNANP.sde')
edit.startEditing(False, True)  # Puedes ajustar los parametros segun tus necesidades

# Iniciar una operacion de edicion
edit.startOperation()

# Abrir un InsertCursor para insertar los registros en el Feature Class
with arcpy.da.InsertCursor(fc, ('anp_codi','rf_nesp','rf_ncomun','rf_tobs','rf_evid','rf_fdato','rf_fech','rf_nindiv','rf_este', 'rf_norte','SHAPE@')) as cursor:
    # Insertar las filas en el Feature Class
    for registro in registros_con_geometria:
        cursor.insertRow(registro)

# Confirma la operacion de edicion
edit.stopOperation()

# Finaliza la sesion de edicion (guardando los cambios)
edit.stopEditing(True)

print("Registros insertados exitosamente en el Feature Class.") 