#include <Servo.h> // Incluye la librería para controlar servos

// --- PINES DE CONEXIÓN ---
const int buttonPin = 2; // Pin digital para el botón
const int servoPin1 = 9; // Pin digital para el primer servo
const int servoPin2 = 7; // Pin digital para el segundo servo

// --- OBJETOS Y VARIABLES ---
Servo myServo1;    // Objeto para el primer servo
Servo myServo2;    // Objeto para el segundo servo

// Ángulos de movimiento para los servos
const int ANGLE_MIN_RANDOM = 20;
const int ANGLE_MAX_RANDOM = 160;
const int ANGLE_STOP = 0; // Posición de parada inicial

// Variables para la lógica del botón
int lastButtonState = HIGH; // Estado anterior del botón (INPUT_PULLUP es HIGH por defecto)

// Variable de estado para controlar si los servos deben estar moviéndose
bool isMovingRandomly = false;

// Variables para el control de tiempo (para el movimiento aleatorio)
unsigned long lastRandomMoveTime = 0;
const long RANDOM_MOVE_INTERVAL = 100; // Mover cada 100 milisegundos

void setup() {
  // Inicia la comunicación serie a 9600 baudios
  Serial.begin(9600);
  Serial.println("------------------------------------");
  Serial.println("Sistema de control de servos iniciado.");
  Serial.println("Esperando comandos del PC.");
  Serial.println("------------------------------------");

  // Configura el pin del botón como entrada con resistencia interna
  pinMode(buttonPin, INPUT_PULLUP);

  // Adjunta los servos a sus respectivos pines
  myServo1.attach(servoPin1);
  myServo2.attach(servoPin2);

  // Mueve los servos a la posición de parada inicial
  myServo1.write(ANGLE_STOP);
  myServo2.write(ANGLE_STOP);
}

void loop() {
  // --- 1. PROCESAR COMANDOS SERIALES DEL PC ---
  if (Serial.available() > 0) {
    char command = Serial.read(); // Lee el primer byte recibido

    if (command == '1') {
      Serial.println("Comando '1' recibido. Activando movimiento aleatorio...");
      isMovingRandomly = true;
    } else if (command == '0') {
      Serial.println("Comando '0' recibido. Deteniendo servos.");
      isMovingRandomly = false;
      // Mueve los servos a la posición de parada inmediatamente
      myServo1.write(ANGLE_STOP);
      myServo2.write(ANGLE_STOP);
    }
  }

  // --- 2. DETECCIÓN DE BOTÓN ---
  int currentButtonState = digitalRead(buttonPin);

  // Comprueba si el botón acaba de ser pulsado (transición de HIGH a LOW)
  if (currentButtonState == LOW && lastButtonState == HIGH) {
    // Retardo para evitar el "rebote" del botón
    delay(50);
    // Envía la señal 'B' al PC.
    Serial.println("B");
  }
  
  // Guarda el estado actual del botón para la siguiente iteración
  lastButtonState = currentButtonState;

  // --- 3. CONTROL DEL MOVIMIENTO DE SERVOS ---
  if (isMovingRandomly) {
    unsigned long currentMillis = millis(); // Obtiene el tiempo actual
    
    // Si ha pasado el intervalo de tiempo, mueve los servos
    if (currentMillis - lastRandomMoveTime >= RANDOM_MOVE_INTERVAL) {
      lastRandomMoveTime = currentMillis; // Reinicia el contador de tiempo
      
      // Genera ángulos aleatorios para cada servo
      int randomAngle1 = random(ANGLE_MIN_RANDOM, ANGLE_MAX_RANDOM + 1);
      int randomAngle2 = random(ANGLE_MIN_RANDOM, ANGLE_MAX_RANDOM + 1);
      
      myServo1.write(randomAngle1); // Mueve el primer servo
      myServo2.write(randomAngle2); // Mueve el segundo servo
    }
  }
}

