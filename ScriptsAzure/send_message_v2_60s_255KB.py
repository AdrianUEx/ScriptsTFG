# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# Modificaciones realizadas por Adrián Barquilla Rodríguez, 2025

import os
import time
import uuid
from azure.iot.device import IoTHubDeviceClient, Message
import base64 # Import hecho por mí para poder convertir las imágenes a base64 para poder serializarlo en JSON
import json # Import para las funcionalidades de JSON

ruta_carpeta_imgs = "/home/raspberry-adrian/imagenesTFG"
ruta_img = "/home/raspberry-adrian/imagenesTFG/foto_alumnos.jpg"
MAX_PAYLOAD_B64 = 255 * 1024 #255K para no superar el límite de IoT Hub
duracion_prueba = 60 #duración en segundos que ha de durar la ráfaga de mensajes

# The connection string for a device should never be stored in code. For the sake of simplicity we're using an environment variable here.
# cadena_conexion_principal = "HostName=miprimer-iothub.azure-devices.net;DeviceId=MiDispositivoCliente;SharedAccessKey=i0Ixw6JJyEyvN+glRkew6MGerhsJmynYTjPEuSmTR08="
# conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")
conn_str = "HostName=miprimer-iothub.azure-devices.net;DeviceId=MiDispositivoCliente;SharedAccessKey=i0Ixw6JJyEyvN+glRkew6MGerhsJmynYTjPEuSmTR08=;GatewayHostName=adrian-VirtualBox"

# The client object is used to interact with your Azure IoT hub.
device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

# Connect the client.
device_client.connect()

# Método para convertir a base64
def convertir_imagen_b64():
    with open(ruta_img, "rb") as f:
        print('Convirtiendo imagen a base64')
        imagen_b64 = base64.b64encode(f.read()).decode('utf-8') # Codificar y convertir a base64 el archivo leído, y luego se usa .decode() para pasarlo de bytes a str. No puede ser mayor a 256KB porque es lo máximo que aguanta IoT Hub; MQTT tiene un máximo teórico de 256MB. Esto es relevante porque el resto de servicios IoT reciben datos a través del enrutamiento a través de IoT Hub.
        print('Convertida imagen a base64')
    return imagen_b64

# Método para devolver una lista con los fragmentos de 255KB en cada posición
def fragmentar_imagen_b64(imagen_b64):
    total_length = len(imagen_b64)
    
    fragmentos = [] # Una lista
    for i in range(0, total_length, MAX_PAYLOAD_B64): # range() es un iterable que empieza en 0 por defecto, llega hasta 'total_length' yendo en pasos de MAX_PAYLOAD_B64
        fragmento = imagen_b64[i:i + MAX_PAYLOAD_B64] # accede a un subconjunto de elementos utilizando los índices
        fragmentos.append(fragmento)
    
    return fragmentos # Esta lista ya tiene en cada posición los 255K caracteres en base64
    
fragmentos = fragmentar_imagen_b64(convertir_imagen_b64())
print(f'Cantidad de fragmentos: ', len(fragmentos))

print('Comenzando envío de mensajes hacia IoT Edge')
loop_count = 0
inicio = time.perf_counter()
while time.perf_counter() - inicio  < duracion_prueba: 
        
    message = {} # Declara un diccionario, que es una estructura que almacena pares clave-valor

    for index, contenido in enumerate(fragmentos): # Se emplean dos 'indices' porque el enumerate crea una lista de elementos clave-valor, donde la clave es un número (index) y el valor es lo que sea (contenido)
        message['image'] = contenido
        messageJson = json.dumps(message) # Convierte el diccionario 'message' en un JSON. Hace falta porque los datos esperados han de ser texto o cosas codificables en formato JSON.

        device_client.send_message(messageJson)

    loop_count += 1
    #time.sleep(1)
    
fin = time.perf_counter()
print(f'Tiempo transcurrido: {fin-inicio:.4f} segundos. Imágenes transmitidas: {loop_count}')

# finally, shut down the client
device_client.shutdown()
