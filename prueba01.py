import pyautogui
import cv2
import numpy as np

#Para ejecutar el programa asegurate que la imagen boton.png sea el boton que se require buscar 

# Obtener las dimensiones de toda la pantalla
ancho_pantalla, alto_pantalla = pyautogui.size()

# Configuración de la región de la ventana de la VM (toda la pantalla)
vm_region = (0, 0, ancho_pantalla, alto_pantalla)  # (x, y, ancho, alto)

# Capturar pantalla de la VM
screenshot = pyautogui.screenshot(region=vm_region)
img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

# Cargar template del botón
template = cv2.imread('image.png')
# Verificar si la imagen se cargó correctamente
if template is None:
    raise ValueError("No se pudo cargar la imagen 'boton.png'. Verifica la ruta y el formato.")

h, w = template.shape[:2]

# Buscar el botón
result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
_, max_val, _, max_loc = cv2.minMaxLoc(result)

# Umbral de confianza para la detección
umbral_confianza = 0.6

if max_val > umbral_confianza:
    # Calcular centro del botón en coordenadas globales
    center_x = vm_region[0] + max_loc[0] + w//2
    center_y = vm_region[1] + max_loc[1] + h//2
    
    # Mover el mouse y hacer clic
    pyautogui.moveTo(center_x, center_y)
    pyautogui.click()
    
    print(f"Botón encontrado en coordenadas: ({center_x}, {center_y})")
    print(f"Nivel de confianza: {max_val:.2f}")
else:
    print(f"Botón no encontrado. Mejor coincidencia con confianza: {max_val:.2f}")
    
    # Opcional: Mostrar dónde se encontró la mejor coincidencia (aunque no supere el umbral)
    if max_val > 0.5:  # Mostrar si hay al menos cierta similitud
        center_x = vm_region[0] + max_loc[0] + w//2
        center_y = vm_region[1] + max_loc[1] + h//2
        print(f"Mejor coincidencia en: ({center_x}, {center_y})")

# Opcional: Guardar la captura de pantalla para depuración
#cv2.imwrite('captura_pantalla.png', img)
