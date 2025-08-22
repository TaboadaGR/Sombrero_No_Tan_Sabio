import pygame
import logging
import os
import time

from .serialHat import send_servo_command,read_arduino_feedback

logger = logging.getLogger("main_logger")

def init_pygame_mixer():
    """Inicializa el mezclador de Pygame."""
    try:
        pygame.mixer.init()
        logger.info("Pygame mixer inicializado.")
        return True
    except Exception as e:
        logger.error(f"Error al inicializar Pygame mixer: {e}", exc_info=True)
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
    if not os.path.exists(file_path):
        logger.error(f"Archivo de audio no encontrado: {file_path}")
        print(f"Error: El archivo de audio '{file_path}' no existe.")
        return False

    try:
        # 1. Enviar comando para INICIAR el movimiento aleatorio en Arduino
        # El Arduino moverá los servos a su HOME_ANGLE interno y luego iniciará el movimiento aleatorio.
        if ser_port:
            if not send_servo_command(ser_port, '1'):
                logger.warning("No se pudo iniciar el movimiento del servo antes de reproducir el audio.")
        
        # 2. Cargar y reproducir el audio
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        logger.info(f"Reproduciendo audio: {file_path}")
        print(f"Reproduciendo: {file_path}")
        
        # 3. Esperar a que el audio termine y leer feedback de Arduino
        while pygame.mixer.music.get_busy():
            read_arduino_feedback(ser_port) # <-- Leer feedback mientras el audio suena
            time.sleep(0.1) # Pequeña pausa para no consumir mucha CPU
        
        logger.info(f"Audio '{file_path}' terminado.")
        print(f"Audio '{file_path}' terminado.")
        
        # 4. Enviar comando para DETENER el movimiento aleatorio en Arduino
        # El Arduino regresará los servos a su HOME_ANGLE interno.
        if ser_port:
            if not send_servo_command(ser_port, '0'):
                logger.warning("No se pudo detener el servo después de reproducir el audio.")
                
        return True # Audio reproducido y servo controlado con éxito
    
    except Exception as e:
        logger.error(f"Error durante la reproducción de audio y control del servo para '{file_path}': {e}", exc_info=True)
        # print(f"Error al reproducir '{file_path}': {e}")
        # Si ocurre un error, asegúrate de enviar el comando de detener al servo
        if ser_port:
            send_servo_command(ser_port, '0')
        return False

def speak_text(text,engine):
    """Sintetiza texto a voz."""
    engine.say(text)
    engine.runAndWait()

def play_sound_effect(file_path):
    """Reproduce un efecto de sonido sin controlar el servo (no bloqueante)."""
    if not os.path.exists(file_path):
        logger.warning(f"Efecto de sonido no encontrado: {file_path}")
        print(f"Advertencia: El efecto de sonido '{file_path}' no existe.")
        return False
    try:
        sound = pygame.mixer.Sound(file_path) # Usar Sound para efectos cortos
        sound.play()
        logger.debug(f"Reproduciendo efecto: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error al reproducir efecto de sonido '{file_path}': {e}", exc_info=True)
        print(f"Error al reproducir efecto de sonido: {e}")
        return False
