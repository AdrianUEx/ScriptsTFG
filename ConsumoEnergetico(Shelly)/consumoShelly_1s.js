// Código creado por Adrián Barquilla Rodríguez, 2025

// Ejecuta cada 60 segundos (60000 ms)
// Ejecuta cada 1 segundos (1000 ms)
/*Timer.set(1000, true, function () {
  Shelly.call(
    "Switch.GetStatus",
    { id: 0 },
    function (res) {
      let apower = res.apower;
      let by_minute = res.aenergy.by_minute;
      let minute_ts = res.aenergy.minute_ts;

      print("------");
      print("apower:", apower, "W");
      console.clear();
    },
    function (res) {
      let by_minute = res.aenergy.by_minute;
      let minute_ts = res.aenergy.minute_ts;
      
      print("------");
      print("Último minuto (mWh):", by_minute[by_minute.length - 1]); //Recupera la última posición del array (la que indica el consumo en el último minuto desde el tick de reloj)
      print("Timestamp inicio serie:", minute_ts);
    }
  );
}, null);*/


let apower_samples = [];

// Ejecutar cada 1 segundo
Timer.set(1000, true, function () {
  Shelly.call("Switch.GetStatus", { id: 0 }, function (res) { //llamada a API Shelly.GetStatus?id=0
    let apower = res.apower;
    print("apower: ", apower);
    // Añadir muestra
    if(apower_samples)
      apower_samples.push(apower);

    // Calcular media si ya hay 60 muestras
    if (apower_samples.length === 60) {
      let arrayMedia = apower_samples;
      apower_samples = []; //Resetea el array para el siguiente minuto
      let sum = 0;
      for (let i = 0; i < 60; i++) {
        sum += arrayMedia[i];
      }
      let avg = sum / 60;

      print("Promedio de consumo en 1 min:", avg.toFixed(2), "W");
    }
  });
}, null);