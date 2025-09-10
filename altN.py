import pyautogui
import time
time.sleep(1)
pyautogui.hotkey('ctrl', 'o')  # Abrir diálogo de abrir archivo
time.sleep(1)
nombre_archivo = "LT "
for n in range(1, 2):  # Cambiar el rango según la cantidad de archivos que desees crear
    pyautogui.write(nombre_archivo)  # Escribir nombre de archivo
    pyautogui.write(f"{n}")  # Escribir numero de archivo
    pyautogui.write('.kml')  # Escribir extensión
    time.sleep(3)
    pyautogui.press('enter')  # Presionar Enter
    time.sleep(3)
