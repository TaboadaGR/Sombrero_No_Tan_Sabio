# Sombrero_No_Tan_Sabio
Sombrero seleccionador by Álvaro and Pablo

Proyecto paso a paso 
-------------------------

## Como lanzar el ejecutable

- Acceder por ssh a la Raspberry con el usuario *dietpi* y la contraseña adecuada
- Entrar en /home/dietpi/workbench/Sombrero_No_Tan_Sabio
```
cd /home/dietpi/workbench/Sombrero_No_Tan_Sabio
```
- Activar el entorno virtual
```
source .venv/bin/activate
```
- Lanzar el script *main.py* con el argumento *fake* si queremos lanzar el loop de
prueba de servicio, o bien con el argumento *start* para que comienze el bucle real
```
python code/python/main.py fake
python code/python/main.py start
```

## Como lanzar el servicio

Existen dos servicios automáticos programados para systemd en la Raspberry:
**animatronic** y **animatronic-fake**. El primer servicio lanza el script *main.py* con
el argumento *start*, mientras que el segundo lanza el script con el servicio de loop
de prueba.

Podemos trabajar con los servicios usando el terminal desde el usuario *root* o desde
el usuario *dietpi* usando el comando *sudo*:

- **Lanzar un servicio**: systemctl start "nombre-del-servicio"
```
systemctl start animatronic
systemctl start animatronic-fake
```
- **Detener un servicio**: systemctl stop "nombre-del-servicio"
```
systemctl stop animatronic
systemctl stop animatronic-fake
```
- **Activar un servicio al inicio**: systemctl enable "nombre-del-servicio"
```
systemctl enable animatronic
systemctl enable animatronic-fake
```
- **Desactivar un servicio al inicio**: systemctl disable "nombre-del-servicio"
```
systemctl disable animatronic
systemctl disable animatronic-fake
```
- **Comprobar el estado del servicio**: systemctl status "nombre-del-servicio"
```
systemctl status animatronic
systemctl status animatronic-fake
```

Ambos servicios escriben en el mismo archivo de log.

## Archivo de configuracion

El archivo de configuracion es **configuration.yaml**, contiene la información de configuración para el script.
Si queremos cambiar alguno de los parámetros, sólo tenemos que entrar y cambiar la configuración allí, para luego
recargar el servicio o lanzar el script:

```yaml
names_file: /home/dietpi/workbench/Sombrero_No_Tan_Sabio/code/python/nombres_y_mesas.json
log_file: /home/dietpi/Desktop/log_sombrero_seleccionador.txt
arduino:
  port: COM4
  baud_rate: 9600
pyttsx3:
  rate: 180
  volume: 0.9
```

## Archivo de mesas

Los nombres y las localizaciones de los usuarios están en el archivo *log_file*, situado en 
*/home/dietpi/workbench/Sombrero_No_Tan_Sabio/code/python/nombres_y_mesas.json*. El formato es el siguiente:

```json
{
    "nombres_y_mesas": [
        {
            "nombre":"Invitado 1",
            "casa":"Gryffindor",
            "mesa": "mesa_1"
        },
        {
            "nombre":"Invitado 2",
            "casa": "Slytherin",
            "mesa": "mesa_2"
        }
    ]
}
```

El script principal leerá el archivo y convertirá el formato al que espera recibir el script.
