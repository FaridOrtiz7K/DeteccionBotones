import pyautogui
import time
import threading
import pygetwindow as gw
import subprocess
import os
from pynput import keyboard

class VirtualMachineWriter:
    def __init__(self):
        self.is_vm = self.detect_vm()
        print(f"Ejecutando en entorno virtual: {self.is_vm}")
        
    def detect_vm(self):
        """Detectar si estamos ejecutando en una máquina virtual"""
        try:
            # Detección para Windows
            if os.name == 'nt':
                result = subprocess.run('systeminfo', capture_output=True, text=True)
                if 'VirtualBox' in result.stdout or 'VMware' in result.stdout:
                    return True
            
            # Detección para Linux
            elif os.name == 'posix':
                # Verificar sistemas de virtualización comunes
                virtualization_files = [
                    '/proc/cpuinfo',
                    '/sys/class/dmi/id/product_name',
                    '/sys/class/dmi/id/sys_vendor'
                ]
                
                for file in virtualization_files:
                    if os.path.exists(file):
                        with open(file, 'r') as f:
                            content = f.read()
                            if 'virtualbox' in content.lower() or 'vmware' in content.lower() or 'qemu' in content.lower():
                                return True
                
                # Verificar mediante comandos
                try:
                    result = subprocess.run(['dmesg'], capture_output=True, text=True)
                    if 'virtual' in result.stdout.lower() or 'vmware' in result.stdout.lower():
                        return True
                except:
                    pass
                    
            return False
        except:
            return False

    def ensure_focus(self, window_title=None):
        """Asegurarse de que la ventana objetivo tenga el foco"""
        try:
            if window_title:
                windows = gw.getWindowsWithTitle(window_title)
                if windows:
                    window = windows[0]
                    if window.isMinimized:
                        window.restore()
                    window.activate()
                    time.sleep(0.5)  # Esperar a que la ventana se active
        except Exception as e:
            print(f"Error al enfocar ventana: {e}")

    def write_text_basic(self, text):
        """Método básico de escritura"""
        try:
            pyautogui.write(text, interval=0.1)
            return True
        except Exception as e:
            print(f"Error en escritura básica: {e}")
            return False

    def write_text_clipboard(self, text):
        """Método usando portapapeles (Ctrl+V)"""
        try:
            # Copiar al portapapeles
            import pyperclip
            pyperclip.copy(text)
            
            # Pegar
            pyautogui.hotkey('ctrl', 'v')
            return True
        except Exception as e:
            print(f"Error usando portapapeles: {e}")
            return False

    def write_text_direct_input(self, text):
        """Método de entrada directa (usando pynput)"""
        try:
            controller = keyboard.Controller()
            
            for char in text:
                controller.type(char)
                time.sleep(0.05)
            return True
        except Exception as e:
            print(f"Error en entrada directa: {e}")
            return False

    def write_with_retry(self, text, max_attempts=3, window_title=None):
        """Escribir texto con múltiples intentos y métodos"""
        for attempt in range(max_attempts):
            print(f"Intento {attempt + 1} de {max_attempts}")
            
            # Asegurar el foco en la ventana objetivo
            self.ensure_focus(window_title)
            time.sleep(0.5)
            
            # Intentar diferentes métodos
            if self.write_text_basic(text):
                print("Éxito con método básico")
                return True
            time.sleep(1)
            
            if self.write_text_clipboard(text):
                print("Éxito con portapapeles")
                return True
            time.sleep(1)
            
            if self.write_text_direct_input(text):
                print("Éxito con entrada directa")
                return True
                
            time.sleep(1)
        
        print("Todos los métodos fallaron")
        return False

# Uso del script
if __name__ == "__main__":
    writer = VirtualMachineWriter()
    
    # Esperar unos segundos para que puedas hacer clic en la ventana objetivo
    print("Preparándose para escribir... coloca el cursor en el campo de texto")
    time.sleep(5)
    
    # Escribir el texto (en este caso el número 7)
    success = writer.write_with_retry('7', window_title="Bloc de notas")
    
    if success:
        print("Texto escrito exitosamente")
    else:
        print("No se pudo escribir el texto")