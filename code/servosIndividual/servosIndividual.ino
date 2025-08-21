#include <Servo.h>

// --- Definición del pin para el servo ---
const int servoPin = 9;

// --- Creación del objeto Servo ---
Servo myServo;

// --- Variables para el control de movimiento ---
// Controla si el servo debe moverse o estar quieto
bool moving = false;
// Posición actual del servo
int currentPos; 
// Posición objetivo a la que se moverá
int targetPos;  

// --- Variables para la animación suave ---
long lastMoveTime = 0;
// Aumentado a 25 ms para un movimiento más lento y orgánico
const int moveInterval = 25; 

void setup() {
  // Inicializa la comunicación serial con el ordenador
  Serial.begin(9600);
  // Adjunta el servo al pin 9
  myServo.attach(servoPin);
  
  // Establece la posición inicial del servo en 0 grados
  myServo.write(90); // Se establece la posición central inicial
  currentPos = 90;
  targetPos = 90; // El objetivo inicial también es 90
  
  // Pequeña pausa para que el servo se asiente
  delay(1000); 

  Serial.println("Arduino: Ready to receive commands.");
}

void loop() {
  // --- 1. Procesamiento de comandos seriales ---
  if (Serial.available() > 0) {
    // Lee la cadena completa hasta el salto de línea
    String command = Serial.readStringUntil('\n');
    command.trim(); // Elimina espacios en blanco

    if (command == "1") {
      moving = true;
      Serial.println("Arduino: Received '1'. Starting movement.");
    } else if (command == "0") {
      moving = false;
      Serial.println("Arduino: Received '0'. Stopping movement.");
      // Cuando se detiene, establece el objetivo a 0 para que regrese
      targetPos = 90; // Vuelve a la posición central
    }
  }

  // --- 2. Lógica de movimiento "orgánico" (solo si moving es true) ---
  if (moving) {
    // Si ha pasado el intervalo de movimiento...
    if (millis() - lastMoveTime > moveInterval) {
      lastMoveTime = millis();
      
      // Mueve el servo de forma independiente
      // Se ha reducido el rango de movimiento a random(1,2) para hacerlo más suave
      moveServo(myServo, currentPos, targetPos, random(1, 2));
      
      // Si el servo está cerca de su objetivo, establece uno nuevo
      if (abs(currentPos - targetPos) < 2) {
        setNewRandomTarget();
      }
    }
  } else {
    // Cuando se detiene el movimiento, mueve suavemente el servo a la posición central
    moveServo(myServo, currentPos, targetPos, 2);
  }
}

// Función para mover el servo de forma incremental
void moveServo(Servo& servo, int& currentPos, int& targetPos, int step) {
  if (currentPos < targetPos) {
    currentPos += step;
    if (currentPos > targetPos) currentPos = targetPos;
  } else if (currentPos > targetPos) {
    currentPos -= step;
    if (currentPos < targetPos) currentPos = targetPos;
  }
  servo.write(currentPos);
}

// Función para establecer un nuevo objetivo aleatorio
void setNewRandomTarget() {
  // Rango de 60 a 120 grados, que es 30 grados a cada lado del centro (90)
  targetPos = random(60, 121);
  Serial.print("Arduino: New target set: ");
  Serial.println(targetPos);
}


