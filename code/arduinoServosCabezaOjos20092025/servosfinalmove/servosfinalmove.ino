#include <Servo.h> // Incluye la librería Servo

// Declaración de los objetos Servo
Servo myServo1;    // Primer servo
Servo myServo2;    // Segundo servo

// Definición de los pines para cada servo
const int servoPin1 = 9; // Pin para el primer servo
const int servoPin2 = 7; // Pin para el segundo servo

// Ángulos para el movimiento aleatorio de ambos servos
const int ANGLE_MIN_RANDOM = 30;  // Ángulo mínimo para el movimiento aleatorio
const int ANGLE_MAX_RANDOM = 90; // Ángulo máximo para el movimiento aleatorio
const int ANGLE_STOP = 90;         // <--- CAMBIO AQUÍ: Ángulo de inicio/parada a 0 grados

// Variables para el control de tiempo del movimiento aleatorio
unsigned long lastRandomMoveTime = 0;
const long RANDOM_MOVE_INTERVAL = 250; // Mover cada 100 milisegundos (ajusta a tu gusto)

// Variable de estado para saber si los servos deben estar moviéndose aleatoriamente
bool isMovingRandomly = false;
// Bandera para controlar si ambos servos ya han sido adjuntados
bool servosAttached = false; 

// Variables para depuración periódica
unsigned long lastDebugPrintTime = 0;
const long DEBUG_PRINT_INTERVAL = 1000; // Imprimir estado cada 1 segundo

void setup() {
  Serial.begin(9600); // Inicia la comunicación serial
  // Es bueno esperar un poco para que el monitor serial se abra
  // while (!Serial); // Descomenta si usas el monitor serial y quieres esperar
  Serial.println("------------------------------------");
  Serial.println("ARDUINO INICIADO / REINICIADO!");
  Serial.println("Esperando comandos de Python.");
  Serial.println("------------------------------------");

  // Inicializa el generador de números aleatorios con un valor impredecible
  randomSeed(analogRead(A0)); 
}

void loop() {
  // 1. Procesar comandos seriales de Python
  if (Serial.available() > 0) {
    char command = Serial.read(); // Lee el primer byte recibido

    // Consumir el resto de la línea, incluido el '\n'
    while (Serial.available() > 0) {
      Serial.read();
    }

    if (command == '1') {
      Serial.print("Comando '1' recibido. ");
      if (!servosAttached) { // Si los servos no están adjuntos, adjuntarlos y ponerlos en posición inicial
        myServo1.attach(servoPin1);
        myServo2.attach(servoPin2);
        servosAttached = true;
        // Establece una posición inicial al adjuntar para evitar saltos bruscos
        myServo1.write(ANGLE_STOP); // Ahora irá a 0 grados
        myServo2.write(ANGLE_STOP); // Ahora irá a 0 grados
        delay(50); // Pequeña pausa para que lleguen a esa posición
        Serial.println("Servos ADJUNTOS.");
      } else {
        Serial.println("Servos ya estaban adjuntos.");
      }
      isMovingRandomly = true;
      Serial.println("Activado modo de movimiento aleatorio para ambos servos.");
      
    } else if (command == '0') {
      Serial.print("Comando '0' recibido. ");
      isMovingRandomly = false;
      if (servosAttached) { // Solo mover si ya están adjuntos
          myServo1.write(ANGLE_STOP); // Ahora irá a 0 grados
          myServo2.write(ANGLE_STOP); // Ahora irá a 0 grados
          Serial.println("Servos movidos a posicion de parada.");
      } else {
          Serial.println("Servos no estaban adjuntos.");
      }
    }
  }

  // 2. Controlar el movimiento aleatorio si está activo
  if (isMovingRandomly) {
    unsigned long currentMillis = millis(); // Obtiene el tiempo actual
    // Si ha pasado el intervalo deseado desde el último movimiento
    if (currentMillis - lastRandomMoveTime >= RANDOM_MOVE_INTERVAL) {
      lastRandomMoveTime = currentMillis; // Actualiza el último tiempo de movimiento

      // Genera un ángulo aleatorio para el primer servo
      int randomAngle1 = random(ANGLE_MIN_RANDOM, ANGLE_MAX_RANDOM + 1); 
      // Genera un ángulo aleatorio diferente para el segundo servo
      int randomAngle2 = random(ANGLE_MIN_RANDOM, ANGLE_MAX_RANDOM + 1); 
      
      if (servosAttached) { // Asegurarse de que los servos estén adjuntos antes de escribir
          myServo1.write(randomAngle1); // Mueve el primer servo al nuevo ángulo aleatorio
          myServo2.write(randomAngle2); // Mueve el segundo servo al nuevo ángulo aleatorio
          
          // Descomentar para ver cada movimiento, pero puede inundar el serial
          // Serial.print("Mov. Servo1 a: "); Serial.print(randomAngle1);
          // Serial.print(", Servo2 a: "); Serial.println(randomAngle2);              
      }
    }
  }

  // 3. Depuración periódica del estado
  unsigned long currentMillis = millis(); // Volver a obtener el tiempo actual
  if (currentMillis - lastDebugPrintTime >= DEBUG_PRINT_INTERVAL) {
    lastDebugPrintTime = currentMillis;
    Serial.print("Estado actual - isMovingRandomly: ");
    Serial.println(isMovingRandomly ? "TRUE" : "FALSE");
    if (!servosAttached) {
      Serial.println("Servos NO ADJUNTOS.");
    }
  }
}

