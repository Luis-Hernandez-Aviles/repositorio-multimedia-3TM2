// Variable para verificar y saber si el asistente esta en "modo escucha" de opciones
let asistenteActivado = false;

// Configuracion de la voz del asistente
const synth = window.speechSynthesis;

function hablar(texto) {
  // Mostramos tambien el texto en pantalla
  let outputArea = document.getElementById('output-area');
  if (outputArea) outputArea.innerHTML = texto;

  // Creamos el objeto de voz
  let utterThis = new SpeechSynthesisUtterance(texto);
  utterThis.lang = 'es-MX'; // Idioma de la voz
  utterThis.rate = 1;       // Velocidad de la voz
  synth.speak(utterThis);
}

function iniciarAsistente() {
  // Inicializamos el reconocimiento
  var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = "es-MX";
  recognition.continuous = true; // Permite que escuche de forma continua
  recognition.interimResults = false;

  recognition.onresult = function(event) {
    // Obtenemos el ultimo resultado detectado
    let lastIndex = event.results.length - 1;
    let transcript = event.results[lastIndex][0].transcript.toLowerCase();
    
    console.log("Escuchado:", transcript);

    // Si el asistente esta hablando, ignoramos lo que escucha para que no se escuche a si mismo
    if (synth.speaking) return;

    // LOGICA DE NIVELES
    if (!asistenteActivado) {
      // NIVEL 1: Esperando la palabra activadora (estado de stand by)
      if (transcript.includes("talleres")) {
        asistenteActivado = true; // Cambiamos el estado
        hablar("¿Cuál es el taller de tu interés?");
      }
    } else {
      // NIVELES 2, 3 y 4: El asistente ya fue activado, espera la categoria correspondiente
      if (transcript.includes("cultural") || transcript.includes("culturales")) {
        hablar("Claro, los talleres impartidos en la UPIITA del sector cultural son: música, salsa, teatro, taller de rol, etcétera.");
        asistenteActivado = false; // Se apaga el estado para que espere la palabra activadora "talleres" de nuevo
      
      } else if (transcript.includes("deporte") || transcript.includes("deportes") || transcript.includes("deportivo")) {
        hablar("Claro, los talleres impartidos en la UPIITA del sector deportivo son: futbol, basketball, volleyball, calistenia, karate, etcétera.");
        asistenteActivado = false;
      
      } else if (transcript.includes("académico") || transcript.includes("académicos") || transcript.includes("académicas")) {
        hablar("Claro, las asociaciones impartidas en la UPIITA son: Ocelot racing, open source upiita, las distintas ramas I E E E como SIGHT, EMBS, RAS, etcétera.");
        asistenteActivado = false;
      
      } else if (transcript.includes("cancelar") || transcript.includes("ninguno")) {
        // Opcion extra de seguridad por si el usuario se arrepiente o no esta del todo seguro
        hablar("De acuerdo, cancelando consulta de talleres.");
        asistenteActivado = false;
      }
    }
  };

  // Si el reconocimiento se apaga por silencio, se vuelve a encender
  recognition.onend = function() {
    recognition.start();
  };

  // Arranque del microfono
  recognition.start();
}

// Nota:Como se pidio la omision del boton, el asistente se inicia en cuanto se cargue la pagina
window.onload = function() {
  iniciarAsistente();
};