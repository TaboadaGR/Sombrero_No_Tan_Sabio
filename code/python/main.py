import time
import datetime
import pygame
import speech_recognition as sr
import pyttsx3
import logging
import os
import simplejson as json
from omegaconf import OmegaConf,DictConfig

from animatronic.serialHat import *
from animatronic.audioHat import *
from animatronic.auxiliarHat import *

import typer

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

configuration = OmegaConf.load(os.path.join(CURRENT_PATH,'configuration.yaml'))

# --- Configuración del Log ---
log_file =configuration.get('log_file')

log_handlers = [logging.FileHandler(log_file),logging.StreamHandler()]
log_level = logging.INFO
log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=log_level, # Nivel de log por defecto (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    format=log_format,
    handlers=log_handlers
)

logger = logging.getLogger('main_logger')

# --- Configuración del Sintetizador de Voz (pyttsx3) ---
engine = pyttsx3.init()
engine.setProperty('rate', configuration.get('pyttsx3',{}).get('rate','180')) # Velocidad de la voz (ajusta entre 150-250 para voz natural)
engine.setProperty('volume', configuration.get('pyttsx3',{}).get('volume','0.9')) # Volumen (0.0 a 1.0)

# --- Configuración del Puerto Serial de Arduino ---
ARDUINO_PORT = configuration.get('arduino',{}).get('port','COM4') # <--- ¡CAMBIA ESTO A TU PUERTO ARDUINO REAL!
BAUD_RATE = int(configuration.get('arduino',{}).get('baud_rate','9600'))

arduino = None # Variable global para la conexión serial

# --- Configuración de Nombres y Mesas ---


nombres_y_mesas = None

with open(configuration.get('names_file','nombres_y_mesas.json'),'r') as istream:
    nombres_y_mesas = raw_names_to_expected_format(json.load(istream))

logger.info(f'Expected names: {nombres_y_mesas}')

# --- Inicialización del Reconocimiento de Voz ---
try:
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
except Exception as e:
    logger.error(f'ERROR configurando recognizer or mic: {e}')
    recognizer = None
    mic = None

intentos = 0
max_intentos = 3 # Número máximo de intentos antes de salir

app = typer.Typer()

@app.command()
def fake():
    while True:
        logger.info(f'Actualiza el servicio...{datetime.datetime.now()}')
        time.sleep(10)


