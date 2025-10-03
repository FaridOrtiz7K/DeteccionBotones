import cv2
template = cv2.imread('img/b9.png')  
if template is None:
    print("No se pudo cargar la imagen 'cargarArchivo.png'")
else:
    print("Imagen cargada correctamente")