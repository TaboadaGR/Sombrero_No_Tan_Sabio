import serial
import time
import pygame
import speech_recognition as sr
import pyttsx3
import logging
import os

# --- Obtener el directorio del script para rutas absolutas ---
script_dir = os.path.dirname(os.path.abspath(__file__))

# --- Configuración del Log ---
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
log_file = os.path.join(desktop_path, "log_sombrero_seleccionador.txt")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO, # Nivel de log por defecto (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- Configuración del Sintetizador de Voz (pyttsx3) ---
engine = pyttsx3.init()
engine.setProperty('rate', 180) # Velocidad de la voz (ajusta entre 150-250 para voz natural)
engine.setProperty('volume', 0.9) # Volumen (0.0 a 1.0)

# --- Configuración del Puerto Serial de Arduino ---
ARDUINO_PORT = 'COM4' # <--- ¡CAMBIA ESTO A TU PUERTO ARDUINO REAL!
BAUD_RATE = 9600

arduino = None # Variable global para la conexión serial

# --- Configuración de Nombres y Mesas ---
nombres_y_mesas = {
    "Juan Maldonado": ("Gryffindor", "mesa_1"),
    "María Lozano Olvera": ("Slytherin", "mesa_2"),
    "Pablo Lozano Olvera": ("Hufflepuff", "mesa_1"),
    "Álvaro David Taboada": ("Ravenclaw", "mesa_1"),
    "Ascenion Olvera Raya": ("Gryffindor", "mesa_1"),
    "Manuel": ("Ravenclaw", "mesa_12"),
    "Pepe": ("Hufflepuff", "mesa_1"),
    "Antonio": ("Ravenclaw", "mesa_1"),
    "Lucia": ("Gryffindor", "mesa_1"),
    "Alvaro": ("Ravenclaw", "mesa_2"), # Versión corta si se reconoce así
    "Pablo": ("Gryffindor", "mesa_1"), # Si hay dos "Pablo", el primero en la lista será el que se use
    "Jorge Lozano Lozano": ("Ravenclaw", "mesa_2"), # Añadido para el caso específico
    "Silvia Martín Díaz": ("Ravenclaw", "MESA_1") # Añadido para el caso específico
}

# --- Inicialización del Reconocimiento de Voz ---
recognizer = sr.Recognizer()
mic = sr.Microphone()

# --- Funciones de Serial ---
def open_serial_port(com_port, baudrate):
    """Abre y configura el puerto serial para Arduino."""
    try:
        ser = serial.Serial(com_port, baudrate, timeout=1)
        time.sleep(2) # Esperar a que Arduino se reinicie y establezca la conexión
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
                        print(f"     [Servo Info]: Servos inician movimiento desde HOME_ANGLE: S1={angle1}°, S2={angle2}°")
                elif feedback.startswith("[FINAL_ANGLE]:"):
                    parts = feedback.split(":")[1:]
                    if len(parts) == 2 and parts[0].startswith("S1=") and parts[1].startswith("S2="):
                        angle1 = parts[0].split("=")[1]
                        angle2 = parts[1].split("=")[1]
                        print(f"     [Servo Info]: Servos finalizan movimiento en HOME_ANGLE: S1={angle1}°, S2={angle2}°")
                elif feedback.startswith("[CURRENT_ANGLES]:"):
                    parts = feedback.split(":")[1:]
                    if len(parts) == 2 and parts[0].startswith("S1=") and parts[1].startswith("S2="):
                        angle1 = parts[0].split("=")[1]
                        angle2 = parts[1].split("=")[1]
                        print(f"     [Servo Info]: S1 a: {angle1}°, S2 a: {angle2}° (Movimiento aleatorio)")
                # Add more conditions for other Arduino debug messages if needed
                
                logging.debug(f"Recibido de Arduino: {feedback}")
        except Exception as e:
            logging.error(f"Error al leer feedback de Arduino: {e}", exc_info=True)
            print(f"[ARDUINO ERROR]: {e}")

# --- Funciones de Audio con Pygame ---
def init_pygame_mixer():
    """Inicializa el mezclador de Pygame."""
    try:
        pygame.mixer.init()
        logging.info("Pygame mixer inicializado.")
        return True
    except Exception as e:
        logging.error(f"Error al inicializar Pygame mixer: {e}", exc_info=True)
        print(f"Error: No se pudo inicializar Pygame mixer. Asegúrate de tener tarjeta de sonido y drivers.")
        return False

