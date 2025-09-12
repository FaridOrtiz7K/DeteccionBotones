import pyautogui
import time

time.sleep(3)  # Espera 2 segundos antes de escribir
pyautogui.hotkey('L', 'T',' ','.', 'k', 'm', 'l')  # Escribir "LT .kml"
time.sleep(4)
print("Archivo escrito")
time.sleep(2)