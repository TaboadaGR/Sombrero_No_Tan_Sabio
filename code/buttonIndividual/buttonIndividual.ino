// Definir el pin digital donde está conectado el botón.

// Conecta una de las patas del botón al pin 2 y la otra a GND.

const int buttonPin = 2;



// Usamos esta variable para detectar cuándo se pulsa el botón.

// La inicializamos a HIGH porque con la resistencia interna (INPUT_PULLUP)

// el pin está en HIGH por defecto cuando no se pulsa el botón.

int lastButtonState = HIGH;



void setup() {

  // Inicia la comunicación serie a 9600 baudios.

  // ¡IMPORTANTE! Este valor (9600) debe ser el mismo que uses en Python.

  Serial.begin(9600);



  // Configura el pin del botón como una entrada con una resistencia interna.

  // Esto evita que el pin "flote" y facilita el cableado.

  pinMode(buttonPin, INPUT_PULLUP);



  // Mensajes de bienvenida que solo se imprimen una vez, al inicio.

  Serial.println("Arduino iniciado. Listo para recibir una pulsacion.");

  Serial.println("Pulsa el boton en el pin 2 para enviar 'B'.");

  Serial.println("------------------------------------");

}



void loop() {

  // Lee el estado actual del botón (HIGH o LOW).

  int currentButtonState = digitalRead(buttonPin);



  // Comprueba si el estado ha cambiado de HIGH a LOW.

  // Esto significa que el botón acaba de ser pulsado.

  if (currentButtonState == LOW && lastButtonState == HIGH) {

    // Si se detecta la pulsación, envía la letra 'B' seguida de un salto de linea.

    Serial.println("B");

    // Espera un momento para evitar que un solo toque envíe multiples 'B's

    // (un fenómeno llamado "rebote").

    delay(10);

  }



  // Guarda el estado actual del botón para la siguiente vez que se ejecute el loop.

  lastButtonState = currentButtonState;

}
