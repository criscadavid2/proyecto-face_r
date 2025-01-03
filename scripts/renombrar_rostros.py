import pickle

# Archivo de codificaciones
archivo_codificaciones = "entrenamiento/codificaciones.pkl"

# Nombre antiguo y nuevo
nombre_antiguo = "C"
nombre_nuevo = "Cristina Cadavid"

# Cargar las codificaciones
with open(archivo_codificaciones, "rb") as archivo:
    datos = pickle.load(archivo)

# Actualizar el nombre en la lista
if nombre_antiguo in datos["nombres"]:
    indices = [i for i, nombre in enumerate(datos["nombres"]) if nombre == nombre_antiguo]
    for i in indices:
        datos["nombres"][i] = nombre_nuevo

    # Guardar los cambios
    with open(archivo_codificaciones, "wb") as archivo:
        pickle.dump(datos, archivo)

    print(f"Nombre actualizado de '{nombre_antiguo}' a '{nombre_nuevo}'.")
else:
    print(f"El nombre '{nombre_antiguo}' no se encontró en las codificaciones.")
