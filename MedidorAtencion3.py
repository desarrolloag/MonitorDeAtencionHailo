#!/usr/bin/env python
# coding: utf-8

# In[3]:


import cv2
import degirum as dg, degirum_tools
from degirum_tools.video_support import get_video_stream_properties
import numpy as np
import time
import os
import pandas as pd

# --- Configuración de la inferencia ---
inference_host_address = "@local"
zoo_url = "degirum/hailo"
token = ''
device_type = "HAILORT/HAILO8"

# --- Fuente de video ---
# Utiliza la siguiente línea para probar con un video desde internet
# video_source = "https://raw.githubusercontent.com/DeGirum/PySDKExamples/main/images/WalkingPeople2.mp4"
# O utiliza esta línea para usar una cámara local (0 para la cámara por defecto)
video_source = 0
display_name = "Deteccion de Personas y Orientacion"

# --- Nombres de los modelos ---
person_det_model_name = "yolov8n_relu6_coco_pose--640x640_quant_hailort_hailo8_1"
face_det_model_name = "yolov8n_relu6_widerface_kpts--640x640_quant_hailort_hailo8_1"

print(f"Cargando modelo de detección de personas: {person_det_model_name}")
print(f"Cargando modelo de detección facial: {face_det_model_name}")

# --- Cargar los modelos ---
try:
    person_det_model = dg.load_model(
        model_name=person_det_model_name,
        inference_host_address=inference_host_address,
        zoo_url=zoo_url,
        token=token,
        device_type=device_type
    )
    face_det_model = dg.load_model(
        model_name=face_det_model_name,
        inference_host_address=inference_host_address,
        zoo_url=zoo_url,
        token=token,
        device_type=device_type
    )
    print("Modelos cargados exitosamente.")
except Exception as e:
    print(f"Error al cargar los modelos: {e}")
    raise e

print("Modelos cargados. Iniciando procesamiento de video.")

# --- Umbrales de distancia y orientación ---
UMBRAL_ROSTRO_CERCA = 60
UMBRAL_DISTANCIA_RASTREO = 150
# --- NUEVO UMBRAL PARA LA MIRADA ---
UMBRAL_DESVIACION_MIRADA = 0.2

# --- Configuración de la lógica de negocio ---
TIEMPO_ATENCION_SEGUNDOS = 10
TIEMPO_GRACIA_SEGUNDOS = 2

# Directorio para guardar las evidencias fotográficas
EVIDENCE_DIR = "evidencias_impactos"
# Nombre del archivo para el historial de impactos
EXCEL_FILENAME = "registro_impactos.xlsx"

# Colores (BGR para OpenCV)
COLOR_ROJO = (0, 0, 255)
COLOR_VERDE = (0, 255, 0)
COLOR_ROSTRO_NO_INTERES = (0, 255, 255)
COLOR_AMARILLO = (0, 255, 255)
COLOR_CONTADO = (0, 165, 255) # Naranja para impactos ya contados
COLOR_PERSONA = (255, 255, 0) # Cian para el recuadro de la persona
COLOR_MIRADA_LINEA = (0, 0, 255) # Rojo para la línea de la mirada

# Variables de estado
impact_count = 0
next_person_id = 1
# Diccionario para rastrear a cada persona: {id: {'bbox': bbox, 'attention_time': float, 'last_seen_time': float, 'last_attention_time': float, 'impact_counted': bool}}
tracked_persons = {}
last_frame_time = time.time()