def play_audio_and_control_servo(file_path, ser_port, servo_home_angle_concept=0):
    """
    Reproduce un archivo de audio y controla el servo:
    Envía '1' (iniciar movimiento aleatorio) antes de reproducir,
    espera a que termine, y luego envía '0' (detener y regresar a HOME_ANGLE).
    
    servo_home_angle_concept: Este parámetro es conceptual en Python.
    El Arduino tiene su propio HOME_ANGLE calibrado. Python solo le indica
    que inicie/detenga el movimiento aleatorio.
    """
    # Usamos os.path.join para construir la ruta completa del archivo de audio
    full_path = os.path.join(script_dir, file_path)

    if not os.path.exists(full_path):
        logging.error(f"Archivo de audio no encontrado: {full_path}")
        print(f"Error: El archivo de audio '{full_path}' no existe.")
        return False

    try:
        # 1. Enviar comando para INICIAR el movimiento aleatorio en Arduino
        # El Arduino moverá los servos a su HOME_ANGLE interno y luego iniciará el movimiento aleatorio.
        if ser_port:
            if not send_servo_command(ser_port, '1'):
                logging.warning("No se pudo iniciar el movimiento del servo antes de reproducir el audio.")
        
        # 2. Cargar y reproducir el audio
        pygame.mixer.music.load(full_path)
        pygame.mixer.music.play()
        logging.info(f"Reproduciendo audio: {full_path}")
        print(f"Reproduciendo: {full_path}")
        
        # 3. Esperar a que el audio termine y leer feedback de Arduino
        while pygame.mixer.music.get_busy():
            read_arduino_feedback(ser_port) # <-- Leer feedback mientras el audio suena
            time.sleep(0.1) # Pequeña pausa para no consumir mucha CPU
        
        logging.info(f"Audio '{full_path}' terminado.")
        print(f"Audio '{full_path}' terminado.")
        
        # 4. Enviar comando para DETENER el movimiento aleatorio en Arduino
        # El Arduino regresará los servos a su HOME_ANGLE interno.
        if ser_port:
            if not send_servo_command(ser_port, '0'):
                logging.warning("No se pudo detener el servo después de reproducir el audio.")
                
        return True # Audio reproducido y servo controlado con éxito
    
    except Exception as e:
        logging.error(f"Error durante la reproducción de audio y control del servo para '{full_path}': {e}", exc_info=True)
        print(f"Error al reproducir '{full_path}': {e}")
        # Si ocurre un error, asegúrate de enviar el comando de detener al servo
        if ser_port:
            send_servo_command(ser_port, '0')
        return False

def speak_text(text):
    """Sintetiza texto a voz."""
    engine.say(text)
    engine.runAndWait()

def play_sound_effect(file_path):
    """Reproduce un efecto de sonido sin controlar el servo (no bloqueante)."""
    # Usamos os.path.join para construir la ruta completa del archivo de audio
    full_path = os.path.join(script_dir, file_path)

    if not os.path.exists(full_path):
        logging.warning(f"Efecto de sonido no encontrado: {full_path}")
        print(f"Advertencia: El efecto de sonido '{full_path}' no existe.")
        return False
    try:
        sound = pygame.mixer.Sound(full_path) # Usar Sound para efectos cortos
        sound.play()
        logging.debug(f"Reproduciendo efecto: {full_path}")
        return True
    except Exception as e:
        logging.error(f"Error al reproducir efecto de sonido '{full_path}': {e}", exc_info=True)
        print(f"Error al reproducir efecto de sonido: {e}")
        return False

