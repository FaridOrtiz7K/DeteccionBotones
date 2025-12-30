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
            Sleep, 500
            
            ; Confirmación para Python
            FileAppend, saved, ahk_save_done.txt
            Sleep, 100
            FileDelete, ahk_save_done.txt
        }
    }
    Sleep, 500  ; Revisar cada medio segundo
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
            return True  # Ya está en ejecución
            
        try:
            if not os.path.exists(self.script_path):
                if not self.crear_script_ahk():
                    return False
                    
            self.ahk_process = subprocess.Popen([self.ahk_path, self.script_path])
            time.sleep(2)
            is_running = self.ahk_process.poll() is None
            if is_running:
                logger.info("AutoHotkey iniciado correctamente")
            else:
                logger.error("AutoHotkey no se pudo iniciar")
            return is_running
        except Exception as e:
            logger.error(f"Error iniciando AutoHotkey: {e}")
            return False
            
    def stop_ahk(self):
        """Detiene AutoHotkey correctamente"""
        if self.ahk_process:
            try:
                self.ahk_process.terminate() 
                self.ahk_process.wait(timeout=5) 
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
                with open("ahk_save_command.txt", "w", encoding="utf-8") as f:
                    f.write("SAVE")
                
                logger.info("Comando de guardar enviado a AHK")
                
                timeout = 5
                start_time = time.time()
                
                while time.time() - start_time < timeout:
                    if os.path.exists("ahk_save_done.txt"):
                        time.sleep(0.1)
                        if os.path.exists("ahk_save_done.txt"):
                            try:
                                os.remove("ahk_save_done.txt")
                            except:
                                pass
                        return True
                    time.sleep(0.1)
                
                logger.warning("Timeout esperando confirmación de AHK")
                return False
                
            except Exception as e:
                logger.error(f"Error enviando comando de guardar a AHK: {e}")
                return False
    
    def process_batch(self, batch_data=None):
        """Procesa un lote y guarda cada 2 lotes"""
        with self.save_lock:
            self.batch_counter += 1
            
            if batch_data:
                logger.info(f"Procesando lote {self.batch_counter}: {batch_data}")
            else:
                logger.info(f"Procesando lote {self.batch_counter}")
            
            if self.batch_counter % 2 == 0:
                logger.info("Guardando cambios (cada 2 lotes)...")
                return self.trigger_save()
            
            return True
    
    def reset_counter(self):
        """Reinicia el contador de lotes"""
        with self.save_lock:
            self.batch_counter = 0
            logger.info("Contador de lotes reiniciado")