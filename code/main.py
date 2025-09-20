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
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)


engine = pyttsx3.init()
engine.setProperty('rate', 180) 
engine.setProperty('volume', 0.9) 

# --- Configuración del Puerto Serial de Arduino ---
ARDUINO_PORT = '/dev/ttyACM0'
# ARDUINO_PORT = 'COM4'
BAUD_RATE = 9600

arduino = None 

# --- Configuración de Nombres y Mesas ---
nombres_y_mesas = {
    "Jorge Gardón": ("Slytherin", "mesa_13"),
    "Silvia Martín": ("Ravenclaw", "mesa_13"),
    "Agustín Martín": ("Gryffindor", "mesa_13"),
    "Silvia Díaz": ("Gryffindor", "mesa_13"),
    "Yolanda Gardón": ("Slytherin", "mesa_13"),
    "Maria Angustias Gardón": ("Hufflepuff", "mesa_1"),
    "Jose Manuel Ramirez": ("Hufflepuff", "mesa_1"),
    "Rosa Gardón": ("Hufflepuff", "mesa_1"),
    "Carmen Clavero": ("Muggle", "mesa_1"),
    "Maria Angustias Ramírez": ("Hufflepuff", "mesa_1"),
    "Fermín Balderas": ("Ravenclaw", "mesa_1"),
    "Christian Balderas": ("Ravenclaw", "mesa_1"),
    "Lucas Balderas": ("Muggle", "mesa_1"),
    "Violeta Rodríguez": ("Slytherin", "mesa_1"),
    "Ramón Gardón": ("Slytherin", "mesa_1"),
    "Rocío Sánchez": ("Slytherin", "mesa_1"),
    "Carmen Gardón": ("Slytherin", "mesa_1"),
    "Maribel Díaz": ("Slytherin", "mesa_2"),
    "José Antonio Frías": ("Gryffindor", "mesa_2"),
    "Mario Díaz": ("Hufflepuff", "mesa_2"),
    "Belén Quesada": ("Hufflepuff", "mesa_2"),
    "Maria del Carmen Díaz": ("Muggle", "mesa_2"),
    "Maria Reyes Díaz": ("Hufflepuff", "mesa_2"),
    "Juan de Dios Ariza": ("Hufflepuff", "mesa_2"),
    "Iván Martín": ("Gryffindor", "mesa_3"),
    "Maria Werfel": ("Ravenclaw", "mesa_3"),
    "Daniel Ariza": ("Gryffindor", "mesa_3"),
    "Claudia Ramal": ("Gryffindor", "mesa_3"),
    "Alejandro Ariza": ("Gryffindor", "mesa_3"),
    "Lorena Frías": ("Slytherin", "mesa_3"),
    "Manuel Frías": ("Gryffindor", "mesa_3"),
    "Inmaculada": ("Hufflepuff", "mesa_3"),
    "Belén Díaz": ("Hufflepuff", "mesa_3"),
    "Alejandro Cervera": ("Hufflepuff", "mesa_4"),
    "Mónica Carrasco": ("Hufflepuff", "mesa_4"),
    "Rocío Carrasco": ("Hufflepuff", "mesa_4"),
    "Alberto Aragón": ("Slytherin", "mesa_4"),
    "Javier Quirosa": ("Hufflepuff", "mesa_4"),
    "Marina Martín": ("Hufflepuff", "mesa_4"),
    "Estrella Quirosa": ("Slytherin", "mesa_4"),
    "Javier Álvarez": ("Gryffindor", "mesa_4"),
    "Aiden Álvarez": ("Gryffindor", "mesa_4"),
    "Gillian Álvarez": ("Gryffindor", "mesa_4"),
    "Oliver Calvo": ("Gryffindor", "mesa_5"),
    "Ester Moreno": ("Hufflepuff", "mesa_5"),
    "Nil Calvo": ("Slytherin", "mesa_5"),
    
    "Sión Calvo": ("Ravenclaw", "mesa_5"), #---------------|
    "Sion Calvo": ("Ravenclaw", "mesa_5"), #lo está pillando sin tilde sión
    
    "Paco Aguilar": ("Hufflepuff", "mesa_5"),
    
    "Antonio Lachica": ("Slytherin", "mesa_5"), #------------------------|
    "Antonio La chica": ("Slytherin", "mesa_5"), # hay que separar el apellido en dos lachica
    
    "Javier Gallegos": ("Ravenclaw", "mesa_5"),
    "Inmaculada Morillas": ("Ravenclaw", "mesa_5"),
    "Silvia": ("Slytherin", "mesa_5"),
    "Isabel Arnau": ("Hufflepuff", "mesa_5"),
    "Francisco Romero": ("Hufflepuff", "mesa_6"),
    "Jorge Lemus": ("Ravenclaw", "mesa_6"),
    "David Bermejo": ("Gryffindor", "mesa_6"),
    "David Guerra": ("Gryffindor", "mesa_6"),
    
    "ysmari Gil": ("Hufflepuff", "mesa_6"), #--------------|
    "ismari Gil": ("Hufflepuff", "mesa_6"), #lo pilla con i latina ysmari
    
    "Victoria Sofia Guerra": ("Ravenclaw", "mesa_6"),
    "Juan Carbonell": ("Slytherin", "mesa_6"),
    "Irene Burgos": ("Gryffindor", "mesa_7"),
    "Noemí Fernández": ("Hufflepuff", "mesa_7"),
    "Vicente García": ("Hufflepuff", "mesa_7"),
    "Laura Gregorio": ("Hufflepuff", "mesa_7"),
    "Sofía Atanasov": ("Hufflepuff", "mesa_7"),
    "Atanas Atanasov": ("Hufflepuff", "mesa_7"),
    "Juan Antonio Gregorio": ("Hufflepuff", "mesa_7"),
    "María Albertuz": ("Slytherin", "mesa_7"),
    "Noelia Herrera": ("Gryffindor", "mesa_8"),
    "David Higueras": ("Hufflepuff", "mesa_8"),
    "Sofía Higueras": ("Slytherin", "mesa_8"),
    "Ana María Fernández": ("Gryffindor", "mesa_8"),
    "Jose Espinosa": ("Gryffindor", "mesa_8"),
    "Angela Espinosa": ("Gryffindor", "mesa_8"),
    "Jose Antonio Espinosa": ("Gryffindor", "mesa_8"),
    "Cristina Cabello": ("Hufflepuff", "mesa_8"),
    "Jose Sánchez": ("Muggle", "mesa_8"),
    "Jose Antonio Sánchez": ("Gryffindor", "mesa_8"),
    "Marta Sánchez": ("Hufflepuff", "mesa_8"),
    "David": ("Muggle", "mesa_8"),
    "Álvaro Taboada": ("Slytherin", "mesa_9"),
    "Lucía Fernández": ("Hufflepuff", "mesa_9"),
    "Esteban Fernández": ("Slytherin", "mesa_9"),
    "Jorge Zapata": ("Ravenclaw", "mesa_9"),
    "Celia Hernández": ("Ravenclaw", "mesa_9"),
    "Julián Fernández": ("Hufflepuff", "mesa_9"),
    "Miguel Córdoba": ("Hufflepuff", "mesa_9"),
    
    "Belén": ("Hufflepuff", "mesa_9"), #--------------|
    "Belén vázquez": ("Hufflepuff", "mesa_9"),# belen gazquez
    
    "Patricio Martinez": ("Muggle", "mesa_9"),
    "Pablo Lozano": ("Hufflepuff", "mesa_9"),
    "Raúl Romero": ("Hufflepuff", "mesa_10"),
    "Marta Rodriguez": ("Gryffindor", "mesa_10"),
    "Alexander Vas": ("Gryffindor", "mesa_10"),
    "Sandra Navarro": ("Muggle", "mesa_10"),
    "Ricardo Cañuelo": ("Muggle", "mesa_10"),
    "Marina Muñoz": ("Gryffindor", "mesa_10"),
    
    "Beni": ("Gryffindor", "mesa_10"), #--------------|
    "Benny": ("Gryffindor", "mesa_10") # beni hay que pasarlo a benny
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
            message = f"{command}\n" 
            ser_port.write(message.encode()) 
            logging.debug(f"Enviado a Arduino: {message.strip()}") 
            if command == '1':
                print("Servo: MOVING")
            elif command == '0':
                print("Servo: STOPPED")
            time.sleep(0.02) 
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
                print(f"[ARDUINO]: {feedback}") 
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
        if ser_port:
            if not send_servo_command(ser_port, '1'):
                logging.warning("No se pudo iniciar el movimiento del servo antes de reproducir el audio.")
        
        # 2. Cargar y reproducir el audio
        pygame.mixer.music.load(full_path)
        pygame.mixer.music.play()
        logging.info(f"Reproduciendo audio: {full_path}")
        print(f"Reproduciendo: {full_path}")
        

        while pygame.mixer.music.get_busy():
            read_arduino_feedback(ser_port) 
            time.sleep(0.1) 
        
        logging.info(f"Audio '{full_path}' terminado.")
        print(f"Audio '{full_path}' terminado.")
        
        if ser_port:
            if not send_servo_command(ser_port, '0'):
                logging.warning("No se pudo detener el servo después de reproducir el audio.")
                
        return True
    
    except Exception as e:
        logging.error(f"Error durante la reproducción de audio y control del servo para '{full_path}': {e}", exc_info=True)
        print(f"Error al reproducir '{full_path}': {e}")
        if ser_port:
            send_servo_command(ser_port, '0')
        return False

def speak_text(text):
    """Sintetiza texto a voz."""
    engine.say(text)
    engine.runAndWait()

def play_sound_effect(file_path):
    """Reproduce un efecto de sonido sin controlar el servo (no bloqueante)."""
    full_path = os.path.join(script_dir, file_path)

    if not os.path.exists(full_path):
        logging.warning(f"Efecto de sonido no encontrado: {full_path}")
        print(f"Advertencia: El efecto de sonido '{full_path}' no existe.")
        return False
    try:
        sound = pygame.mixer.Sound(full_path) 
        sound.play()
        logging.debug(f"Reproduciendo efecto: {full_path}")
        return True
    except Exception as e:
        logging.error(f"Error al reproducir efecto de sonido '{full_path}': {e}", exc_info=True)
        print(f"Error al reproducir efecto de sonido: {e}")
        return False

# --- Bucle principal del programa ---
if __name__ == "__main__":
    if not init_pygame_mixer():
        print("No se pudo iniciar el sistema de audio. Saliendo.")
        exit()

    # 2. Abrir Puerto Serial de Arduino
    arduino = open_serial_port(ARDUINO_PORT, BAUD_RATE)
    
    if arduino:
        send_servo_command(arduino, '0')
        time.sleep(0.5) # Pequeña pausa para que el servo se asiente


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
                        # play_sound_effect(os.path.join('voice', 'fx', 'bell.mp3')) no sabemos que es
                        activacion_exitosa = True
                    else:
                        print("❌ Frase incorrecta. Intente de nuevo.")
                except sr.UnknownValueError:
                    print("❌ No entendí lo que dijiste. Intente de nuevo.")
                except sr.RequestError as e:
                    print(f"❌ Error al conectar con el servicio de voz de Google; {e}")
                    logging.error(f"Error de conexión con Google Speech Recognition: {e}")
                
                time.sleep(1) # Pausa para no saturar el bucle

        print("\n¡Bienvenido al Sombrero Seleccionador!")
        logging.info("Iniciando secuencia del Sombrero Seleccionador.")

        print("Reproduciendo audio de bienvenida...")
        play_audio_and_control_servo(os.path.join('voice', 'welcome', 'sombreo_inicio.mp3'), arduino, servo_home_angle_concept=0) 

        try:
            intentos = 0
            max_intentos = 3 
            while True:
                if not pygame.mixer.music.get_busy(): 
                    read_arduino_feedback(arduino)

                with mic as source:
                    print("\n🎤 Di tu nombre:")
                    recognizer.adjust_for_ambient_noise(source)
                    try: 
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    except sr.WaitTimeoutError:
                        print("No se detectó voz. Reintentando...")
                        intentos += 1
                        if intentos >= max_intentos:
                            logging.warning("Máximo de intentos de escucha alcanzado. Saliendo.")
                            break 
                        

                        error_audio_path = os.path.join('voice', 'error', f'sombreo_error_{intentos}.mp3')
                        print(f"Reproduciendo audio de error: {error_audio_path}")
                        if not play_audio_and_control_servo(error_audio_path, arduino, servo_home_angle_concept=0):
                             print(f"⚠️ Error al reproducir audio de error y controlar el servo.")
                        
                        continue 

                    try:
                        nombre = recognizer.recognize_google(audio, language="es-ES")
                        print(f"👂 Escuché: {nombre}")
                        nombre_formateado = nombre.title() 

                        if nombre_formateado in nombres_y_mesas:
                            # --- Lógica para nombres específicos (Silvia y Jorge) ---
                            if nombre_formateado == "Silvia Martín":
                                print("Reproduciendo audio de Silvia")
                                if not play_audio_and_control_servo(os.path.join('voice', 'SilviaJorge', 'Silvia_final.mp3'), arduino, servo_home_angle_concept=0):
                                    print(f"⚠️ Error al reproducir audio de Silvia y controlar el servo.")
                                time.sleep(1) 
                                if not play_audio_and_control_servo(os.path.join('voice', 'table', 'mesa_13.mp3'), arduino, servo_home_angle_concept=0):
                                    print(f"⚠️ Error al reproducir audio de MESA_1 y controlar el servo.")
                            elif nombre_formateado == "Jorge Gardón":
                                print("Reproduciendo audio de Jorge")
                                if not play_audio_and_control_servo(os.path.join('voice', 'SilviaJorge', 'Jorge_final.mp3'), arduino, servo_home_angle_concept=0):
                                    print(f"⚠️ Error al reproducir audio de Jorge y controlar el servo.")
                                time.sleep(1) 
                                if not play_audio_and_control_servo(os.path.join('voice', 'table', 'mesa_13.mp3'), arduino, servo_home_angle_concept=0):
                                    print(f"⚠️ Error al reproducir audio de mesa_2 y controlar el servo.")
                            else:
                                casa, mesa = nombres_y_mesas[nombre_formateado]
                                print(f"✔️ Nombre reconocido: {nombre_formateado}, Casa: {casa}, Mesa: {mesa}")
                                logging.info(f"Nombre reconocido: {nombre_formateado}, Casa: {casa}, Mesa: {mesa}")


                                audio_casa_path = os.path.join('voice', 'house', f"{casa}_audio.mp3") 
                                if not play_audio_and_control_servo(audio_casa_path, arduino, servo_home_angle_concept=0):
                                    print(f"⚠️ Error al reproducir audio de casa: {audio_casa_path}. Posible desincronización del servo.")

                                time.sleep(0.5) 

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
                            
                            # --- MODIFICACIÓN: Reproducir audio de error secuencial ---
                            error_audio_path = os.path.join('voice', 'error', f'sombreo_error_{intentos}.mp3')
                            print(f"Reproduciendo audio de error: {error_audio_path}")
                            if not play_audio_and_control_servo(error_audio_path, arduino, servo_home_angle_concept=0):
                                print(f"⚠️ Error al reproducir audio de error y controlar el servo.")

                            if intentos >= max_intentos:
                                logging.warning("Máximo de intentos de nombre no encontrado alcanzado. Saliendo.")
                                break # Salir del bucle interno

                    except sr.UnknownValueError:
                        intentos += 1
                        print(f"❌ No entendí lo que dijiste. Intento {intentos}/{max_intentos}")
                        logging.info(f"No se detectó entendimiento. Intento {intentos}/{max_intentos}")
                        
                        # --- MODIFICACIÓN: Reproducir audio de error secuencial ---
                        error_audio_path = os.path.join('voice', 'error', f'sombreo_error_{intentos}.mp3')
                        print(f"Reproduciendo audio de error: {error_audio_path}")
                        if not play_audio_and_control_servo(error_audio_path, arduino, servo_home_angle_concept=0):
                            print(f"⚠️ Error al reproducir audio de error y controlar el servo.")

                        if intentos >= max_intentos:
                            logging.warning("Máximo de intentos de no entendimiento alcanzado. Saliendo.")
                            break # Salir del bucle interno

                    except sr.RequestError as e:
                        logging.error(f"Error al solicitar resultados del servicio de reconocimiento de voz de Google; {e}", exc_info=True)
                        print(f"❌ Error al conectar con el servicio de voz de Google; {e}")
                        time.sleep(2) 
        
        except KeyboardInterrupt:
            print("\nPrograma interrumpido por el usuario (Ctrl+C).")
            logging.info("Programa interrumpido por usuario.")
            break 

        except Exception as e:
            logging.critical(f"Error inesperado en el bucle principal de reconocimiento: {e}", exc_info=True)
            print(f"Error inesperado: {e}")
            break 
    
    # --- PROCESO DE LIMPIEZA FINAL ---
    logging.info("Iniciando proceso de limpieza final.")
    if arduino:
        print("Enviando comando de parada a Arduino...")
        send_servo_command(arduino, '0') # Comando final para detener el servo
        time.sleep(0.5)
        close_serial_port(arduino)
    pygame.mixer.quit()
    logging.info("Pygame mixer apagado.")
    print("Pygame mixer apagado.")
    print("Programa finalizado.")