# --- Bucle principal del programa ---
if __name__ == "__main__":
    # 1. Inicializar Audio de Pygame
    if not init_pygame_mixer():
        print("No se pudo iniciar el sistema de audio. Saliendo.")
        exit()

    # 2. Abrir Puerto Serial de Arduino
    arduino = open_serial_port(ARDUINO_PORT, BAUD_RATE)
    
    # Asegurarse de que el servo esté parado al inicio (por si el Arduino se reinicia)
    if arduino:
        send_servo_command(arduino, '0')
        time.sleep(0.5) # Pequeña pausa para que el servo se asiente

    # --- Bucle externo infinito para reiniciar el programa ---
    while True:
        # --- LÓGICA DE ACTIVACIÓN: Esperar la frase de activación ---
        print("\nPrograma listo, esperando la frase clave 'sombrero seleccionador'...")
        logging.info("Esperando la frase de activación...")
        
        activacion_exitosa = False
        while not activacion_exitosa:
            with mic as source:
                print("🎤 Diga 'sombrero seleccionador' para continuar:")
                recognizer.adjust_for_ambient_noise(source)
                try:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
                except sr.WaitTimeoutError:
                    print("No se detectó voz. Reintentando...")
                    continue
                
                try:
                    frase_detectada = recognizer.recognize_google(audio, language="es-ES").lower()
                    print(f"👂 Escuché: {frase_detectada}")
                    if "sombrero seleccionador" in frase_detectada:
                        print("✔️ Frase clave detectada. ¡Iniciando el proceso de asignación!")
                        logging.info("Frase de activación detectada. Continuando con la asignación.")
                        play_sound_effect(os.path.join('voice', 'fx', 'bell.mp3')) 
                        activacion_exitosa = True
                    else:
                        print("❌ Frase incorrecta. Intente de nuevo.")
                except sr.UnknownValueError:
                    print("❌ No entendí lo que dijiste. Intente de nuevo.")
                except sr.RequestError as e:
                    print(f"❌ Error al conectar con el servicio de voz de Google; {e}")
                    logging.error(f"Error de conexión con Google Speech Recognition: {e}")
                
                time.sleep(1) # Pausa para no saturar el bucle

        # --- Bucle principal del programa (Solo se ejecuta después de la activación) ---
        print("\n¡Bienvenido al Sombrero Seleccionador!")
        logging.info("Iniciando secuencia del Sombrero Seleccionador.")

        # Reproduce el audio de inicio y controla el servo automáticamente
        print("Reproduciendo audio de bienvenida...")
        play_audio_and_control_servo(os.path.join('voice', 'welcome', 'sombreo_inicio.mp3'), arduino, servo_home_angle_concept=0) 

        try:
            intentos = 0
            max_intentos = 3 # Número máximo de intentos antes de salir
            while True:
                # Leer feedback de Arduino continuamente en el bucle principal
                if not pygame.mixer.music.get_busy(): 
                    read_arduino_feedback(arduino)

                with mic as source:
                    print("\n🎤 Di tu nombre:")
                    recognizer.adjust_for_ambient_noise(source)
                    try: # Añadido timeout para evitar esperas infinitas si no hay voz
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    except sr.WaitTimeoutError:
                        print("No se detectó voz. Reintentando...")
                        intentos += 1
                        if intentos >= max_intentos:
                            logging.warning("Máximo de intentos de escucha alcanzado. Saliendo.")
                            break # Salir del bucle interno
                        continue # Volver a intentar escuchar

                    try:
                        nombre = recognizer.recognize_google(audio, language="es-ES")
                        print(f"👂 Escuché: {nombre}")
                        nombre_formateado = nombre.title() # Pone la primera letra de cada palabra en mayúscula

                        if nombre_formateado in nombres_y_mesas:
                            # --- Lógica para nombres específicos (Silvia y Jorge) ---
                            if nombre_formateado == "Silvia Martín Díaz":
                                print("Reproduciendo audio de Silvia")
                                if not play_audio_and_control_servo(os.path.join('voice', 'SilviaJorge', 'silvia_final.mp3'), arduino, servo_home_angle_concept=0):
                                    print(f"⚠️ Error al reproducir audio de Silvia y controlar el servo.")
                                time.sleep(1) # Pausa entre audios
                                if not play_audio_and_control_servo(os.path.join('voice', 'table', 'MESA_1.mp3'), arduino, servo_home_angle_concept=0):
                                    print(f"⚠️ Error al reproducir audio de MESA_1 y controlar el servo.")
                            elif nombre_formateado == "Jorge Lozano Lozano":
                                print("Reproduciendo audio de Jorge")
                                if not play_audio_and_control_servo(os.path.join('voice', 'SilviaJorge', 'jorge_final.mp3'), arduino, servo_home_angle_concept=0):
                                    print(f"⚠️ Error al reproducir audio de Jorge y controlar el servo.")
                                time.sleep(1) # Pausa entre audios
                                if not play_audio_and_control_servo(os.path.join('voice', 'table', 'mesa_2.mp3'), arduino, servo_home_angle_concept=0):
                                    print(f"⚠️ Error al reproducir audio de mesa_2 y controlar el servo.")
                            # --- Lógica general para otras casas/mesas ---
                            else:
                                casa, mesa = nombres_y_mesas[nombre_formateado]
                                print(f"✔️ Nombre reconocido: {nombre_formateado}, Casa: {casa}, Mesa: {mesa}")
                                logging.info(f"Nombre reconocido: {nombre_formateado}, Casa: {casa}, Mesa: {mesa}")

                                # Reproduce el audio de la casa y controla el servo
                                audio_casa_path = os.path.join('voice', 'house', f"{casa}_audio.mp3") 
                                if not play_audio_and_control_servo(audio_casa_path, arduino, servo_home_angle_concept=0):
                                    print(f"⚠️ Error al reproducir audio de casa: {audio_casa_path}. Posible desincronización del servo.")

                                time.sleep(0.5) # Pequeña pausa entre audios si lo necesitas

                                # Reproduce el audio de la mesa y controla el servo
                                audio_mesa_path = os.path.join('voice', 'table', f"{mesa}.mp3")
                                if not play_audio_and_control_servo(audio_mesa_path, arduino, servo_home_angle_concept=0):
                                    print(f"⚠️ Error al reproducir audio de mesa: {audio_mesa_path}. Posible desincronización del servo.")
                            
                            logging.info("Secuencia de casa/mesa completada.")
                            break # Salir del bucle interno
                        else:
                            intentos += 1
                            print(f"❌ Nombre no encontrado. Intento {intentos}/{max_intentos}")
                            logging.info(f"Nombre no encontrado: {nombre}. Intento {intentos}/{max_intentos}")
                            
                            error_audio_path = os.path.join('voice', 'error', 'sombreo_inicio_error.mp3')
                            if not play_audio_and_control_servo(error_audio_path, arduino, servo_home_angle_concept=0):
                                print(f"⚠️ Error al reproducir audio de error y controlar el servo.")

                            if intentos >= max_intentos:
                                logging.warning("Máximo de intentos de nombre no encontrado alcanzado. Saliendo.")
                                break # Salir del bucle interno

                    except sr.UnknownValueError:
                        intentos += 1
                        print(f"❌ No entendí lo que dijiste. Intento {intentos}/{max_intentos}")
                        logging.info(f"No se detectó entendimiento. Intento {intentos}/{max_intentos}")
                        
                        error_audio_path = os.path.join('voice', 'welcome', 'sombreo_inicio_error.mp3')
                        if not play_audio_and_control_servo(error_audio_path, arduino, servo_home_angle_concept=0):
                            print(f"⚠️ Error al reproducir audio de error y controlar el servo.")

                        if intentos >= max_intentos:
                            logging.warning("Máximo de intentos de no entendimiento alcanzado. Saliendo.")
                            break # Salir del bucle interno

                    except sr.RequestError as e:
                        logging.error(f"Error al solicitar resultados del servicio de reconocimiento de voz de Google; {e}", exc_info=True)
                        print(f"❌ Error al conectar con el servicio de voz de Google; {e}")
                        time.sleep(2) # Esperar un poco antes de reintentar
                        # No incrementamos intentos por problemas de red
        
        except KeyboardInterrupt:
            print("\nPrograma interrumpido por el usuario (Ctrl+C).")
            logging.info("Programa interrumpido por usuario.")
            break # Salir del bucle externo para limpiar y finalizar

        except Exception as e:
            logging.critical(f"Error inesperado en el bucle principal de reconocimiento: {e}", exc_info=True)
            print(f"Error inesperado: {e}")
            break # Salir ante cualquier otro error crítico
    
    # --- PROCESO DE LIMPIEZA FINAL ---
    logging.info("Iniciando proceso de limpieza final.")
    # Asegurarse de detener servo y audio al finalizar o salir
    if arduino:
        print("Enviando comando de parada a Arduino...")
        send_servo_command(arduino, '0') # Comando final para detener el servo
        time.sleep(0.5)
        close_serial_port(arduino)
    pygame.mixer.quit() # Apagar el mezclador de Pygame
    logging.info("Pygame mixer apagado.")
    print("Pygame mixer apagado.")
    print("Programa finalizado.")
