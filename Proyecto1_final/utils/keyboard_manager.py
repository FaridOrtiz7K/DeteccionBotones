import subprocess
import time
import os
import logging
import threading

logger = logging.getLogger(__name__)

class KeyboardManager:
    def __init__(self):
        self.ahk_process = None
        self.script_path = "keyboard_ahk_script.ahk"
        self.is_ahk_running = False
        self.is_monitoring = False
        self.monitor_thread = None
        
    def crear_script_ahk(self):
        """Crea automáticamente el script de AutoHotkey para teclado"""
        ahk_script = """#Persistent
#SingleInstance force

; Script de AutoHotkey para manejar acciones de teclado y detección de errores
Loop {
    ; === DETECCIÓN DE VENTANA DE ERROR (b9.png) ===
    ImageSearch, ErrorX, ErrorY, 0, 0, A_ScreenWidth, A_ScreenHeight, img/b9.png
    if (ErrorLevel = 0) {
        ; Ventana de error encontrada - presionar Enter para cerrarla
        Send, {Enter}
        Sleep, 1000
        FileAppend, error_detected, keyboard_status.txt
    }
    
    ; === PROCESAR COMANDOS DE TECLADO ===
    FileRead, comando, keyboard_command.txt
    if (ErrorLevel = 0) {
        FileDelete, keyboard_command.txt
        
        ; Parsear comando: action_type,param1,param2
        Array := StrSplit(comando, ",")
        action_type := Array[1]
        
        if (action_type = "press_enter") {
            ; Acción para presionar Enter múltiples veces
            times := Array[2]
            interval := Array[3]
            Loop, %times% {
                Send, {Enter}
                Sleep, %interval%
            }
        } else if (action_type = "type_text") {
            ; Acción para escribir texto
            text_to_type := Array[2]
            SendInput, %text_to_type%
            Sleep, 500
        }
        
        ; Confirmación para Python
        FileAppend, done, keyboard_done.txt
    }
    Sleep, 500  ; Revisar cada medio segundo
}

; Función para buscar imágenes con múltiples intentos
SearchImage(imagePath, maxAttempts := 5) {
    attempts := 0
    while (attempts < maxAttempts) {
        ImageSearch, FoundX, FoundY, 0, 0, A_ScreenWidth, A_ScreenHeight, %imagePath%
        if (ErrorLevel = 0) {
            return {x: FoundX, y: FoundY, found: true}
        }
        attempts++
        Sleep, 1000
    }
    return {found: false}
}
"""
        try:
            with open(self.script_path, "w", encoding="utf-8") as f:
                f.write(ahk_script)
            logger.info("Script de Keyboard AHK creado automáticamente")
            return True
        except Exception as e:
            logger.error(f"Error creando script Keyboard AHK: {e}")
            return False
    
    def start_ahk(self):
        """Inicia AutoHotkey para el teclado"""
        if self.is_ahk_running and self.ahk_process and self.ahk_process.poll() is None:
            return True
            
        try:
            if not os.path.exists(self.script_path):
                if not self.crear_script_ahk():
                    return False
            
            # Verificar que existe la carpeta img con b9.png
            if not os.path.exists("img/b9.png"):
                logger.warning("Advertencia: No se encontró img/b9.png - la detección de errores no funcionará")
            
            # Buscar AutoHotkey en rutas comunes
            ahk_paths = [
                'AutoHotkey_1.1.37.02/AutoHotkeyU64.exe',
                'AutoHotkey.exe',
                'C:\\Program Files\\AutoHotkey\\AutoHotkey.exe',
                'C:\\Program Files (x86)\\AutoHotkey\\AutoHotkey.exe'
            ]
            
            ahk_executable = None
            for path in ahk_paths:
                if os.path.exists(path):
                    ahk_executable = path
                    break
            
            if not ahk_executable:
                logger.error("No se pudo encontrar AutoHotkey")
                return False
                    
            self.ahk_process = subprocess.Popen([ahk_executable, self.script_path])
            time.sleep(2)
            self.is_ahk_running = self.ahk_process.poll() is None
            
            if self.is_ahk_running:
                logger.info("Keyboard AHK iniciado correctamente")
                # Iniciar monitoreo de estado
                self.start_status_monitoring()
            else:
                logger.error("Keyboard AHK no se pudo iniciar")
            return self.is_ahk_running
            
        except Exception as e:
            logger.error(f"Error iniciando Keyboard AHK: {e}")
            return False
    
    def stop_ahk(self):
        """Detiene AutoHotkey del teclado"""
        self.stop_status_monitoring()
        if self.ahk_process:
            try:
                self.ahk_process.terminate()
                self.ahk_process.wait(timeout=5)
                self.is_ahk_running = False
                logger.info("Keyboard AHK detenido correctamente")
            except subprocess.TimeoutExpired:
                self.ahk_process.kill()
                logger.warning("Keyboard AHK fue forzado a detenerse")
            except Exception as e:
                logger.error(f"Error deteniendo Keyboard AHK: {e}")
    
    def start_status_monitoring(self):
        """Inicia el monitoreo del estado de AHK"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._status_monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Monitoreo de estado de Keyboard AHK iniciado")
        
    def stop_status_monitoring(self):
        """Detiene el monitoreo del estado"""
        self.is_monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        logger.info("Monitoreo de estado de Keyboard AHK detenido")
        
    def _status_monitor_loop(self):
        """Loop para monitorear el estado de AHK"""
        while self.is_monitoring and self.is_ahk_running:
            try:
                self.check_error_status()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error en monitoreo de estado: {e}")
                time.sleep(5)
    
    def presionar_enter_final(self, veces=3, intervalo=500):
        """Envía comando a AHK para presionar Enter múltiples veces al final"""
        if not self.start_ahk():
            logger.error("No se pudo iniciar Keyboard AHK para presionar Enter")
            return False
            
        comando = f"press_enter,{veces},{intervalo}"
        
        try:
            with open("keyboard_command.txt", "w", encoding="utf-8") as f:
                f.write(comando)
            
            logger.info(f"Comando Enter enviado a Keyboard AHK: {veces} veces")
            
            # Esperar confirmación
            timeout = 10
            start_time = time.time()
            while time.time() - start_time < timeout:
                if os.path.exists("keyboard_done.txt"):
                    os.remove("keyboard_done.txt")
                    logger.info("Keyboard AHK completó los Enter exitosamente")
                    return True
                time.sleep(0.5)
            
            logger.warning("Timeout esperando respuesta de Keyboard AHK para Enter")
            return False
            
        except Exception as e:
            logger.error(f"Error enviando comando Enter a Keyboard AHK: {e}")
            return False
    
    def escribir_texto(self, texto):
        """Envía comando a AHK para escribir texto"""
        if not self.start_ahk():
            return False
            
        comando = f"type_text,{texto}"
        
        try:
            with open("keyboard_command.txt", "w", encoding="utf-8") as f:
                f.write(comando)
            
            logger.info(f"Comando de texto enviado a Keyboard AHK: {texto}")
            
            # Esperar confirmación
            timeout = 5
            start_time = time.time()
            while time.time() - start_time < timeout:
                if os.path.exists("keyboard_done.txt"):
                    os.remove("keyboard_done.txt")
                    return True
                time.sleep(0.5)
            
            logger.warning("Timeout esperando respuesta de Keyboard AHK para texto")
            return False
            
        except Exception as e:
            logger.error(f"Error enviando comando de texto a Keyboard AHK: {e}")
            return False
    
    def check_error_status(self):
        """Verifica si AHK detectó algún error recientemente"""
        try:
            if os.path.exists("keyboard_status.txt"):
                with open("keyboard_status.txt", "r") as f:
                    status = f.read().strip()
                os.remove("keyboard_status.txt")
                if "error_detected" in status:
                    logger.info("Keyboard AHK detectó y cerró una ventana de error")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error verificando estado de Keyboard AHK: {e}")
            return False
    
    def is_running(self):
        """Verifica si AHK está ejecutándose"""
        return self.is_ahk_running and self.ahk_process and self.ahk_process.poll() is None