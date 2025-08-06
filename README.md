# Sistema de Analítica de Atención en Vitrinas 🤖️

Este proyecto utiliza una Raspberry Pi 5 y un acelerador de IA Hailo para medir la atención de las personas hacia una vitrina o exhibición de productos. Cuando el sistema detecta una **"atención cualificada"** (una persona mira fijamente por un tiempo), registra un "impacto visual" y toma una fotografía como evidencia.

![placeholder](https://i.imgur.com/v2Jz7g6.png)
*(Aquí puedes poner una foto o un GIF de tu proyecto en acción)*

## Índice

* [Hardware Requerido](#-hardware-requerido-️)
* [Configuración del Software](#-configuración-del-software)
* [Estructura del Repositorio](#-estructura-del-repositorio)
* [Uso y Calibración del Programa](#-uso-y-calibración-del-programa)
* [Autoinicio del Sistema](#-autoinicio-del-sistema)
* [Solución de Problemas](#-solución-de-problemas)

---

### **Requisitos de Hardware** 🛠️

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

Sigue estos pasos para preparar tu Raspberry Pi. Se asume que los drivers del AI HAT+ de Hailo ya están instalados.

#### **Paso 1: Clonar este Repositorio**

Abre una terminal y clona este repositorio:
```bash
git clone [https://github.com/TU_USUARIO/MonitorDeAtencionHailo.git](https://github.com/TU_USUARIO/MonitorDeAtencionHailo.git)
cd MonitorDeAtencionHailo
