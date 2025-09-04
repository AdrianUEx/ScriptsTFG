# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os 
import time
from azure.iot.device import IoTHubDeviceClient, Message
import base64 
import json 

ruta_carpeta_imgs = "/home/raspberry-adrian/imagenesTFG"
ruta_img = "/home/raspberry-adrian/imagenesTFG/foto_alumnos.jpg"
MAX_PAYLOAD_B64 = 63 * 1024 # Tamaño del paquete
duracion_prueba = 60 # Duración en segundos que ha de durar la ráfaga de mensajes

print("ATENCION: NO OLVIDAR CAMBIAR LA DIRECCIÓN IP EN EL FICHERO /etc/hosts ANTES DE LANZAR EL SCRIPT \n");

# The connection string for a device should never be stored in code. For the sake of simplicity we're using an environment variable here.
#cadena_conexion_principal = "HostName=miprimer-iothub.azure-devices.net;DeviceId=MiDispositivoCliente;SharedAccessKey=i0Ixw6JJyEyvN+glRkew6MGerhsJmynYTjPEuSmTR08="
#conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")
conn_str = "HostName=miprimer-iothub.azure-devices.net;DeviceId=MiDispositivoCliente;SharedAccessKey=i0Ixw6JJyEyvN+glRkew6MGerhsJmynYTjPEuSmTR08=;GatewayHostName=adrian-VirtualBox"

# The client object is used to interact with your Azure IoT hub.
device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

# Connect the client.
device_client.connect()

# Método para convertir a base64
def convertir_imagen_b64():
    with open(ruta_img, "rb") as f:
        print('Convirtiendo imagen a base64...')
        imagen_b64 = base64.b64encode(f.read()).decode('utf-8')
        print('Convertida imagen a base64')
    return imagen_b64

# Método para devolver una lista con los fragmentos en base64
def fragmentar_imagen_b64(imagen_b64):
    total_length = len(imagen_b64)
    
    fragmentos = [] # Una lista
    for i in range(0, total_length, MAX_PAYLOAD_B64):
        fragmento = imagen_b64[i:i + MAX_PAYLOAD_B64]
        fragmentos.append(fragmento)
    
    return fragmentos 
    
fragmentos = fragmentar_imagen_b64(convertir_imagen_b64())
print(f'Cantidad de fragmentos: ', len(fragmentos))

loop_count = 0
message = {'image': ""} 
inicio = time.perf_counter()
print('Enviando...')
while time.perf_counter() - inicio  < duracion_prueba: 
    for index, contenido in enumerate(fragmentos): 
        message['image'] = contenido
        messageJson = json.dumps(message) 

        device_client.send_message(messageJson)

    loop_count += 1
    #time.sleep(1)
    
fin = time.perf_counter()
print(f'Tiempo transcurrido: {fin-inicio:.4f} segundos. Imágenes transmitidas: {loop_count}')


device_client.shutdown()
