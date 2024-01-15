# -*- coding: utf-8 -*-
import arcpy
import pandas as pd
import json
import requests
import os
import unicodedata


#################################### Inicio de Funciones ################################
def convertir_a_entero(cadena):
    try:
        # Intentar convertir la cadena a un entero
        entero = int(cadena)
        return entero
    except ValueError:
        # En caso de error de conversion, devolver 0
        return 0

# Función para quitar tildes de un texto
def quitar_tildes(texto):
    return ''.join((c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn'))
################################### Fin de Funciones ####################################

# URL del archivo GeoJSON
url_geojson = 'https://sernanpperuconnect.smartconservationtools.org/server/noa/sharedlink/?uuid=709c3527-52fa-4546-ae5d-3de45825ae9f'

try:
    # Descargar el archivo GeoJSON desde la URL
    response = requests.get(url_geojson)
    
    # Verificar si la solicitud fue exitosa (codigo 200)
    if response.status_code == 200:
        geojson_data = json.loads(response.text)

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
        #print(df)
    else:
        print("La solicitud no fue exitosa. Codigo de estado:", response.status_code)

except Exception as e:
    print("Ocurrio un error:", str(e))

df.columns = [quitar_tildes(column) for column in df.columns]
if 'Nombre_cientifico__flora' not in df.columns:
    # Si no existe, crear la columna con valores vacíos
    df['Nombre_cientifico__flora'] = ''
df['anp_codi'] = "RN08"
df['fuente'] = 1
df['fenologia'] = df.iloc[:, 0].str.slice(0, 4)
mapeo_fenologia = {
    "Defo": 1,
    "Vege": 2,
    "Flor": 3,
    "Fruc": 4,
    "Prod": 5,
    "Rege": 6
}

df['estado_fenologico'] = df['fenologia'].map(mapeo_fenologia)
df['Waypoint_date'] = pd.to_datetime(df['Waypoint_Date'])
df['Date'] = df['Waypoint_date'].dt.date
sistema_coordenada = arcpy.SpatialReference(32718)
print(df)

# Crear una lista para almacenar los registros con geometria
registros_con_geometria = []

for index, row in df.iterrows():
    lat = row['Y']
    lon = row['X']
    punto = arcpy.Point(lon, lat)
    geometria = arcpy.PointGeometry(punto, sistema_coordenada)

    # Agregar la geometria como un par de coordenadas X, Y en el registro
    registro = (
        row['anp_codi'], row['Nombre_cientifico__flora'], row['Nombre_comun__flora'], row['estado_fenologico'],
        row['fuente'], row['Date'], row['Numero_de_individuos'], row['X'], row['Y'],
        geometria  # Agregar la geometria aqui
    )

    # Agregar el registro a la lista
    registros_con_geometria.append(registro)

# Establecer la ruta de la geodatabase y el nombre del Feature Class
gdb_path = r'Database Connections\SERNANP.sde'
dataset = 'gdb.sde.RegistrosBiodiversidad'
feature_class_name = 'gdb.sde.RegistroPresenciaFlora'  # Reemplaza con el nombre deseado

# Combinar la ruta de la geodatabase con el nombre del Feature Class
fc = os.path.join(gdb_path, feature_class_name)

# Iniciar una sesion de edicion
edit = arcpy.da.Editor(r'Database Connections\SERNANP.sde')
edit.startEditing(False, True)  # Puedes ajustar los parametros segun tus necesidades

# Iniciar una operacion de edicion
edit.startOperation()

# Abrir un InsertCursor para insertar los registros en el Feature Class
with arcpy.da.InsertCursor(fc, ('anp_codi','rfl_nesp','rfl_ncomun','rfl_efenol','rfl_fdato','rfl_fech','rfl_nindiv','rfl_este', 'rfl_norte','SHAPE@')) as cursor:
    # Insertar las filas en el Feature Class
    for registro in registros_con_geometria:
        cursor.insertRow(registro)

# Confirma la operacion de edicion
edit.stopOperation()

# Finaliza la sesion de edicion (guardando los cambios)
edit.stopEditing(True)

print("Registros insertados exitosamente en el Feature Class.") 