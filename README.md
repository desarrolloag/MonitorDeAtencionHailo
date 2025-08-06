# Sistema de Analítica de Atención en Vitrinas 

Este proyecto utiliza una Raspberry Pi 5 y un acelerador de IA Hailo para medir la atención de las personas hacia una vitrina o exhibición de productos. Cuando el sistema detecta una **"atención cualificada"** (una persona mira fijamente por un tiempo), registra un "impacto visual" y toma una fotografía como evidencia.

![Demostración del control por gestos](https://github.com/desarrolloag/MonitorDeAtencionHailo/blob/main/AIHAT+.jpeg?raw=true)

## Índice

  * [Requisitos de Hardware](#-requisitos-de-hardware-️)
  * [Configuración del Software](#-Configuración-del-Software-️)
  * [Estructura del Repositorio](#-estructura-del-repositorio-️)
  * [Uso y Calibración del Programa](#-uso-y-calibración-del-programa-️)
  * [Autoinicio del Sistema](#-autoinicio-del-sistema-️)
  * [Solución de Problemas](#-solución-de-problemas-️)

-----

### 🤔 **Requisitos de Hardware** ▶️

Para montar este proyecto, necesitarás los siguientes componentes:

  * **Procesamiento:**
      * **Raspberry Pi 5**
      * **Raspberry Pi AI HAT+** con acelerador Hailo-8 AI.
  * **Periféricos:**
      * Cámara USB compatible con Raspberry Pi.
      * Tarjeta MicroSD de 16 GB o más.
      * **Batería RTC oficial de Raspberry Pi 5** (recomendado para mantener la hora sin energía).
  * **Fuente de alimentación:**
      * Fuente de alimentación USB-C para la Raspberry Pi 5 (5V, 5A).

-----

### 🤔 **Configuración del Software** ▶️

Sigue estos pasos para preparar tu Raspberry Pi. Se asume que los drivers del AI HAT+ de Hailo ya están instalados.

#### **Paso 1: Clonar el Repositorio**

Abre una terminal y clona este repositorio:

```bash
git clone https://github.com/TU_USUARIO/MonitorDeAtencionHailo.git
cd MonitorDeAtencionHailo
```

*(Recuerda cambiar la URL por la de tu propio repositorio)*

#### **Paso 2: Instalar Dependencias** 

El proyecto necesita varias librerías de Python. La mejor práctica es usar un entorno virtual.

1.  Crea y activa un entorno virtual (si no lo has hecho ya):
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
2.  Instala todas las dependencias del proyecto:
    ```bash
    pip install -r requirements.txt
    ```

-----

### 🤔 **Estructura del Repositorio** ▶️

  * **`MedidorAtencion3.py`**: El script principal de Python que ejecuta la lógica del proyecto.
  * **`lanzar_medidor.sh`**: Script de lanzamiento que activa el entorno virtual y ejecuta el programa.
  * **`medidor_atencion.service`**: Archivo de configuración de `systemd` para el inicio automático.
  * **`requirements.txt`**: Lista de librerías de Python necesarias.
  * **`evidencia/`**: Carpeta donde se guardan las fotos de los impactos.
  * **`registro_impactos.xlsx`**: Archivo de Excel con los registros de atención.

-----

### 🤔 **Uso y Calibración del Programa** ▶️

Antes de ejecutar, abre el archivo `MedidorAtencion3.py` y ajusta los parámetros que se encuentran al inicio del script.

  * `AREA_INTERES`: Coordenadas para definir el **rectángulo azul (zona de interés)**.
  * `TIEMPO_ATENCION`: El **tiempo en segundos** que una persona debe mantener la atención para contar como un "impacto".
  * `TAMAÑO_MINIMO_PERSONA`: El **tamaño mínimo** de la persona para ser considerada.

-----

### 🤔 **Autoinicio del Sistema** ▶️

Para que el script inicie automáticamente al encender la Raspberry Pi, sigue estos pasos:

1.  Copia el archivo de servicio a la carpeta del sistema (este comando necesita permisos de administrador):
    ```bash
    sudo cp medidor_atencion.service /etc/systemd/system/
    ```
2.  Recarga el daemon y habilita el servicio:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable medidor_atencion.service
    ```
3.  Inicia el servicio por primera vez:
    ```bash
    sudo systemctl start medidor_atencion.service
    ```

Para detenerlo, usa el comando `sudo systemctl stop medidor_atencion.service`.

-----

### 🤔 **Solución de Problemas**

  * **El programa no inicia o se cierra:**
      * Revisa los logs con `journalctl -u medidor_atencion.service` para ver el error.
      * Asegúrate de que `Environment="DISPLAY=:0"` esté en el archivo de servicio.
  * **"Camera not found" o pantalla negra:**
      * Verifica que la cámara USB esté bien conectada.
      * Usa `lsusb` en la terminal para confirmar que la cámara sea detectada.
  * **Bajo rendimiento (video lento):**
      * Asegúrate de que el **AI HAT+ esté conectado firmemente** y que los drivers de Hailo estén activos.
