import subprocess
import time
import os
import logging

logger = logging.getLogger(__name__)

class AHKManager:
    def __init__(self):
        self.ahk_process = None
        self.script_path = "ahk_script.ahk"
        
    def crear_script_ahk(self):
        """Crea automáticamente el script de AutoHotkey"""
        ahk_script = """
#Persistent
#SingleInstance force

; Script de AutoHotkey para manejar acciones de UI
Loop {
    ; Esperar comandos de Python
    FileRead, comando, ahk_command.txt
    if (ErrorLevel = 0) {
        FileDelete, ahk_command.txt
        
        ; Parsear comando: x,y,filename
        Array := StrSplit(comando, ",")
        x_campo := Array[1]
        y_campo := Array[2]
        nombre_archivo := Array[3]
        
        ; Ejecutar acciones
        Click, %x_campo% %y_campo%
        Sleep, 200
        
        ; Limpiar campo
        Send, ^a
        Sleep, 100
        Send, {Delete}
        Sleep, 100
        
        ; Escribir nombre de archivo (método confiable)
        SendInput, %nombre_archivo%
        Sleep, 400
        
        ; Presionar Enter
        Send, {Enter}
        Sleep, 200
        
        ; Confirmación para Python
        FileAppend, done, ahk_done.txt
        FileDelete, ahk_done.txt
    }
    Sleep, 500  ; Revisar cada medio segundo
}
"""
        try:
            with open(self.script_path, "w", encoding="utf-8") as f:
                f.write(ahk_script)
            logger.info("Script de AutoHotkey creado automáticamente")
            return True
        except Exception as e:
            logger.error(f"Error creando script AHK: {e}")
            return False
            
    def start_ahk(self):
        """Inicia AutoHotkey de manera más robusta"""
        if self.ahk_process and self.ahk_process.poll() is None:
            return True  # Ya está en ejecución
            
        try:
            if not os.path.exists(self.script_path):
                if not self.crear_script_ahk():
                    return False
                    
            self.ahk_process = subprocess.Popen(['AutoHotkey_1.1.37.02/AutoHotkeyU64.exe', self.script_path])
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
                
    def ejecutar_acciones_ahk(self, x_campo, y_campo, nombre_archivo):
        """Envía comandos a AutoHotkey mediante archivo temporal"""
        # Crear archivo de comandos para AHK
        comando = f"{x_campo},{y_campo},{nombre_archivo}"
        
        try:
            with open("ahk_command.txt", "w", encoding="utf-8") as f:
                f.write(comando)
            
            logger.info(f"Comando enviado a AHK: {comando}")
            return True
        except Exception as e:
            logger.error(f"Error enviando comando a AHK: {e}")
            return False