import pyautogui
import cv2
import numpy as np
import time
import logging
import threading

logger = logging.getLogger(__name__)

class KeyboardManager:
    def __init__(self):
        self.is_monitoring = False
        self.monitor_thread = None
        self.error_detection_enabled = True
        
    def start_error_monitoring(self):
        """Inicia el monitoreo continuo de ventanas de error"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._error_monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Monitoreo de errores iniciado")
        
    def stop_error_monitoring(self):
        """Detiene el monitoreo de errores"""
        self.is_monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        logger.info("Monitoreo de errores detenido")
        
    def _error_monitor_loop(self):
        """Loop principal para detección de errores"""
        while self.is_monitoring:
            try:
                # Detectar ventana de error b9
                if self.error_detection_enabled:
                    self.detectar_y_cerrar_error()
                    
                time.sleep(0.5)  # Revisar cada medio segundo
                
            except Exception as e:
                logger.error(f"Error en el monitoreo: {e}")
                time.sleep(1)
    
    def detectar_y_cerrar_error(self):
        """
        Detecta la ventana de error (b9.png) y presiona Enter para cerrarla
        Returns:
            bool: True si encontró y cerró la ventana de error
        """
        try:
            # Cargar template de la ventana de error
            template = cv2.imread('img/b9.png')
            if template is None:
                return False
            
            # Capturar pantalla
            screenshot = pyautogui.screenshot()
            pantalla = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Realizar template matching
            result = cv2.matchTemplate(pantalla, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            
            confianza_minima = 0.6
            
            if max_val >= confianza_minima:
                logger.info(f"Ventana de error detectada con confianza: {max_val:.2f}")
                
                # Presionar Enter para cerrar la ventana de error
                pyautogui.press('enter')
                time.sleep(0.5)
                
                logger.info("Ventana de error cerrada con Enter")
                return True
                
        except Exception as e:
            logger.error(f"Error detectando ventana de error: {e}")
            
        return False
    
    def presionar_enter_final(self, veces=3, intervalo=0.5):
        """
        Presiona Enter múltiples veces al final del ciclo
        Args:
            veces: Número de veces a presionar Enter
            intervalo: Tiempo entre cada pulsación
        """
        try:
            logger.info(f"Presionando Enter {veces} veces con intervalo de {intervalo}s")
            
            for i in range(veces):
                pyautogui.press('enter')
                if i < veces - 1:  # No esperar después del último Enter
                    time.sleep(intervalo)
                    
            logger.info("Enter final completado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error presionando Enter final: {e}")
            return False
    
    def presionar_enter_simple(self, veces=1, intervalo=0.1):
        """
        Presiona Enter una o más veces de forma simple
        """
        try:
            pyautogui.press('enter', presses=veces, interval=intervalo)
            return True
        except Exception as e:
            logger.error(f"Error presionando Enter simple: {e}")
            return False
    
    def enable_error_detection(self):
        """Habilita la detección de errores"""
        self.error_detection_enabled = True
        logger.info("Detección de errores habilitada")
    
    def disable_error_detection(self):
        """Deshabilita la detección de errores"""
        self.error_detection_enabled = False
        logger.info("Detección de errores deshabilitada")