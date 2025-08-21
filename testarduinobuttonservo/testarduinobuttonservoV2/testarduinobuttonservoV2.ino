#include <Servo.h> // Incluye la librería para controlar servos

// --- PINES DE CONEXIÓN ---
const int buttonPin = 2; // Pin digital para el botón
const int servoPin1 = 9; // Pin digital para el primer servo
const int servoPin2 = 7; // Pin digital para el segundo servo

// --- OBJETOS Y VARIABLES ---
Servo myServo1;    // Objeto para el primer servo
Servo myServo2;    // Objeto para el segundo servo

// Ángulos de movimiento para los servos
// Rango de movimiento de +/- 20 grados respecto al centro (90)
const int ANGLE_MIN_RANDOM = 70;
const int ANGLE_MAX_RANDOM = 110;
const int ANGLE_STOP = 0; // Posición de parada inicial

// Variables para la lógica del botón
int lastButtonState = HIGH; // Estado anterior del botón (INPUT_PULLUP es HIGH por defecto)

// Variables de control de movimiento
bool isMovingRandomly = false;
int targetAngle1 = ANGLE_STOP;
int targetAngle2 = ANGLE_STOP;
int currentAngle1 = ANGLE_STOP;
int currentAngle2 = ANGLE_STOP;
unsigned long lastMoveTime = 0;
const long MOVE_INTERVAL = 20; // Intervalo en milisegundos para actualizar el movimiento

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

  // Mueve los servos a la posición de parada inicial de forma suave
  smoothMove(myServo1, ANGLE_STOP, 5);
  smoothMove(myServo2, ANGLE_STOP, 5);
  currentAngle1 = ANGLE_STOP;
  currentAngle2 = ANGLE_STOP;
}

void loop() {
  // --- 1. PROCESAR COMANDOS SERIALES DEL PC ---
  if (Serial.available() > 0) {
    char command = Serial.read();

    if (command == '1') {
      Serial.println("Comando '1' recibido. Activando movimiento aleatorio...");
      isMovingRandomly = true;
    } else if (command == '0') {
      Serial.println("Comando '0' recibido. Deteniendo servos.");
      isMovingRandomly = false;
      // Los servos se moverán suavemente a la posición de parada
      targetAngle1 = ANGLE_STOP;
      targetAngle2 = ANGLE_STOP;
    }
  }

  // --- 2. DETECCIÓN DE BOTÓN ---
  int currentButtonState = digitalRead(buttonPin);
  if (currentButtonState == LOW && lastButtonState == HIGH) {
    delay(50);
    Serial.println("B");
  }
  lastButtonState = currentButtonState;

  // --- 3. CONTROL DEL MOVIMIENTO DE SERVOS ---
  unsigned long currentMillis = millis();

  if (isMovingRandomly) {
    // Genera un nuevo ángulo aleatorio si los servos han llegado a su destino
    if (currentAngle1 == targetAngle1 && currentAngle2 == targetAngle2) {
      targetAngle1 = random(ANGLE_MIN_RANDOM, ANGLE_MAX_RANDOM + 1);
      targetAngle2 = random(ANGLE_MIN_RANDOM, ANGLE_MAX_RANDOM + 1);
    }
    
    // Mueve los servos suavemente hacia el ángulo objetivo
    if (currentMillis - lastMoveTime >= MOVE_INTERVAL) {
      lastMoveTime = currentMillis;

      if (currentAngle1 < targetAngle1) {
        currentAngle1++;
      } else if (currentAngle1 > targetAngle1) {
        currentAngle1--;
      }
      myServo1.write(currentAngle1);

      if (currentAngle2 < targetAngle2) {
        currentAngle2++;
      } else if (currentAngle2 > targetAngle2) {
        currentAngle2--;
      }
      myServo2.write(currentAngle2);
    }
  } else {
    // Si el movimiento aleatorio está detenido, asegura que los servos vuelvan a 0
    if (currentAngle1 != ANGLE_STOP || currentAngle2 != ANGLE_STOP) {
      if (currentMillis - lastMoveTime >= MOVE_INTERVAL) {
        lastMoveTime = currentMillis;

        if (currentAngle1 > ANGLE_STOP) {
          currentAngle1--;
        }
        if (currentAngle2 > ANGLE_STOP) {
          currentAngle2--;
        }
        myServo1.write(currentAngle1);
        myServo2.write(currentAngle2);
      }
    }
  }
}

// Función auxiliar para mover un servo suavemente a un ángulo de destino
void smoothMove(Servo& servo, int target, int speed) {
  int current = servo.read();
  if (current < target) {
    for (int i = current; i <= target; i++) {
      servo.write(i);
      delay(speed);
    }
  } else {
    for (int i = current; i >= target; i--) {
      servo.write(i);
      delay(speed);
    }
  }
}

