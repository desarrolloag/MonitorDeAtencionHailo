# Sistema de Analítica de Atención en Vitrinas 🤖️

Este proyecto utiliza una Raspberry Pi 5 y un acelerador de IA Hailo para medir la atención de las personas hacia una vitrina o exhibición de productos. Cuando el sistema detecta una **"atención cualificada"** (una persona mira fijamente por un tiempo), registra un "impacto visual" y toma una fotografía como evidencia.

![placeholder](https://i.imgur.com/v2Jz7g6.png)
*(Aquí puedes poner una foto o un GIF de tu proyecto en acción)*

## Índice

* [Requisitos de Hardware](#-requisitos-de-hardware-️)
* [Configuración del Software](#-configuración-del-software)
* [Estructura del Repositorio](#-estructura-del-repositorio)
* [Uso y Calibración del Programa](#-uso-y-calibración-del-programa)
* [Autoinicio del Sistema](#-autoinicio-del-sistema)
* [Solución de Problemas](#-solución-de-problemas)

---

### 🛠️**Requisitos de Hardware** 🛠️

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

---

### **Configuración del Software** ⚙️

Sigue estos pasos en orden para preparar tu sistema y clonar el proyecto.

#### **Paso 0: Preparación del Sistema y Drivers**

1.  **Instalar Raspberry Pi OS:** Es fundamental usar la versión de 64 bits de Raspberry Pi OS Bookworm. Si partes de cero, instala el sistema operativo en tu tarjeta SD siguiendo la [guía oficial](https://www.raspberrypi.com/software/).
2.  **Configurar el AI HAT+:** Sigue las instrucciones oficiales para la instalación física y de software del **AI HAT+** en tu Raspberry Pi 5. Puedes encontrar la documentación detallada aquí:
    * [Instalación del AI HAT+ en Raspberry Pi](https://www.raspberrypi.com/documentation/accessories/ai-hat-plus.html)
    * [Información general sobre IA en Raspberry Pi](https://www.raspberrypi.com/documentation/computers/ai.html)
3.  **Instalar los Drivers de Hailo:** El AI HAT+ necesita sus drivers para funcionar correctamente. Este es un paso fundamental.

#### **Paso 1: Clonar Repositorios y Configurar el Entorno Virtual**

Tu proyecto está basado en el repositorio de ejemplos de Hailo. Es necesario clonar ambos repositorios y preparar un entorno virtual de Python.

1.  Abre una terminal y clona el repositorio base:
    ```bash
    git clone [https://github.com/DeGirum/hailo_examples.git](https://github.com/DeGirum/hailo_examples.git)
    cd hailo_examples
    ```
2.  Desde el mismo directorio, clona este repositorio:
    ```bash
    git clone [https://github.com/desarrolloag/MonitorDeAtencionHailo.git](https://github.com/desarrolloag/MonitorDeAtencionHailo.git)
    ```
3.  Crea y activa un entorno virtual para el proyecto:
    ```bash
    python3 -m venv venv_hailo
    source venv_hailo/bin/activate
    ```
4.  Instala las librerías de Python necesarias para el repositorio base:
    ```bash
    pip install -r requirements.txt
    ```

#### **Paso 2: Integrar el Proyecto y Ejecutar**

Ahora integraremos los archivos de tu proyecto y nos aseguraremos de que el código esté configurado para usar los modelos desde la nube de Hailo.

1.  Copia los archivos de tu proyecto al repositorio base, reemplazando los existentes:
    ```bash
    cp MonitorDeAtencionHailo/MedidorAtencion3.py .
    cp MonitorDeAtencionHailo/lanzar_medidor.sh .
    cp MonitorDeAtencionHailo/medidor_atencion.service .
    ```
2.  **Edita el script de lanzamiento:** Abre `lanzar_medidor.sh` y verifica que la línea `source venv_hailo/bin/activate` coincida con el nombre de tu entorno virtual.
3.  **Ejecuta el programa:**
    * Abre el archivo `MedidorAtencion3.py` y verifica que la línea `zoo_url = "degirum/hailo"` esté presente. Esto asegura que los modelos se descargarán automáticamente desde la nube si no los tienes localmente.
    * Ejecuta el script de lanzamiento para iniciar el sistema:
        ```bash
        bash lanzar_medidor.sh
        ```
    > **Nota:** Si tu proyecto usa un Jupyter Notebook (por ejemplo, si has modificado el `003_face_detection.ipynb`), asegúrate de haber instalado `jupyterlab` y de seguir los pasos de la sección de "Uso del programa" para modificar el nombre del modelo y ejecutar las celdas.

---

### **Estructura del Repositorio** 📂

* **`MedidorAtencion3.py`**: El script principal de Python que ejecuta la lógica del proyecto.
* **`lanzar_medidor.sh`**: Script de lanzamiento que activa el entorno virtual y ejecuta el programa.
* **`medidor_atencion.service`**: Archivo de configuración de `systemd` para el inicio automático.
* **`requirements.txt`**: Lista de librerías de Python necesarias.
* **`evidencia/`**: Carpeta donde se guardan las fotos de los impactos.
* **`registro_impactos.xlsx`**: Archivo de Excel con los registros de atención.

---

### **Uso y Calibración del Programa** ▶️

Antes de ejecutar, abre el archivo `MedidorAtencion3.py` y ajusta los parámetros que se encuentran al inicio del script.

* `AREA_INTERES`: Coordenadas para definir el **rectángulo azul (zona de interés)**.
* `TIEMPO_ATENCION`: El **tiempo en segundos** que una persona debe mantener la atención para contar como un "impacto".
* `TAMAÑO_MINIMO_PERSONA`: El **tamaño mínimo** de la persona para ser considerada.

---

### **Autoinicio del Sistema** 🚀

Para que el script inicie automáticamente al encender la Raspberry Pi, sigue estos pasos:

1.  **Edita el archivo de servicio:** Abre `medidor_atencion.service` y **modifica los siguientes campos** con tu información:
    * `WorkingDirectory`: Cambia `mi_usuario` por tu nombre de usuario y `hailo_examples` por la ruta correcta de tu proyecto.
    * `ExecStart`: Asegúrate de que la ruta del script `lanzar_medidor.sh` sea correcta.
    * `User`: Cambia `mi_usuario` por tu nombre de usuario de la Raspberry Pi.

2.  Copia el archivo de servicio a la carpeta del sistema (este comando necesita permisos de administrador):
    ```bash
    sudo cp medidor_atencion.service /etc/systemd/system/
    ```
3.  Recarga el daemon y habilita el servicio:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable medidor_atencion.service
    ```
4.  Inicia el servicio para probarlo:
    ```bash
    sudo systemctl start medidor_atencion.service
    ```
Para detenerlo, usa el comando `sudo systemctl stop medidor_atencion.service`.

---

### **Solución de Problemas** 🤔

* **El programa no inicia o se cierra:**
    * Revisa los logs con `journalctl -u medidor_atencion.service` para ver el error.
    * Asegúrate de que `Environment="DISPLAY=:0"` esté en el archivo de servicio.
* **"Camera not found" o pantalla negra:**
    * Verifica que la cámara USB esté bien conectada.
    * Usa `lsusb` en la terminal para confirmar que la cámara sea detectada.
* **Bajo rendimiento (video lento):**
    * Asegúrate de que el **AI HAT+ esté conectado firmemente** y que los drivers de Hailo estén activos.
* **Errores de `externally-managed-environment`:**
    * Este error se soluciona usando un **entorno virtual** de Python, como se explica en el **Paso 1**.
