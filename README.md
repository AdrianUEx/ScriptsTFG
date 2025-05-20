# ScriptsTFG
## Scripts de consumo energético
* **consumoShelly_1s.js** : el primer script creado para el Shelly Plus 1PM. Mide el consumo en periodos de un segundo.
* **consumoShelly_500ms.js** : una versión mejorada del primer script. Este segundo script mide el consumo en periodos de medio segundo, siguiendo la sugerencia del cotutor. Además permite recoger métricas separadas por coma y presenta una tabla de equivalencias para regular los valores de las variables de ajuste para recuperar las métricas según la necesidad.
* **consumoShelly_500ms_v2.js** : un prototipo de mejora fallido del script anterior. La consola del Shelly no es capaz de mostrar correctamente valores complejos a la velocidad suficiente, por lo que no se pueden recuperar los valores en formato CSV listos para ser usados.

## Scripts AWS
* **basic_discovery.py** : el script básico incluido en awsiotsdk. Cuenta con un fallo del *print()* al final donde pide valores del puback, pero no existe. Dicho fallo, debido a la falta de mantenimiento, está corregido. Manda 10 mensajes string genéricos y termina.

* **basic_discovery_v2.py** : cuenta con muchísimos comentarios nuevos. También cuenta con *print()* adicionales para organizar mejor la info por consola y mostrar otra info de utilidad para hacer debug. También cuenta con un método 'convertir_imagen_b64()' que no hace nada. 
Por último, este script lanza 10 veces un mensaje 'test' codificado en base64 con éxito para probar la codificación y el envío.

* **basic_discovery_v3.py** : esta mejora de la v2 incluye el nuevo método 'fragmentar_imagen_b64()' y el bucle *for* para lanzar los fragmentos. Se han optimizado los *print()*, y cuenta con algunas variables globales e imports nuevos. Manda los fragmentos con éxito una vez y cuenta el tiempo tardado.
  
* **basic_discovery_v4.py** : esta mejora de la v3 es capaz de mandar los mensajes durante un periodo de tiempo de 60 seg. Manda cada imagen con un segundo de intervalo, y cuenta con pequeños reajustes para los mensajes por consola.
  
* **basic_discovery_v4_40s.py** : una modificación de la v4, pero con un límite de 40s para ser medido por *iftop* en pruebas preliminares. Además, no cuenta con el *time.sleep(1)*, por lo que la ráfaga es continuada a máxima cadencia. 
También codifica la imagen solo una vez en lugar de hacerlo con cada iteración como en la v4 normal, siendo más eficiente, y muestra el número de imágenes completas enviadas.
* **basic_discovery_v4_60s.py** : Igual que la versión anterior solo que no se muestran los prints de envio de fragmento para ahorrar CPU. Es una versión completamente funcional para cumplir el objetivo de envío.

* **basic_discovery_v5_60s.py** : versión mejorada de basic_discovery_v4_60s, donde ya no se intenta recibir los datos en suscripción. Tampoco muestra la variable 'cmdData' por consola, por lo que queda más limpia la salida al lanzar el comando. Gracias a esto es una versión con menos consumo de CPU que las versiones anteriores.

* **basic_discovery_v6_60s.py** : Igual que la v5 en términos de rendimiento y consumo de recursos. Esta versión presenta un código mucho más limpio de comentarios para su posible reutilización y modificación en otros entornos.

## Scripts Azure
* **send_message.py** : versión básica que venía con el azureiotsdk. Cuenta con múltiples bucles *for* separados para mandar distintas ráfagas de mensajes.
* **send_message_v2_60s_127KB.py** : versión modificada del send_message.py básico. Se han eliminado los bucles for y se ha copiado el código desde basic_discovery.py. También se ha creado una variable con el connection_string necesario para poder conectarse al gateway. AL utilizar el mismo código que su homólogo de AWS, conforma una versión lista para su uso.
* **send_message_v2_60s_255KB.py** : mismo código que la versión de 127KB. En esta versión el tamaño máximo de mensaje es el doble que con IoT Core, siendo el máximo permitido por IoT Hub.
