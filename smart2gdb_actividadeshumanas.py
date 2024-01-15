# -*- coding: utf-8 -*-
import arcpy
import pandas as pd
import json
import requests
import os
import time
    
#################################### Inicio de Funciones ################################
def convertir_a_entero(cadena):
    try:
        # Intentar convertir la cadena a un entero
        entero = int(cadena)
        return entero
    except ValueError:
        # En caso de error de conversion, devolver 0
        return 0
################################### Fin de Funciones ####################################

# URL del archivo GeoJSON
url_geojson = 'https://sernanpperuconnect.smartconservationtools.org/server/noa/sharedlink/?uuid=957ff6fc-1aa9-482c-8602-93649165e822'

try:
    # Descargar el archivo GeoJSON desde la URL
    response = requests.get(url_geojson)
    
    # Verificar si la solicitud fue exitosa (codigo 200)
    if response.status_code == 200:
        
        #geojson_text = response.content.decode('latin-1')
        
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
        #df = df.dropna(subset=['Observation_Category_1']) - Eliminar los campos vacios segun la columna indicada
        # Mostrar el DataFrame
        print(df)
    else:
        print("La solicitud no fue exitosa. Codigo de estado:", response.status_code)

except Exception as e:
    print("Ocurrio un error:", str(e))


df['anp_codi'] = "RN09"
df['cod_efec'] = df['Lista_de_efectos'].str.slice(0, 2)
df['cod_act'] = df['Observation_Category_1'].str.slice(0, 2)
df['Date'] = pd.to_datetime(df['Waypoint_Date'])
df["cod_act"] = df["cod_act"].apply(convertir_a_entero)
#df.iloc[:, 0].fillna("Solo registro", inplace=True)

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
        row['anp_codi'], row['cod_act'], row['Observation_Category_1'], row['X'],
        row['Y'], row['Date'], row.iloc[0], row['cod_efec'], row['Patrol_ID'],
        geometria  # Agregar la geometria aqui
    )

    # Agregar el registro a la lista
    registros_con_geometria.append(registro)


# Establecer la ruta de la geodatabase y el nombre del Feature Class
gdb_path = r'Database Connections\SERNANP.sde'
dataset = 'gdb.sde.VigilanciaControl'
feature_class_name = 'gdb.sde.RegistroActividadesHumanasPt'  # Reemplaza con el nombre deseado



# Combinar la ruta de la geodatabase con el nombre del Feature Class
fc = os.path.join(gdb_path, feature_class_name)

# Establecer la conexión a la geodatabase
arcpy.env.workspace = r'Database Connections\SERNANP.sde'

# Esperar 5 segundos antes de continuar
time.sleep(5)

# Iniciar una sesion de edicion
edit = arcpy.da.Editor(r'Database Connections\SERNANP.sde')
edit.startEditing(False, True)  # Puedes ajustar los parametros segun tus necesidades

# Iniciar una operacion de edicion
edit.startOperation()


# Abrir un InsertCursor para insertar los registros en el Feature Class
with arcpy.da.InsertCursor(fc, ('anp_codi', 'ra_ac_cod', 'ra_activ', 'ra_este', 'ra_norte', 'ra_fecreg',
                                'ra_accion', 'ra_ef_cod', 'rp_cod', 'SHAPE@')) as cursor:
    # Insertar las filas en el Feature Class
    for registro in registros_con_geometria:
        cursor.insertRow(registro)

# Confirma la operacion de edicion
edit.stopOperation()

# Finaliza la sesion de edicion (guardando los cambios)
edit.stopEditing(True)

print("Registros insertados exitosamente en el Feature Class.")

