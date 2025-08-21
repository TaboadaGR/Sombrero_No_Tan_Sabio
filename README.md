# Sombrero_No_Tan_Sabio
Sombrero seleccionador by Álvaro and Pablo

Proyecto paso a paso 
-------------------------

Puntos Clave del Proyecto del Sombrero Seleccionador
A continuación, se detallan los elementos críticos que deben cumplirse para que la interacción entre el código de Python y el hardware de Arduino funcione sin problemas.
1. Hardware y Conexión Física
Arduino: Asegúrate de que el Arduino esté correctamente conectado a tu ordenador mediante un cable USB. La conexión debe ser estable.
Servos: Los servos deben estar conectados al Arduino y alimentados por una fuente de poder externa si es necesario, ya que el USB del ordenador podría no ser suficiente para moverlos. Confirma que los cables estén en los pines correctos según el código de Arduino.
Micrófono y Altavoces: Asegúrate de que el micrófono esté correctamente configurado como dispositivo de entrada predeterminado en tu sistema operativo y que los altavoces estén configurados como dispositivo de salida predeterminado y con el volumen alto.
2. Código de Arduino (en el Canvas)
Puerto Serial: El código de Arduino debe estar cargado y ejecutándose en la placa. Su única función es escuchar comandos en el puerto serial.
Comandos:
Cuando recibe un '1', debe iniciar un movimiento aleatorio en los servos.
Cuando recibe un '0', debe detener el movimiento y devolver los servos a su posición inicial (normalmente 0 grados).
Depuración: El código de Arduino debe tener la función de enviar mensajes de vuelta al PC (por ejemplo, "Servo MOVING") para que el script de Python pueda mostrarlos y puedas verificar que la comunicación funciona en ambos sentidos.
3. Script de Python (en el Canvas)
Puerto Serial (ARDUINO_PORT): Este es el punto más importante. En la línea ARDUINO_PORT = 'COM4', debes cambiar 'COM4' por el puerto serial al que esté conectado tu Arduino. Puedes encontrar esta información en el IDE de Arduino en Herramientas > Puerto.
Bibliotecas de Python: Debes tener instaladas todas las bibliotecas necesarias. Si no lo has hecho, abre tu terminal y ejecuta estos comandos:

pip install pyserial
pip install SpeechRecognition
pip install PyAudio
pip install pygame
pip install pyttsx3

Si tienes problemas con PyAudio en Windows, a veces es necesario instalarlo con pipwin: pip install pipwin y luego pipwin install pyaudio.
Nombres y Mesas: La lista nombres_y_mesas debe contener exactamente los nombres que esperas que el micrófono reconozca. El reconocimiento de voz puede ser sensible, así que los nombres deben coincidir lo mejor posible con la pronunciación.
Archivos de Audio: Todos los archivos de audio (.mp3) deben estar en la misma carpeta que el script de Python. Los nombres deben coincidir exactamente con los que se definen en el script (por ejemplo, Gryffindor_audio.mp3, mesa_1.mp3, etc.). Si algún archivo falta, el script mostrará un error.

4. Flujo de Funcionamiento
El script de Python se inicia y abre la conexión con Arduino.
Reproduce el audio de bienvenida (sombrero_inicio_1.mp3) y, durante la reproducción, envía el comando '1' al Arduino para que los servos comiencen a moverse.
Cuando el audio termina, envía el comando '0' para que los servos se detengan.
El script se pone a la escucha de un nombre a través del micrófono.
Cuando reconoce un nombre de la lista, reproduce el audio de la casa (Casa_audio.mp3) y de la mesa (mesa_X.mp3). Durante estas reproducciones, vuelve a enviar el comando '1' para mover los servos, y luego un '0' para detenerlos.
Si no reconoce el nombre, reproduce un audio de error y vuelve a intentarlo.
Si has verificado todos estos puntos y el problema persiste, es muy probable que el problema esté en la comunicación serial o en el reconocimiento de voz.
