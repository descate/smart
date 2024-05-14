# -*- coding: utf-8 -*-
import arcpy
import requests
import json
import pandas as pd
from shapely.geometry import MultiLineString
import os
import time

#Parametros para Patrullaje
parametro_anp = arcpy.GetParameter(0)
url_patrullaje = arcpy.GetParameter(1)
url_actividades = arcpy.GetParameter(2)
url_fauna = arcpy.GetParameter(3)
url_flora = arcpy.GetParameter(4)
anp_codi = parametro_anp.split(" - ")[0]

#################################### INICIO DE FUNCIONES ################################
def convertir_a_entero(cadena):
    try:
        # Intentar convertir la cadena a un entero
        entero = int(cadena)
        return entero
    except ValueError:
        # En caso de error de conversion, devolver 0
        return 0

""" def smart2gdb(url_patrullaje):
    #url_geojson = 'https://sernanpperuconnect.smartconservationtools.org/server/noa/sharedlink/?uuid=bf944241-886a-4a87-b971-481a3f69c91c'
    df = None

    try:
        # Descargar el archivo GeoJSON desde la URL
        response = requests.get(url_patrullaje)
        # Verificar si la solicitud fue exitosa (código 200)
        if response.status_code == 200:
            geojson_data = json.loads(response.content.decode('utf-8'))
            # Extraer el valor de EPSG y eliminar "EPSG:" del string
            epsg_value = int(geojson_data["crs"]["properties"]["name"].split(":")[1])
            # Crear listas para almacenar los atributos y geometrías
            datos = []
            geometrias = []
            # Iterar a través de las características (features) en el GeoJSON
            for feature in geojson_data['features']:
                # Obtener los atributos y la geometría de cada característica
                atributos = feature['properties']
                geometria = feature['geometry']
                # Crear un diccionario con los atributos y geometría
                fila = atributos.copy()
                fila['geometria'] = geometria  # Agregar la geometría como una nueva columna
                # Agregar la fila a la lista de datos
                datos.append(fila)
            # Convertir la lista de datos en un DataFrame de Pandas
            df = pd.DataFrame(datos)
        else:
            print("La solicitud no fue exitosa. Código de estado:", response.status_code)
            
    except Exception as e:
        print("Ocurrió un error:", str(e))

    # Eliminar registros con geometría vacía
    df = df.dropna(subset=['geometria'])

    # Crear una lista para almacenar las nuevas coordenadas
    nuevas_coordenadas = []

    # Iterar a través de las filas del DataFrame original
    for index, row in df.iterrows():
        # Obtener las coordenadas de la geometría
        coordenadas = MultiLineString(row['geometria']['coordinates'])
        
        # Añadir las coordenadas a la lista
        nuevas_coordenadas.append(coordenadas)

    # Añadir la nueva columna 'coordenadas' al DataFrame original
    df['coordenadas'] = nuevas_coordenadas
    df['anp_codi'] = anp_codi
    # Verificar si 'Pilot' existe en las columnas del DataFrame
    if 'Pilot' not in df.columns:
        # Si no existe, crea la columna 'Pilot' con valores vacíos
        df['Pilot'] = ''
    mapeo_mandate = {
        "Especial": 1,
        "Especial con fines de Intervencion": 2,
        "Rutinario": 3,
        "Sobrevuelo": 4,
        "Vigilancia Comunal": 5,
        "Vigilancia en el PVC": 6
    }
    df['mandato'] = df['Mandate'].map(mapeo_mandate)

    mapeo_transporte = {
        "Air": 1,
        "Ground": 2,
        "Water": 3
    }
    df['transporte'] = df['Patrol_Transport_Type'].map(mapeo_transporte)
    df['objetivo'] = df ['Objective'].str[:1000]

    mapeo_tipotransporte = {
        "Acémilas": 1,
        "A pie": 2,
        "Bicicleta": 3,
        "Camioneta": 4,
        "Cuatrimoto": 5,
        "Drones": 6,
        "Motocicleta": 3
        
    }
    df['tipotransporte'] = df['Patrol_Transport_Type'].map(mapeo_tipotransporte)
    sistema_coordenada = arcpy.SpatialReference(epsg_value)
    df['SHAPE'] = df['coordenadas'].apply(lambda x: arcpy.FromWKT(x.wkt, sistema_coordenada))
    df['tra_cod'] = df['Patrol_Leg_ID'].str[0]



    registros_con_geometria = []

    for index, row in df.iterrows():
        
        registro = (
            row['anp_codi'], row['Patrol_ID'], row['Patrol_Start_Date'], row['Patrol_End_Date'], row['transporte'],
            row['mandato'], row['Station'], row['Team'], row['objetivo'], row['tra_cod'], row['Patrol_Leg_Start_Date'],
            row['Patrol_Leg_End_Date'], row['tipotransporte'], row['Leader'], row['Pilot'],
            row['SHAPE']# Agregar la geometria aqui
        )

        # Agregar el registro a la lista
        registros_con_geometria.append(registro)

    print(df)


    # Establecer la ruta de la geodatabase y el nombre del Feature Class
    gdb_path = r'Database Connections\SERNANP.sde'
    dataset = 'gdb.sde.VigilanciaControl'
    feature_class_name = 'gdb.sde.Patrullaje'  # Reemplaza con el nombre deseado

    # Combinar la ruta de la geodatabase con el nombre del Feature Class
    fc = os.path.join(gdb_path, feature_class_name)

    # Iniciar una sesion de edicion
    edit = arcpy.da.Editor(r'Database Connections\SERNANP.sde')
    edit.startEditing(False, True)  # Puedes ajustar los parametros segun tus necesidades

    # Iniciar una operacion de edicion
    edit.startOperation()

    # Abrir un InsertCursor para insertar los registros en el Feature Class
    with arcpy.da.InsertCursor(fc, ('anp_codi','pat_codi','pat_fecini','fecha','pat_tip','pat_mdt','pat_est','pat_sec', 'pat_obj', 'tra_cod','tra_fecini',
                                        'tra_fecfin','tra_tip','tra_lid', 'tra_pil','SHAPE@')) as cursor:
        # Insertar las filas en el Feature Class
        for registro in registros_con_geometria:
            try:
                cursor.insertRow(registro)
            except Exception as e:
                print("Error al insertar el siguiente registro:")
                print(registro)
                print("Error:", str(e))

    # Confirma la operacion de edicion
    edit.stopOperation()

    # Finaliza la sesion de edicion (guardando los cambios)
    edit.stopEditing(True)

    print("Registros insertados exitosamente en el Feature Class.")  """