# Función para calcular la distancia entre los centros de dos BBoxes
def bbox_center_distance(bbox1, bbox2):
    c1 = ((bbox1[0] + bbox1[2]) / 2, (bbox1[1] + bbox1[3]) / 2)
    c2 = ((bbox2[0] + bbox2[2]) / 2, (bbox2[1] + bbox2[3]) / 2)
    return ((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)**0.5

# Función para guardar el registro en Excel
def save_impact_to_excel(impact_number):
    """Guarda la información de un impacto en un archivo de Excel."""

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    new_impact_data = {
        'fecha_hora': [timestamp],
        'impacto_total': [impact_number]
    }

    new_df = pd.DataFrame(new_impact_data)

    file_exists = os.path.exists(EXCEL_FILENAME)

    if file_exists:
        try:
            existing_df = pd.read_excel(EXCEL_FILENAME, engine='openpyxl')
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
            updated_df.to_excel(EXCEL_FILENAME, index=False, engine='openpyxl')
        except Exception as e:
            print(f"Error al actualizar el archivo de Excel: {e}")
            new_df.to_excel(EXCEL_FILENAME, index=False, engine='openpyxl')
    else:
        new_df.to_excel(EXCEL_FILENAME, index=False, engine='openpyxl')

    print(f"Impacto #{impact_number} registrado en {EXCEL_FILENAME}")

# --- Crear el directorio para evidencias si no existe ---
if not os.path.exists(EVIDENCE_DIR):
    os.makedirs(EVIDENCE_DIR)

# --- Abrir la ventana de visualización y ejecutar la inferencia ---
try:
    ancho_pantalla = 1920
    alto_pantalla = 1080

    cv2.namedWindow(display_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(display_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    with degirum_tools.open_video_stream(video_source) as video_stream:
        for i, frame in enumerate(degirum_tools.video_source(video_stream)):
            current_time = time.time()
            time_delta = current_time - last_frame_time
            last_frame_time = current_time

            img_to_draw = frame.copy()

            # --- Paso 1: Detección de personas en el fotograma completo ---
            person_results = person_det_model(frame)
            person_detections = [r for r in person_results.results if r.get('label') == 'person']

            # --- Paso 2: Detección de rostros en ROIs de personas y mapeo ---
            person_face_mapping = {}
            for p_det in person_detections:
                p_bbox = p_det['bbox']
                px1, py1, px2, py2 = map(int, p_bbox)
                roi = frame[py1:py2, px1:px2]

                if roi.size > 0:
                    face_in_roi_results = face_det_model(roi)
                    best_match_face = None
                    max_area = 0
                    for f_det in face_in_roi_results.results:
                        if f_det.get('label') == 'face' and 'bbox' in f_det:
                            face_bbox = f_det['bbox']
                            face_area = (face_bbox[2] - face_bbox[0]) * (face_bbox[3] - face_bbox[1])
                            if face_area > max_area:
                                max_area = face_area
                                best_match_face = f_det

                    if best_match_face:
                        best_match_face['bbox'][0] += px1
                        best_match_face['bbox'][1] += py1
                        best_match_face['bbox'][2] += px1
                        best_match_face['bbox'][3] += py1
                        if 'landmarks' in best_match_face:
                            for landmark in best_match_face['landmarks']:
                                landmark['landmark'][0] += px1
                                landmark['landmark'][1] += py1
                        person_face_mapping[tuple(p_bbox)] = best_match_face

            # --- Lógica de rastreo de personas ---
            new_detections = [p['bbox'] for p in person_detections]
            matched_pairs = []

            for person_id, data in tracked_persons.items():
                for idx, det_bbox in enumerate(new_detections):
                    dist = bbox_center_distance(data['bbox'], det_bbox)
                    if dist < UMBRAL_DISTANCIA_RASTREO:
                        matched_pairs.append((dist, person_id, idx))

            matched_pairs.sort(key=lambda x: x[0])

            matched_person_ids = set()
            matched_detection_indices = set()

            for dist, person_id, idx in matched_pairs:
                if person_id not in matched_person_ids and idx not in matched_detection_indices:
                    det_bbox = new_detections[idx]
                    is_of_interest = False

                    if tuple(det_bbox) in person_face_mapping:
                        face_det = person_face_mapping[tuple(det_bbox)]
                        fx1, fy1, fx2, fy2 = map(int, face_det['bbox'])
                        face_height = fy2 - fy1

                        # --- LÓGICA DE CORRECCIÓN: Usar Keypoints para la orientación ---
                        if 'landmarks' in face_det and len(face_det['landmarks']) >= 5:
                            kpts = [lm['landmark'] for lm in face_det['landmarks']]
                            left_eye_x, left_eye_y = kpts[0]
                            right_eye_x, right_eye_y = kpts[1]
                            nose_x, nose_y = kpts[2]

                            eyes_center_x = (left_eye_x + right_eye_x) / 2
                            face_center_x = (fx1 + fx2) / 2

                            # Medir la desviación del punto de la nariz respecto al centro de los ojos
                            # normalizado por la anchura del rostro
                            gaze_deviation = abs(nose_x - eyes_center_x) / (fx2 - fx1)

                            if gaze_deviation < UMBRAL_DESVIACION_MIRADA and face_height >= UMBRAL_ROSTRO_CERCA:
                                is_of_interest = True
                        # --- FIN DE LA LÓGICA DE CORRECCIÓN ---

                    data = tracked_persons[person_id]
                    data['bbox'] = det_bbox
                    data['last_seen_time'] = current_time

                    if is_of_interest:
                        if not data['impact_counted']:
                            data['attention_time'] += time_delta
                        data['last_attention_time'] = current_time
                    elif (current_time - data['last_attention_time']) > TIEMPO_GRACIA_SEGUNDOS:
                        data['attention_time'] = 0.0
                        data['impact_counted'] = False

                    matched_person_ids.add(person_id)
                    matched_detection_indices.add(idx)

            tracked_persons = {pid: data for pid, data in tracked_persons.items() if (current_time - data['last_seen_time']) < TIEMPO_GRACIA_SEGUNDOS}

            for idx, det_bbox in enumerate(new_detections):
                if idx not in matched_detection_indices:
                    is_of_interest = False
                    attention_time_init = 0.0
                    last_attention_time_init = 0.0

                    if tuple(det_bbox) in person_face_mapping:
                        face_det = person_face_mapping[tuple(det_bbox)]
                        fx1, fy1, fx2, fy2 = map(int, face_det['bbox'])
                        face_height = fy2 - fy1

                        if 'landmarks' in face_det and len(face_det['landmarks']) >= 5:
                            kpts = [lm['landmark'] for lm in face_det['landmarks']]
                            left_eye_x, left_eye_y = kpts[0]
                            right_eye_x, right_eye_y = kpts[1]
                            nose_x, nose_y = kpts[2]

                            eyes_center_x = (left_eye_x + right_eye_x) / 2
                            face_center_x = (fx1 + fx2) / 2
                            gaze_deviation = abs(nose_x - eyes_center_x) / (fx2 - fx1)

                            if gaze_deviation < UMBRAL_DESVIACION_MIRADA and face_height >= UMBRAL_ROSTRO_CERCA:
                                is_of_interest = True

                    if is_of_interest:
                        attention_time_init = time_delta
                        last_attention_time_init = current_time

                    tracked_persons[next_person_id] = {
                        'bbox': det_bbox,
                        'attention_time': attention_time_init,
                        'last_seen_time': current_time,
                        'last_attention_time': last_attention_time_init,
                        'impact_counted': False
                    }
                    next_person_id += 1

            impacts_to_save_evidence = []
            for person_id, data in list(tracked_persons.items()):
                if data['attention_time'] >= TIEMPO_ATENCION_SEGUNDOS and not data['impact_counted']:
                    impact_count += 1
                    data['impact_counted'] = True
                    print(f"¡Impacto positivo detectado! Total de impactos: {impact_count}")
                    save_impact_to_excel(impact_count)
                    impacts_to_save_evidence.append(person_id)

            # --- Visualización ---
            atencion_activa = False
            for person_id, data in list(tracked_persons.items()):
                x1, y1, x2, y2 = map(int, data['bbox'])

                person_display_color = COLOR_PERSONA
                if data['impact_counted']:
                    person_display_color = COLOR_CONTADO
                    atencion_activa = True
                elif data['attention_time'] > 0:
                    person_display_color = COLOR_VERDE
                    atencion_activa = True

                cv2.rectangle(img_to_draw, (x1, y1), (x2, y2), person_display_color, 2)

                label_text = ""
                if data['attention_time'] > 0:
                    label_text = f"Atencion: {data['attention_time']:.2f}s"
                if data['impact_counted']:
                    label_text = f"Impacto Contado"

                if label_text:
                    cv2.putText(img_to_draw, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, person_display_color, 2)

                # Buscar el rostro correspondiente para dibujar
                for det_bbox_tuple in person_face_mapping:
                    if bbox_center_distance(data['bbox'], list(det_bbox_tuple)) < UMBRAL_DISTANCIA_RASTREO:
                        face_det = person_face_mapping[det_bbox_tuple]
                        fx1, fy1, fx2, fy2 = map(int, face_det['bbox'])

                        face_display_color = COLOR_ROSTRO_NO_INTERES
                        if data['attention_time'] > 0:
                            face_display_color = COLOR_VERDE

                        cv2.rectangle(img_to_draw, (fx1, fy1), (fx2, fy2), face_display_color, 2)

                        if 'landmarks' in face_det:
                            kpts = [lm['landmark'] for lm in face_det['landmarks']]
                            for kpt in kpts:
                                cv2.circle(img_to_draw, (int(kpt[0]), int(kpt[1])), 3, COLOR_AMARILLO, -1)
                        break

            if atencion_activa:
                cv2.putText(img_to_draw, "ATENCION ACTIVA", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, COLOR_AMARILLO, 2)
            cv2.putText(img_to_draw, f"Impactos: {impact_count}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, COLOR_AMARILLO, 2)

            for person_id in impacts_to_save_evidence:
                timestamp_str = time.strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(EVIDENCE_DIR, f"evidencia_impacto_{timestamp_str}.jpg")
                cv2.imwrite(filename, img_to_draw)
                print(f"¡Evidencia fotográfica guardada!: {filename}")

            h_orig, w_orig, _ = img_to_draw.shape
            aspect_ratio_orig = w_orig / h_orig
            aspect_ratio_screen = ancho_pantalla / alto_pantalla

            if aspect_ratio_orig > aspect_ratio_screen:
                ancho_redimensionado = ancho_pantalla
                alto_redimensionado = int(ancho_pantalla / aspect_ratio_orig)
            else:
                alto_redimensionado = alto_pantalla
                ancho_redimensionado = int(alto_pantalla * aspect_ratio_orig)

            img_resized = cv2.resize(img_to_draw, (ancho_redimensionado, alto_redimensionado), interpolation=cv2.INTER_AREA)
            fondo_negro = np.zeros((alto_pantalla, ancho_pantalla, 3), dtype=np.uint8)
            y_offset = (alto_pantalla - alto_redimensionado) // 2
            x_offset = (ancho_pantalla - ancho_redimensionado) // 2
            fondo_negro[y_offset:y_offset + alto_redimensionado, x_offset:x_offset + ancho_redimensionado] = img_resized

            cv2.imshow(display_name, fondo_negro)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

except Exception as e:
    print(f"Error durante el streaming o la visualización: {e}")
    print("Asegúrate de que la fuente de video sea accesible y que tu entorno gráfico esté configurado.")
    raise e
finally:
    cv2.destroyAllWindows()

print("Procesamiento de video terminado.")


# In[ ]:





# In[ ]:




