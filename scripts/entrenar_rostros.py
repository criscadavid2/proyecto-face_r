import os
import face_recognition
import pickle

# Ruta al directorio de las imágenes capturadas
ruta_dataset = "entrenamiento/dataset"
archivo_codificaciones = "entrenamiento/codificaciones.pkl"

# Listas para guardar los datos
nombres = []
codificaciones = []

# Recorrer la carpeta del dataset
for nombre_persona in os.listdir(ruta_dataset):
    ruta_persona = os.path.join(ruta_dataset, nombre_persona)

    if not os.path.isdir(ruta_persona):
        continue

    print(f"Procesando imágenes de {nombre_persona}...")

    # Recorrer las imágenes de la persona
    for archivo_imagen in os.listdir(ruta_persona):
        ruta_imagen = os.path.join(ruta_persona, archivo_imagen)

        # Cargar la imagen con face_recognition
        try:
            imagen = face_recognition.load_image_file(ruta_imagen)
            # Generar las codificaciones del rostro
            codificacion = face_recognition.face_encodings(imagen)

            if len(codificacion) > 0:
                # Guardar el nombre y la codificación
                nombres.append(nombre_persona)
                codificaciones.append(codificacion[0])
                print(f"Codificación generada para {archivo_imagen}")
            else:
                print(f"Advertencia: No se detectó un rostro en {archivo_imagen}")
        except Exception as e:
            print(f"Error al procesar {archivo_imagen}: {e}")

# Guardar las codificaciones en un archivo
print("\nGuardando las codificaciones...")
with open(archivo_codificaciones, "wb") as archivo:
    pickle.dump({"nombres": nombres, "codificaciones": codificaciones}, archivo)

print(f"Codificaciones guardadas en {archivo_codificaciones}")
