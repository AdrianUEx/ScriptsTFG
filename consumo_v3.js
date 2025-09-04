/*
  TABLA DE CORRESPONDENCIAS
  Intervalo muestreo | Muestras por seg | 'total_length' para 1 min | 'total_length' para 5 min | 'total_length' para 10 min
  ------------------ | ---------------- | ------------------------- | ------------------------- | --------------------------
  1000 ms (1 s)      | 1                | 60                        | 300                       | 600
  500 ms (0.5 s)     | 2                | 120                       | 600                       | 1200
  250 ms (0.25 s)    | 4                | 240                       | 1200                      | 2400
  200 ms (0.2 s)     | 5                | 300                       | 1500                      | 3000
  100 ms (0.1 s)     | 10               | 600                       | 3000                      | 6000
  50 ms (0.05 s)     | 20               | 1200                      | 6000                      | 12000
*/

const intervalo_muestreo = 500; // Milisegundos
const total_length = 120; 

let apower_sum = 0;
let apower_count = 0;
let apower_bloque = [];
let contador_mensaje = 0;

// ------------ CUENTA ATRÁS ------------
let countdown = 10;
print("Comenzando en 10 segundos...");
let countdownTimer = Timer.set(1000, true, function () {
  countdown--;
  if (countdown > 0) {
    print("Empieza en " + countdown + " segundos...");
  } else {
    Timer.clear(countdownTimer);
    print("--------------- COMENZANDO MEDICIÓN ---------------");
    
    print("Valor inicial: " + Shelly.getComponentStatus("switch:0").apower);
    // ------------ INICIO DE MEDICIÓN ------------
    let muestreo_timer_handle = Timer.set(intervalo_muestreo, true, function () {
      let status = Shelly.getComponentStatus("switch:0");
      let apower = status.apower;

      // Acumular solo lo necesario
      apower_sum += apower;
      apower_count += 1;
      apower_bloque.push(apower);
      contador_mensaje++;

      // Imprimir cada minuto
      if (contador_mensaje === 120) {
        print("Fragmento último minuto:", apower_bloque.join(", "));
        apower_bloque = [];  // Limpiar bloque de muestras
        contador_mensaje = 0;

       // print("Tamaño bloque actual:", apower_bloque.length);
      }

      // Finalizar si se alcanzó el límite
      if (apower_count >= total_length) {
        print("------------------ FIN MEDICIÓN -------------------");
        Timer.clear(muestreo_timer_handle);
      }
    }, null);
  }
});