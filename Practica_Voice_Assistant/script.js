function listen() {
  let inputArea = document.getElementById('input-area')
  let outputArea = document.getElementById('output-area')

  var recognition = new webkitSpeechRecognition();
  recognition.lang = "es-MX"; //Modificacion de reconocedor configurado a español de mexico (es-MX)
  recognition.start();

  recognition.onresult = function(event) {
    let transcript = event.results[0][0].transcript.toLowerCase(); //.toLowerCase()-> Convierte lo que escucha a minusculas, evitando errores con mayuscula inicial
    
    console.log ("Trans:", transcript); //funcion que permite visualizar que fue lo que el programa escucho (mediante la inspeccion de la pagina en el navegador)
    
    if (transcript.includes("hello")) {
      outputArea.innerHTML = "Hello, User!"
    } else if (transcript.includes("weather")) {
      window.open("https://www.google.com/search?q=weather")
    } else if (transcript.includes("teacher")) {
      outputArea.innerHTML = "What do you want Chief..."
    } else if (transcript.includes("hora")){  //Agregando funcionalidad para que muestre la hora actual, al decir la palabra "hora".
      let horaActual = new Date().toLocaleTimeString();
      outputArea.innerHTML = "La hora exacta es: " + horaActual;
    }else if (transcript.includes("song")){
      window.open("https://youtu.be/RF0HhrwIwp0?si=KJ4T9mIP4et42OLf") //Agregando funcionalidad para que abra una canción de YT en otra ventana
      outputArea.innerHTML = "Reproduciendo la cancion...";
    }else {
      outputArea.innerHTML = "I don't know what you mean."
    }
  }
}