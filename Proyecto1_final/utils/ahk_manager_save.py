# utils/ahk_manager_save.py
import subprocess
import time
import os
import logging
import threading

logger = logging.getLogger(__name__)

class AHKSaveManager:
    def __init__(self, ahk_path="AutoHotkey_1.1.37.02/AutoHotkeyU64.exe"):
        self.ahk_process = None
        self.script_path = "ahk_save.ahk"
        self.ahk_path = ahk_path
        self.batch_counter = 0
        self.save_lock = threading.Lock()
        self.is_running = False  # Agrega este atributo
        
    def crear_script_ahk(self):
        """Crea automáticamente el script de AutoHotkey para guardar"""
        ahk_script = '''#Persistent
#SingleInstance force

; Script de AutoHotkey para guardar con Ctrl+S
Loop {
    ; Esperar comandos de Python
    FileRead, comando, ahk_save_command.txt
    if (ErrorLevel = 0) {
        FileDelete, ahk_save_command.txt
        
        ; Parsear comando: acción
        accion := Trim(comando)
        
        ; Ejecutar acción de guardar
        if (accion = "SAVE") {
            ; Enviar Ctrl+S para guardar
            Send, ^s
            Sleep, 1000
            
            ; Confirmación para Python
            FileDelete, ahk_savedone.txt
            FileAppend, saved, ahk_savedone.txt
            Sleep, 300
        }
    }
    Sleep, 500
}
'''
        try:
            with open(self.script_path, "w", encoding="utf-8") as f:
                f.write(ahk_script)
            logger.info("Script de AutoHotkey para guardar creado automáticamente")
            return True
        except Exception as e:
            logger.error(f"Error creando script AHK: {e}")
            return False
            
    def start_ahk(self):
        """Inicia AutoHotkey"""
        if self.ahk_process and self.ahk_process.poll() is None:
            self.is_running = True
            logger.info("AutoHotkey ya está en ejecución")
            return True
            
        try:
            # Verificar que AutoHotkey existe
            if not os.path.exists(self.ahk_path):
                logger.error(f"No se encuentra AutoHotkey en: {self.ahk_path}")
                # Intentar con la ruta alterna
                self.ahk_path = "AutoHotkeyU64.exe"
                if not os.path.exists(self.ahk_path):
                    logger.error("No se encuentra AutoHotkeyU64.exe en el directorio")
                    return False
            
            # Crear script si no existe
            if not os.path.exists(self.script_path):
                if not self.crear_script_ahk():
                    return False
            
            # Limpiar archivos viejos
            for file in ["ahk_save_command.txt", "ahk_savedone.txt"]:
                if os.path.exists(file):
                    try:
                        os.remove(file)
                    except:
                        pass
            
            # Iniciar proceso
            logger.info(f"Iniciando AHK desde: {self.ahk_path}")
            self.ahk_process = subprocess.Popen([self.ahk_path, self.script_path])
            
            # Esperar a que inicie
            time.sleep(3)
            
            # Verificar si está corriendo
            if self.ahk_process.poll() is None:
                self.is_running = True
                logger.info("AutoHotkey iniciado correctamente")
                return True
            else:
                self.is_running = False
                logger.error("AutoHotkey no se pudo iniciar (proceso terminado)")
                return False
                
        except Exception as e:
            logger.error(f"Error iniciando AutoHotkey: {e}")
            self.is_running = False
            return False
            
    def stop_ahk(self):
        """Detiene AutoHotkey correctamente"""
        self.is_running = False
        if self.ahk_process:
            try:
                self.ahk_process.terminate()
                self.ahk_process.wait(timeout=3)
                logger.info("AutoHotkey detenido correctamente")
            except subprocess.TimeoutExpired:
                self.ahk_process.kill()
                logger.warning("AutoHotkey fue forzado a detenerse")
            except Exception as e:
                logger.error(f"Error deteniendo AutoHotkey: {e}")
                
    def trigger_save(self):
        """Envía comando para guardar (Ctrl+S)"""
        with self.save_lock:
            try:
                # Verificar que AHK esté corriendo
                if not self.is_running or (self.ahk_process and self.ahk_process.poll() is not None):
                    logger.error("AHK no está corriendo, no se puede guardar")
                    return False
                
                # Limpiar archivo de confirmación previo
                if os.path.exists("ahk_savedone.txt"):
                    os.remove("ahk_savedone.txt")
                
                # Crear archivo de comando
                logger.info("Enviando comando SAVE a AHK...")
                with open("ahk_save_command.txt", "w", encoding="utf-8") as f:
                    f.write("SAVE")
                
                # Esperar confirmación (tiempo aumentado)
                timeout = 10
                start_time = time.time()
                
                while time.time() - start_time < timeout:
                    if os.path.exists("ahk_savedone.txt"):
                        # Leer contenido para verificar
                        try:
                            with open("ahk_savedone.txt", "r") as f:
                                content = f.read().strip()
                            if content == "saved":
                                # Limpiar archivo de confirmación
                                os.remove("ahk_savedone.txt")
                                logger.info("Guardado confirmado por AHK")
                                return True
                        except Exception as e:
                            logger.error(f"Error leyendo archivo de confirmación: {e}")
                    
                    time.sleep(0.5)  # Esperar medio segundo entre chequeos
                
                logger.warning("Timeout esperando confirmación de AHK")
                return False
                
            except Exception as e:
                logger.error(f"Error enviando comando de guardar a AHK: {e}")
                return False
    
    def check_ahk_status(self):
        """Verifica el estado de AHK y archivos"""
        status = {
            "ahk_running": self.is_running,
            "ahk_process_exists": self.ahk_process is not None,
            "ahk_process_alive": self.ahk_process and self.ahk_process.poll() is None,
            "script_exists": os.path.exists(self.script_path),
            "ahk_executable_exists": os.path.exists(self.ahk_path),
            "command_file_exists": os.path.exists("ahk_save_command.txt"),
            "done_file_exists": os.path.exists("ahk_savedone.txt")
        }
        logger.info(f"Estado AHK: {status}")
        return status