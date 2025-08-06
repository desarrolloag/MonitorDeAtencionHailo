````markdown
# Sistema de Analítica de Atención en Vitrinas 🚀

Este proyecto utiliza una Raspberry Pi 5 y un acelerador AI Hailo para medir la atención de las personas hacia una vitrina o exhibición. Cuando el sistema detecta una **atención cualificada** (alguien mira fijamente por un tiempo), registra un **impacto visual** y toma una fotografía como evidencia.

<!-- Aquí puedes poner una foto o un GIF de tu proyecto en acción -->
![Demostración del proyecto](ruta/a/tu-imagen-o-gif.gif)

## Índice

1. [Hardware Requerido](#hardware-requerido-️)
2. [Configuración del Software](#⚙️-configuración-del-software)
3. [Estructura del Repositorio](#📂-estructura-del-repositorio)
4. [Uso y Calibración del Programa](#▶️-uso-y-calibración-del-programa)
5. [Autoinicio del Sistema](#🚀-autoinicio-del-sistema)
6. [Solución de Problemas](#🤔-solución-de-problemas)

---

## Hardware Requerido 🛠️

Para montar este proyecto, necesitarás los siguientes componentes:

### Procesamiento

- **Raspberry Pi 5**  
- **Raspberry Pi AI HAT+** con Hailo-8 AI Accelerator

### Periféricos

- Cámara USB genérica (compatible con Linux/UVC)  
- Tarjeta MicroSD de 16 GB o más (Clase 10)  
- Batería RTC oficial de Raspberry Pi 5 (recomendado para mantener la hora sin energía)

### Fuente de alimentación

- Fuente de alimentación USB-C para la Raspberry Pi 5 (5 V, 5 A)

---

## ⚙️ Configuración del Software

Sigue estos pasos para preparar tu Raspberry Pi desde cero. Asumimos que los drivers del AI HAT+ de Hailo ya están instalados.

### Paso 1: Clonar este Repositorio

```bash
git clone https://github.com/TU_USUARIO/MonitorDeAtencionHailo.git
cd MonitorDeAtencionHailo
````

> *Recuerda cambiar la URL por la de tu propio repositorio.*

### Paso 2: Instalar Dependencias

Es buena práctica crear un entorno virtual para mantener el proyecto ordenado.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📂 Estructura del Repositorio

* **MedidorAtencion3.py**
  El script principal de Python que ejecuta toda la lógica de detección.
* **lanzar\_medidor.sh**
  Script de lanzamiento que activa el entorno virtual y ejecuta el programa.
* **medidor\_atencion.service**
  Archivo de configuración de systemd para el inicio automático.
* **requirements.txt**
  Lista de librerías de Python necesarias para el proyecto.
* **registro\_impactos.xlsx**
  Archivo de Excel donde se guardan los registros de atención.
* **evidencia/**
  Carpeta donde se guardan las fotos de los impactos.
* **README.md**
  Este mismo archivo de instrucciones.

---

## ▶️ Uso y Calibración del Programa

Antes de ejecutar, abre `MedidorAtencion3.py` con un editor de texto (por ejemplo, `nano`) y ajusta los parámetros al inicio:

* `AREA_INTERES`: Coordenadas para definir el rectángulo azul (zona de interés).
* `TIEMPO_ATENCION`: Tiempo en segundos que una persona debe mantener la atención para que cuente como un “impacto”.
* `TAMAÑO_MINIMO_PERSONA`: Tamaño mínimo de la persona para ser considerada. Aumenta este valor si quieres filtrar personas lejanas.

---

## 🚀 Autoinicio del Sistema

Para que el script inicie automáticamente al encender la Raspberry Pi, usamos un servicio de systemd:

1. Copia el archivo del servicio:

   ```bash
   sudo cp medidor_atencion.service /etc/systemd/system/
   ```
2. Recarga el daemon y habilita el servicio:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable medidor_atencion.service
   ```
3. Inicia el servicio para probarlo:

   ```bash
   sudo systemctl start medidor_atencion.service
   ```
4. Para detenerlo:

   ```bash
   sudo systemctl stop medidor_atencion.service
   ```

---

## 🤔 Solución de Problemas

* **El programa no inicia o se cierra inmediatamente:**

  * Ejecuta `journalctl -u medidor_atencion.service` y revisa los logs.
  * Asegúrate de que `Environment="DISPLAY=:0"` esté presente en `medidor_atencion.service`.

* **“Camera not found” o pantalla en negro:**

  * Verifica la conexión USB de la cámara.
  * Ejecuta `lsusb` para comprobar que el sistema detecta la cámara.

* **Bajo rendimiento (video lento):**

  * Revisa que el AI HAT+ esté bien conectado.
  * Confirma que los drivers de Hailo están cargados correctamente.

---

© 2025 Tu Nombre o Tu Organización.

```
```
