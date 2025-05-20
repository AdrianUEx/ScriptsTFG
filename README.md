# ScriptsTFG
Scripts usados a lo largo del TFG

## Scripts de consumo energético
* ConsumoenergeticoShelly.js : el primer script creado para el Shelly Plus 1PM. Mide el consumo en periodos de un segundo.
* ConsumoenergeticoShelly_500ms.js: una versión mejorada del primer script. Este segundo script mide el consumo en periodos de medio segundo, siguiendo la sugerencia del cotutor. Además permite recoger métricas separadas por coma y presenta una tabla de equivalencias para regular los valores de las variables de ajuste para recuperar las métricas según la necesidad.
* ConsumoenergeticoShelly_500ms_v2: un prototipo de mejora fallido del script anterior. La consola del Shelly no es capaz de mostrar correctamente valores complejos a la velocidad suficiente, por lo que no se pueden recuperar los valores en formato CSV listos para ser usados.