def smart2gdb_actividades (url_actividades):
    #url_geojson = 'https://sernanpperuconnect.smartconservationtools.org/server/noa/sharedlink/?uuid=a25d63fd-c8ac-493b-a47d-47dbc7d61c08'

    try:
        # Descargar el archivo GeoJSON desde la URL
        response = requests.get(url_actividades)
        
        # Verificar si la solicitud fue exitosa (codigo 200)
        if response.status_code == 200:
            geojson_data = json.loads(response.content.decode('utf-8'))
            # Extraer el valor de EPSG y eliminar "EPSG:" del string
            epsg_value = int(geojson_data["crs"]["properties"]["name"].split(":")[1])
            
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
            # Mostrar el DataFrame
            print(df)
        else:
            print("La solicitud no fue exitosa. Codigo de estado:", response.status_code)

    except Exception as e:
        print("Ocurrio un error:", str(e))

    df['anp_codi'] = anp_codi
    df['cod_efec'] = df['Lista_de_efectos'].str.slice(0, 2)
    df['cod_act'] = df['Observation_Category_1'].str.slice(0, 2)
    df['Date'] = pd.to_datetime(df['Waypoint_Date'])
    df["cod_act"] = df["cod_act"].apply(convertir_a_entero)
    #df.iloc[:, 0].fillna("Solo registro", inplace=True)

    sistema_coordenada = arcpy.SpatialReference(epsg_value)

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
    intentos_maximos = 2  
    intento_actual = 0  
    while intento_actual < intentos_maximos:
        try:
            edit = arcpy.da.Editor(arcpy.env.workspace)
            edit.startEditing(with_undo=False, multiuser_mode=True)
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
            arcpy.AddMessage("Datos registrados correctamente")
            break
        except Exception as e:
            error_message = str(e)
            arcpy.AddMessage("Error al intentar registrar los datos: {}".format(error_message))
            intento_actual += 1  # Incrementa el contador de intentos
            
            if "Function or procedure does not exist" in error_message:
                arcpy.AddMessage("Reintentando la operación...")
                time.sleep(2)  # Espera 2 segundos antes de reintentar
            else:
                arcpy.AddMessage("Error no relacionado con la existencia de la función o procedimiento. No se reintentará.")
                break  # Si el error no es el esperado, salir del bucle
        finally:
            # Este bloque se ejecuta tanto si se produce una excepción como si no se produce
            if intento_actual >= intentos_maximos:
                arcpy.AddMessage("Se alcanzó el número máximo de intentos. No se pudo registrar los datos.")
################################### FIN DE FUNCIONES ####################################

# EJECUCION DE FUNCIONES
smart2gdb_actividades(url_actividades)

#smart2gdb(url_patrullaje)