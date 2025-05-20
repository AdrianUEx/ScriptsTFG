/*
  Intervalo muestreo | Muestras por seg | 'total_length' (para 1 min)
  ------------------ | ---------------- | --------------------------- 
  1000 ms (1 s)      | 1                | 60                        
  500 ms (0.5 s)     | 2                | 120                      
  250 ms (0.25 s)    | 4                | 240                       
  200 ms (0.2 s)     | 5                | 300                       
  100 ms (0.1 s)     | 10               | 600                       
  50 ms (0.05 s)     | 20               | 1200                      
*/

let apower_samples = [];
const total_length = 120; // Muestra x 60
// Ejecutar cada 0'5s
Timer.set(500, true, function () {
  Shelly.call("Switch.GetStatus", { id: 0 }, function (res) { // Llamada a API Shelly.GetStatus?id=0
    print("apower: ", res.apower, " W");
    // Añadir muestra
    apower_samples.push(res.apower);

    // Calcular media si ya hay 120 muestras (al ser cada medio segundo, cada dos posiciones es un segundo)
    if (apower_samples.length === total_length) {
      let sum = 0;
      for (let i = 0; i < apower_samples.length; i++) {
        sum += apower_samples[i];
      }
      let avg = sum / apower_samples.length;

      print("Promedio consumo en 1 min:", avg.toFixed(2), "W");
      
      // Mostrar CSV
      print("Valores (CSV):", apower_samples.join(", "));

      //Reiniciar array para el siguiente minuto
      apower_samples=[];
    }
  });
}, null);