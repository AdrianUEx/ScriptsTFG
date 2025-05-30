# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0.
# Modificaciones realizadas por Adrián Barquilla Rodríguez, 2025

import time
import json
import base64
import uuid
import os

from awscrt import io, http # Esto de aquí son las dependencias que se encuentran dentro del venv, no del SDK clonado como ocurre con CommandLineUtils.
from awscrt.mqtt import QoS
from awsiot.greengrass_discovery import DiscoveryClient
from awsiot import mqtt_connection_builder
from utils.command_line_utils import CommandLineUtils # Esta línea está importando la clase 'command_line_utils' desde la carpeta 'Utils' que se encuentra en la carpeta 'samples' dentro del SDK.

ruta_carpeta_imgs = "/home/raspberry-adrian/imagenesTFG"
ruta_img = "/home/raspberry-adrian/imagenesTFG/foto_alumnos.jpg"
MAX_PAYLOAD_B64 = 127 * 1024 # 127K para no superar el límite de IoT Core
duracion_prueba = 60 # Duración en segundos 

allowed_actions = ['both', 'publish', 'subscribe']

# cmdData is the arguments/input from the command line placed into a single struct for
# use in this sample. This handles all of the command line parsing, validating, etc.
# See the Utils/CommandLineUtils for more information.
cmdData = CommandLineUtils.parse_sample_input_basic_discovery()

tls_options = io.TlsContextOptions.create_client_with_mtls_from_path(cmdData.input_cert, cmdData.input_key)
if (cmdData.input_ca is not None): # Si el certificado introducido por parámetros existe
    tls_options.override_default_trust_store_from_path(None, cmdData.input_ca)
tls_context = io.ClientTlsContext(tls_options)

socket_options = io.SocketOptions()

proxy_options = None
if cmdData.input_proxy_host is not None and cmdData.input_proxy_port != 0: # Si se han encontrado endpoints configurados (se está comprobando los host y los puertos con los que están asociados)
    proxy_options = http.HttpProxyOptions(cmdData.input_proxy_host, cmdData.input_proxy_port)

print('Performing greengrass discovery...')
discovery_client = DiscoveryClient(
    io.ClientBootstrap.get_or_create_static_default(),
    socket_options,
    tls_context,
    cmdData.input_signing_region, None, proxy_options)
resp_future = discovery_client.discover(cmdData.input_thing_name)
discover_response = resp_future.result()

# En este punto el descubrimiento se ha hecho ya, y solo queda comprobar si el valor es de un dispositivo descubierto o no
if (cmdData.input_is_ci):
    print("Received a greengrass discovery result! Not showing result in CI for possible data sensitivity.")
else:
    print(discover_response)

if (cmdData.input_print_discovery_resp_only):
    exit(0)

def on_connection_interupted(connection, error, **kwargs):
    print('connection interrupted with error {}'.format(error))


def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print('connection resumed with return code {}, session present {}'.format(return_code, session_present))


# Try IoT endpoints until we find one that works
def try_iot_endpoints():
    for gg_group in discover_response.gg_groups:
        for gg_core in gg_group.cores:
            for connectivity_info in gg_core.connectivity:
                try:
                    print(
                        f"Trying core {gg_core.thing_arn} at host {connectivity_info.host_address} port {connectivity_info.port}")
                    # Crea el objeto Connection empleando parte de los parámetros introducidos por parámetros por el usuario
                    mqtt_connection = mqtt_connection_builder.mtls_from_path(
                        endpoint=connectivity_info.host_address,
                        port=connectivity_info.port,
                        cert_filepath=cmdData.input_cert,
                        pri_key_filepath=cmdData.input_key,
                        ca_bytes=gg_group.certificate_authorities[0].encode('utf-8'),
                        on_connection_interrupted=on_connection_interupted,
                        on_connection_resumed=on_connection_resumed,
                        client_id=cmdData.input_thing_name,
                        clean_session=False,
                        keep_alive_secs=30)

                    connect_future = mqtt_connection.connect() # Al efectuar el .connect() este devuelve un objeto de tipo Future que es el que contiene como tal el objeto y los estados por los que pasa.
                    connect_future.result()
                    print('Connected!')
                    return mqtt_connection

                except Exception as e:
                    print('Connection failed with exception {}'.format(e))
                    continue

    exit('All connection attempts failed')


mqtt_connection = try_iot_endpoints()
# En este punto, ya están cargados los endpoints encontrados en forma de conexión MQTT en la variable 'mqtt_connection'.

# Método para convertir a base64
def convertir_imagen_b64():
    with open(ruta_img, "rb") as f:
        print('Convirtiendo imagen a base64...')
        imagen_b64 = base64.b64encode(f.read()).decode('utf-8')
        print('Convertida imagen a base64')
    return imagen_b64

# Método para devolver una lista con los fragmentos de 127KB en cada posición
def fragmentar_imagen_b64(imagen_b64):
    total_length = len(imagen_b64)
    
    fragmentos = []
    for i in range(0, total_length, MAX_PAYLOAD_B64):
        fragmento = imagen_b64[i:i + MAX_PAYLOAD_B64]
        fragmentos.append(fragmento)
    
    return fragmentos
    
fragmentos = fragmentar_imagen_b64(convertir_imagen_b64())
print(f'Cantidad de fragmentos: ', len(fragmentos))

loop_count = 0
inicio = time.perf_counter()
while time.perf_counter() - inicio  < duracion_prueba: 
    if cmdData.input_mode == 'both' or cmdData.input_mode == 'publish':
        
        message = {}

        for index, contenido in enumerate(fragmentos): # Se emplean dos 'indices' porque el enumerate crea una lista de elementos clave-valor, donde la clave es un número (index) y el valor es lo que sea (contenido)
            message['image'] = contenido
            messageJson = json.dumps(message) # Convierte el diccionario 'message' en un JSON. 
           
            pub_future, _ = mqtt_connection.publish(cmdData.input_topic, messageJson, QoS.AT_LEAST_ONCE) # mqtt_connection.publish(topic, payload, qos=0)
            
        loop_count += 1
    
fin = time.perf_counter()
print(f'Tiempo transcurrido: {fin-inicio:.4f} segundos. Imágenes transmitidas: {loop_count}')
