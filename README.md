Sistema de Analítica de Atención en Vitrinas 🤖️
Este proyecto utiliza una Raspberry Pi 5 y un acelerador de IA Hailo para medir la atención de las personas hacia una vitrina o exhibición de productos. Cuando el sistema detecta una "atención cualificada" (una persona mira fijamente por un tiempo), registra un "impacto visual" y toma una fotografía como evidencia.

(Aquí puedes poner una foto o un GIF de tu proyecto en acción)

Índice
Requisitos de Hardware

Configuración del Software

Estructura del Repositorio

Uso y Calibración del Programa

Autoinicio del Sistema

Solución de Problemas

Requisitos de Hardware 🛠️
Para montar este proyecto, necesitarás los siguientes componentes:

Procesamiento:

Raspberry Pi 5

Raspberry Pi AI HAT+ con acelerador Hailo-8 AI.

Periféricos:

Cámara USB compatible con Raspberry Pi.

Tarjeta MicroSD de 16 GB o más.

Batería RTC oficial de Raspberry Pi 5 (recomendado para mantener la hora sin energía).

Fuente de alimentación:

Fuente de alimentación USB-C para la Raspberry Pi 5 (5V, 5A).

Configuración del Software ⚙️
Sigue estos pasos en orden para preparar tu sistema y clonar el proyecto.

Paso 0: Preparación del Sistema y Drivers
Instalar Raspberry Pi OS: Es fundamental usar la versión de 64 bits de Raspberry Pi OS Bookworm. Si partes de cero, instala el sistema operativo en tu tarjeta SD siguiendo la guía oficial.

Configurar el AI HAT+: Sigue las instrucciones oficiales para la instalación física y de software del AI HAT+ en tu Raspberry Pi 5. Puedes encontrar la documentación detallada aquí:

Instalación del AI HAT+ en Raspberry Pi

Información general sobre IA en Raspberry Pi

Instalar los Drivers de Hailo: El AI HAT+ necesita sus drivers para funcionar correctamente. Este es un paso fundamental. Sigue la guía de instalación oficial de Hailo.

Paso 1: Clonar Repositorios y Configurar el Entorno Virtual
Tu proyecto está basado en el repositorio de ejemplos de Hailo. Es necesario clonar ambos repositorios y preparar un entorno virtual de Python.

Abre una terminal y clona el repositorio base:

Bash

git clone https://github.com/DeGirum/hailo_examples.git
Navega al directorio del repositorio que acabas de clonar:

Bash

cd hailo_examples
Desde el mismo directorio, clona este repositorio:

Bash

git clone https://github.com/desarrolloag/MonitorDeAtencionHailo.git
Crea y activa un entorno virtual para el proyecto:

Bash

python3 -m venv venv_hailo
source venv_hailo/bin/activate
Instala las librerías de Python necesarias para el repositorio base:

Bash

pip install -r requirements.txt
Paso 2: Integrar el Proyecto y Ejecutar
Ahora integraremos los archivos de tu proyecto y nos aseguraremos de que el código esté configurado para usar los modelos desde la nube de Hailo.

Copia los archivos de tu proyecto al repositorio base, reemplazando los existentes:

Bash

cp MonitorDeAtencionHailo/MedidorAtencion3.py .
cp MonitorDeAtencionHailo/lanzar_medidor.sh .
cp MonitorDeAtencionHailo/medidor_atencion.service .
Edita el script de lanzamiento: Abre lanzar_medidor.sh y verifica que la línea source venv_hailo/bin/activate coincida con el nombre de tu entorno virtual.

Ejecuta el programa:

Abre el archivo MedidorAtencion3.py y verifica que la línea zoo_url = "degirum/hailo" esté presente. Esto asegura que los modelos se descargarán automáticamente desde la nube si no los tienes localmente.

Ejecuta el script de lanzamiento para iniciar el sistema:

Bash

bash lanzar_medidor.sh
Nota: Si tu proyecto usa un Jupyter Notebook (por ejemplo, si has modificado el 003_face_detection.ipynb), asegúrate de haber instalado jupyterlab y de seguir los pasos de la sección de "Uso del programa" para modificar el nombre del modelo y ejecutar las celdas.

Estructura del Repositorio 📂
MedidorAtencion3.py: El script principal de Python que ejecuta la lógica del proyecto.

lanzar_medidor.sh: Script de lanzamiento que activa el entorno virtual y ejecuta el programa.

medidor_atencion.service: Archivo de configuración de systemd para el inicio automático.

requirements.txt: Lista de librerías de Python necesarias.

evidencia/: Carpeta donde se guardan las fotos de los impactos.

registro_impactos.xlsx: Archivo de Excel con los registros de atención.

Uso y Calibración del Programa ▶️
Antes de ejecutar, abre el archivo MedidorAtencion3.py y ajusta los parámetros que se encuentran al inicio del script. Tu programa utiliza los siguientes colores para la visualización:

UMBRAL_ROSTRO_CERCA: El tamaño mínimo del rostro para ser considerado.

TIEMPO_ATENCION_SEGUNDOS: El tiempo en segundos que una persona debe mantener la atención para contar como un "impacto".

COLOR_PERSONA: Cian para el recuadro de la persona cuando no se ha contado un impacto.

COLOR_CONTADO: Naranja para el recuadro de la persona cuando se ha contado un impacto.

COLOR_VERDE: Verde para el recuadro del rostro cuando se detecta "atención activa".

COLOR_AMARILLO: Amarillo para los puntos clave del rostro (ojos, nariz, etc.) y para el texto informativo.

Autoinicio del Sistema 🚀
Para que el script inicie automáticamente al encender la Raspberry Pi, sigue estos pasos:

Edita el archivo de servicio: Abre medidor_atencion.service y modifica los siguientes campos con tu información:

WorkingDirectory: Cambia mi_usuario por tu nombre de usuario y hailo_examples por la ruta correcta de tu proyecto.

ExecStart: Asegúrate de que la ruta del script lanzar_medidor.sh sea correcta.

User: Cambia mi_usuario por tu nombre de usuario de la Raspberry Pi.

Copia el archivo de servicio a la carpeta del sistema (este comando necesita permisos de administrador):

Bash

sudo cp medidor_atencion.service /etc/systemd/system/
Recarga el daemon y habilita el servicio:

Bash

sudo systemctl daemon-reload
sudo systemctl enable medidor_atencion.service
Inicia el servicio para probarlo:

Bash

sudo systemctl start medidor_atencion.service
Para detenerlo, usa el comando sudo systemctl stop medidor_atencion.service.

Solución de Problemas 🤔
El programa no inicia o se cierra:

Revisa los logs con journalctl -u medidor_atencion.service para ver el error.

Asegúrate de que Environment="DISPLAY=:0" esté en el archivo de servicio.

"Camera not found" o pantalla negra:

Verifica que la cámara USB esté bien conectada.

Usa lsusb en la terminal para confirmar que la cámara sea detectada.

Bajo rendimiento (video lento):

Asegúrate de que el AI HAT+ esté conectado firmemente y que los drivers de Hailo estén activos.

Errores de externally-managed-environment:

Este error se soluciona usando un entorno virtual de Python, como se explica en el Paso 1.