@app.command()
def start():
    if (mic is None) or( recognizer is None):
        logger.critical('No se pudo ')
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

    print("\n¡Bienvenido al Sombrero Seleccionador!")
    logger.info("Iniciando secuencia del Sombrero Seleccionador.")

    # Reproduce el audio de inicio y controla el servo automáticamente
    print("Reproduciendo audio de bienvenida...")
    # Aquí se pasa el concepto de home_angle (aunque Arduino usa su propio valor)
    play_audio_and_control_servo('sombreo_inicio_1.mp3', arduino, servo_home_angle_concept=0) 
    
    try:
        while True:
            # Leer feedback de Arduino continuamente en el bucle principal
            # NOTA: Esto puede ser redundante si read_arduino_feedback ya se llama en play_audio_and_control_servo
            # y no hay comandos de voz activos. Se mantiene para capturar mensajes fuera de la reproducción de audio.
            if not pygame.mixer.music.get_busy(): # Solo leer si no hay audio sonando (para evitar conflicto con el loop de audio)
                read_arduino_feedback(arduino)

            with mic as source:
                print("🎤 Di tu nombre:")
                recognizer.adjust_for_ambient_noise(source)
                try: # Añadido timeout para evitar esperas infinitas si no hay voz
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                except sr.WaitTimeoutError:
                    print("No se detectó voz. Reintentando...")
                    intentos += 1
                    if intentos >= max_intentos:
                         
                        logger.warning("Máximo de intentos de escucha alcanzado. Saliendo.")
                        break # Salir del bucle principal
                    continue # Volver a intentar escuchar

            try:
                nombre = recognizer.recognize_google(audio, language="es-ES")
                print(f"👂 Escuché: {nombre}")
                nombre_formateado = nombre.title() # Pone la primera letra de cada palabra en mayúscula

                if nombre_formateado in nombres_y_mesas:
                    # --- Lógica para nombres específicos (Silvia y Jorge) ---
                    if nombre_formateado == "Silvia Martín Díaz":
                        print("Reproduciendo audio de Silvia")
                        # Reproduce el audio de Silvia y controla el servo
                        if not play_audio_and_control_servo("silvia.mp3", arduino, servo_home_angle_concept=0):
                            print(f"⚠️ Error al reproducir audio de Silvia y controlar el servo.")
                        time.sleep(1) # Pausa entre audios
                        # Reproduce el audio de la mesa de Silvia y controla el servo
                        if not play_audio_and_control_servo("MESA_1.mp3", arduino, servo_home_angle_concept=0):
                            print(f"⚠️ Error al reproducir audio de MESA_1 y controlar el servo.")
                    elif nombre_formateado == "Jorge Lozano Lozano":
                        print("Reproduciendo audio de Jorge")
                        # Reproduce el audio de Jorge y controla el servo
                        if not play_audio_and_control_servo("jorge.mp3", arduino, servo_home_angle_concept=0):
                            print(f"⚠️ Error al reproducir audio de Jorge y controlar el servo.")
                        time.sleep(1) # Pausa entre audios
                        # Reproduce el audio de la mesa de Jorge y controla el servo
                        if not play_audio_and_control_servo("mesa_2.mp3", arduino, servo_home_angle_concept=0):
                            print(f"⚠️ Error al reproducir audio de mesa_2 y controlar el servo.")
                    # --- Lógica general para otras casas/mesas ---
                    else:
                        casa, mesa = nombres_y_mesas[nombre_formateado]
                        print(f"✔️ Nombre reconocido: {nombre_formateado}, Casa: {casa}, Mesa: {mesa}")
                        logger.info(f"Nombre reconocido: {nombre_formateado}, Casa: {casa}, Mesa: {mesa}")

                        # Reproduce el audio de la casa y controla el servo
                        audio_casa_path = f"{casa}_audio.mp3" 
                        if not play_audio_and_control_servo(audio_casa_path, arduino, servo_home_angle_concept=0):
                            print(f"⚠️ Error al reproducir audio de casa: {audio_casa_path}. Posible desincronización del servo.")

                        time.sleep(0.5) # Pequeña pausa entre audios si lo necesitas

                        # Reproduce el audio de la mesa y controla el servo
                        audio_mesa_path = f"{mesa}.mp3"
                        if not play_audio_and_control_servo(audio_mesa_path, arduino, servo_home_angle_concept=0):
                            print(f"⚠️ Error al reproducir audio de mesa: {audio_mesa_path}. Posible desincronización del servo.")
                    
                    logger.info("Secuencia de casa/mesa completada.")
                    break # Salir del bucle principal después de una asignación exitosa

                else:
                    intentos += 1
                    print(f"❌ Nombre no encontrado. Intento {intentos}/{max_intentos}")
                    logger.info(f"Nombre no encontrado: {nombre}. Intento {intentos}/{max_intentos}")
                    
                    # Se llama a play_audio_and_control_servo para mover el servo
                    if not play_audio_and_control_servo('sombreo_inicio_error.mp3', arduino, servo_home_angle_concept=0):
                        print(f"⚠️ Error al reproducir audio de error y controlar el servo.")

                    if intentos >= max_intentos:
                         
                        logger.warning("Máximo de intentos de nombre no encontrado alcanzado. Saliendo.")
                        break # Salir del bucle principal

            except sr.UnknownValueError:
                intentos += 1
                print(f"❌ No entendí lo que dijiste. Intento {intentos}/{max_intentos}")
                logger.info(f"No se detectó entendimiento. Intento {intentos}/{max_intentos}")
                
                # Se llama a play_audio_and_control_servo para mover el servo
                if not play_audio_and_control_servo('sombreo_inicio_error.mp3', arduino, servo_home_angle_concept=0):
                    print(f"⚠️ Error al reproducir audio de error y controlar el servo.")

                if intentos >= max_intentos:
                     
                    logger.warning("Máximo de intentos de no entendimiento alcanzado. Saliendo.")
                    break # Salir del bucle principal

            except sr.RequestError as e:
                logger.error(f"Error al solicitar resultados del servicio de reconocimiento de voz de Google; {e}", exc_info=True)
                print(f"❌ Error al conectar con el servicio de voz de Google; {e}")
                
                time.sleep(2) # Esperar un poco antes de reintentar
                # No incrementamos intentos por problemas de red

            except Exception as e:
                logger.critical(f"Error inesperado en el bucle principal de reconocimiento: {e}", exc_info=True)
                print(f"Error inesperado: {e}")
                break # Salir ante cualquier otro error crítico
    
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario (Ctrl+C).")
        logger.info("Programa interrumpido por usuario.")
    except Exception as e:
        logger.critical(f"Error general en el programa: {e}", exc_info=True)
        print(f"Error general inesperado: {e}")
    finally:
        logger.info("Iniciando proceso de limpieza final.")
        # Asegurarse de detener servo y audio al finalizar o salir
        if arduino:
            send_servo_command(arduino, '0') # Comando final para detener el servo
            close_serial_port(arduino)
        pygame.mixer.quit() # Apagar el mezclador de Pygame
        logger.info("Pygame mixer apagado.")
        print("Pygame mixer apagado.")
        print("Programa finalizado.")
    
# --- Bucle principal del programa ---
if __name__ == "__main__":
    app()
