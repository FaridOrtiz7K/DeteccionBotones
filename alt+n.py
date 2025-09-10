import pyautogui
import time

# ... (código anterior)
numlt = 1
pyautogui.click(1120, 666)  # Hacer clic en "Documents"
time.sleep(3)  # Esperar 3 segundos
pyautogui.hotkey('alt', 'n')  # Presionar combinación Alt + N
time.sleep(3)  # Esperar 3 segundos
pyautogui.write(f'LT {numlt}.kml')  # Escribir el nombre del archivo

# ... (código posterior)