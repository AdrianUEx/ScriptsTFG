# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0.
# Modificaciones realizadas por Adrián Barquilla Rodríguez, 2025

import time
import json
from awscrt import io, http
from awscrt.mqtt import QoS
from awsiot.greengrass_discovery import DiscoveryClient
from awsiot import mqtt_connection_builder

from utils.command_line_utils import CommandLineUtils

allowed_actions = ['both', 'publish', 'subscribe']

# cmdData is the arguments/input from the command line placed into a single struct for
# use in this sample. This handles all of the command line parsing, validating, etc.
# See the Utils/CommandLineUtils for more information.
cmdData = CommandLineUtils.parse_sample_input_basic_discovery()

# cmdData:
#       input_topic: topic introducido por parámetros
#       input_message: payload del mensaje MQTT introducido por parámetros
#       input_cert: certificado introducido por parámetros
#       input_ca: certificado raíz (rootCA) introducido por parámetros
#       input_key: clave privada introducida por parámetros
#       input_thing_name: nombre del IoT Thing cliente introducido por parámetros
#       input_mode: modo de las acciones permitidas. Solo puede tener los valores 'both', 'publish' y 'subscribe'. No se introduce por parámetros.
#       input_signing_region: region sobre la cual realizar el Cloud Discovery introducida por parámetros

#       input_max_pub_ops: 10 (siempre es 10 de manera predeterminada debido a la inicializacion de la variable 'cmdData'). No se introduce por parámetros.
#       input_print_discovery_resp_only: no tengo ni idea. No se introduce por parámetros.
#       input_proxy_port: el puerto. No se introduce por parámetros
#       input_is_ci: Ni idea. No se introduce por parámetros.

tls_options = io.TlsContextOptions.create_client_with_mtls_from_path(cmdData.input_cert, cmdData.input_key)
if (cmdData.input_ca is not None):
    tls_options.override_default_trust_store_from_path(None, cmdData.input_ca)
tls_context = io.ClientTlsContext(tls_options)

socket_options = io.SocketOptions()

proxy_options = None
if cmdData.input_proxy_host is not None and cmdData.input_proxy_port != 0:
    proxy_options = http.HttpProxyOptions(cmdData.input_proxy_host, cmdData.input_proxy_port)

print('Performing greengrass discovery...')
discovery_client = DiscoveryClient(
    io.ClientBootstrap.get_or_create_static_default(),
    socket_options,
    tls_context,
    cmdData.input_signing_region, None, proxy_options)
resp_future = discovery_client.discover(cmdData.input_thing_name)
discover_response = resp_future.result()

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

                    connect_future = mqtt_connection.connect()
                    connect_future.result()
                    print('Connected!')
                    return mqtt_connection

                except Exception as e:
                    print('Connection failed with exception {}'.format(e))
                    continue

    exit('All connection attempts failed')


mqtt_connection = try_iot_endpoints()

if cmdData.input_mode == 'both' or cmdData.input_mode == 'subscribe':
    def on_publish(topic, payload, dup, qos, retain, **kwargs):
        print('Publish received on topic {}'.format(topic))
        print('Payload: ',payload) # MODIFICADO POR MI PARA LEER MEJOR LA CONSOLA
        print('-------------------------------------------------------------------') # ESTA LINEA FUE AÑADIDA POR MÍ PARA LEER MÁS FÁCIL LA CONSOLA
    subscribe_future, _ = mqtt_connection.subscribe(cmdData.input_topic, QoS.AT_MOST_ONCE, on_publish)
    subscribe_result = subscribe_future.result()

loop_count = 0
while loop_count < cmdData.input_max_pub_ops:
    if cmdData.input_mode == 'both' or cmdData.input_mode == 'publish':
        message = {}
        message['message'] = cmdData.input_message
        message['sequence'] = loop_count
        messageJson = json.dumps(message)
        pub_future, _ = mqtt_connection.publish(cmdData.input_topic, messageJson, QoS.AT_LEAST_ONCE)
        publish_completion_data = pub_future.result()
        
        #print(f"DEBUG: Contenido de publish_completion_data = {publish_completion_data}") # ESTA LINEA FUE AÑADIDA POR MI PARA SABER QUÉ TIENE DENTRO PUBLISH_COMPLETION_DATA
        # print('Published topic {}: {} (puback reason: {})\n'.format(cmdData.input_topic, messageJson, repr(publish_completion_data.puback.reason_code))) # ESTA LINEA DA ERROR PORQUE AL PARECER LA VERSION DE AWS_IOT_DEVICE_SDK INSTALADA Y LA DE LA DOCUMENTACION NO COINCIDEN Y YA NO SE EMPLEA EL ATRIBUTO 'PUBACK' DENTRO DEL DICCIONARIO DE PUBLISH_COMPLETION_DATA
        print(f'Published topic {cmdData.input_topic}: {messageJson} (packet_id: {publish_completion_data["packet_id"]})')

        loop_count += 1
    time.sleep(1)
