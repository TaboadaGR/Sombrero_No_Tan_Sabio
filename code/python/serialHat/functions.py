import serial
import time
import logging

logger = logging.getLogger("main_logger")

def open_serial_port(com_port, baudrate):
    """Abre y configura el puerto serial para Arduino."""
    try:
        ser = serial.Serial(com_port, baudrate, timeout=1)
        time.sleep(2)  # Esperar a que Arduino se reinicie y establezca la conexión
        if ser.in_waiting:
            ser.read(ser.in_waiting) # Vaciar buffer de entrada
        logging.info(f"Puerto serie '{com_port}' abierto correctamente.")
        print(f"Puerto serie '{com_port}' abierto correctamente.")
        return ser
    except serial.SerialException as e:
        logging.error(f"Error al abrir el puerto '{com_port}': {e}")
        print(f"Error: No se pudo abrir el puerto '{com_port}'. Asegúrate de que Arduino esté conectado y el puerto sea correcto.")
        print(f"Detalle del error: {e}")
        return None

def send_servo_command(ser_port, command):
    """Envía un comando '1' (mover) o '0' (detener) al servo a través de Arduino."""
    if ser_port and ser_port.is_open:
        try:
            message = f"{command}\n" # Añade salto de línea para que Arduino sepa cuándo termina el comando
            ser_port.write(message.encode()) # Codifica el mensaje a bytes
            logging.debug(f"Enviado a Arduino: {message.strip()}") # strip() para no loguear el '\n'
            if command == '1':
                print("Servo: MOVING")
            elif command == '0':
                print("Servo: STOPPED")
            time.sleep(0.02) # Pequeño delay después de enviar para dar tiempo a Arduino a procesar
            return True
        except Exception as e:
            logging.error(f"Error al enviar comando '{command}' a Arduino: {e}", exc_info=True)
            print(f"Error crítico de comunicación con Arduino: {e}")
            return False
    else:
        logging.warning(f"Intento de enviar comando '{command}', pero el puerto serial no está abierto.")
        return False

def close_serial_port(ser_port):
    """Cierra el puerto serial si está abierto."""
    if ser_port and ser_port.is_open:
        ser_port.close()
        logging.info("Puerto serie cerrado.")
        print("Puerto serie cerrado.")

def read_arduino_feedback(ser_port):
    """Lee y muestra los mensajes de depuración que Arduino envía, incluyendo ángulos."""
    if ser_port and ser_port.is_open and ser_port.in_waiting > 0:
        try:
            feedback = ser_port.readline().decode().strip()
            if feedback:
                print(f"[ARDUINO]: {feedback}") # Siempre imprime el mensaje crudo para depuración

                # Parse specific servo feedback messages from Arduino
                if feedback.startswith("[START_ANGLE]:"):
                    parts = feedback.split(":")[1:]
                    if len(parts) == 2 and parts[0].startswith("S1=") and parts[1].startswith("S2="):
                        angle1 = parts[0].split("=")[1]
                        angle2 = parts[1].split("=")[1]
                        print(f"    [Servo Info]: Servos inician movimiento desde HOME_ANGLE: S1={angle1}°, S2={angle2}°")
                elif feedback.startswith("[FINAL_ANGLE]:"):
                    parts = feedback.split(":")[1:]
                    if len(parts) == 2 and parts[0].startswith("S1=") and parts[1].startswith("S2="):
                        angle1 = parts[0].split("=")[1]
                        angle2 = parts[1].split("=")[1]
                        print(f"    [Servo Info]: Servos finalizan movimiento en HOME_ANGLE: S1={angle1}°, S2={angle2}°")
                elif feedback.startswith("[CURRENT_ANGLES]:"):
                    parts = feedback.split(":")[1:]
                    if len(parts) == 2 and parts[0].startswith("S1=") and parts[1].startswith("S2="):
                        angle1 = parts[0].split("=")[1]
                        angle2 = parts[1].split("=")[1]
                        print(f"    [Servo Info]: S1 a: {angle1}°, S2 a: {angle2}° (Movimiento aleatorio)")
                # Add more conditions for other Arduino debug messages if needed
                
                logging.debug(f"Recibido de Arduino: {feedback}")
        except Exception as e:
            logging.error(f"Error al leer feedback de Arduino: {e}", exc_info=True)
            print(f"[ARDUINO ERROR]: {e}")
