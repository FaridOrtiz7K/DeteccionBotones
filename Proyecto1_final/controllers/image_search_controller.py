import threading
import time
import pyautogui
import cv2
import numpy as np
import os
import subprocess
import keyboard
import logging
from models.image_search_model import ImageSearchModel
from utils.ahk_manager import AHKManager

logger = logging.getLogger(__name__)

class ImageSearchController:
    def __init__(self, root):
        self.model = ImageSearchModel()
        self.root = root
        self.view = None
        self.pause_window = None
        self.authenticated = False
        self.search_thread = None
        self.ahk_manager = AHKManager()
        self.nombre_archivo = ""
        
        # Configurar tecla ESC para pausar
        keyboard.on_press_key("esc", lambda e: self.pause_search())
        
        # Mostrar ventana de login
        self.show_login_window()
    
    def validate_inputs(self):
        """Valida todas las entradas antes de iniciar"""
        errors = []
        
        if not self.model.no_distrito and not self.model.distrito.strip():
            errors.append("Debe ingresar un distrito o marcar 'No tiene distrito'")
        
        if self.model.lote_inicial > self.model.lote_final:
            errors.append("El lote inicial no puede ser mayor al lote final")
        
        if self.model.lote_inicial < 1 or self.model.lote_final < 1:
            errors.append("Los números de lote deben ser positivos")
        
        # Verificar que las imágenes existan
        for imagen, _, _ in self.model.image_sequence:
            if not os.path.exists(imagen):
                errors.append(f"No se encuentra la imagen: {imagen}")
        
        return errors
    
    def show_login_window(self):
        """Muestra la ventana de login"""
        from views.login_window import LoginWindow
        self.login_window = LoginWindow(self.root, self)
        self.login_window.protocol("WM_DELETE_WINDOW", self.root.quit)
    
    def show_main_window(self):
        """Muestra la ventana principal después del login exitoso"""
        from views.main_view import ImageSearchView
        self.view = ImageSearchView(self.root, self)
        self.model.add_observer(self)
        
        # Configurar la ventana principal
        self.root.deiconify()
        self.root.title("Búsqueda de Imágenes Automatizada")
        self.root.geometry("800x600")
        
        # Centrar la ventana
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
    
    def update(self, event, data):
        """Método para recibir actualizaciones del modelo"""
        if event == "running_changed":
            self.view.update_button_states(data, self.model.is_paused)
        elif event == "paused_changed":
            self.view.update_button_states(self.model.is_running, data)
            if data:  # Si está en pausa
                # Mostrar ventana de pausa con la información actual
                self.view.show_pause_window(self.model.current_lote, self.model.lote_final)
        elif event == "image_found":
            self.view.log_message(f"Botón '{data['image']}' encontrado en ({data['x']}, {data['y']}) - Confianza: {data['confidence']:.2f}")
        elif event == "image_not_found":
            self.view.log_message(f"Botón '{data['image']}' no encontrado. Mejor coincidencia: {data['confidence']:.2f} (Intento {data.get('intento', 1)})")
        elif event == "error":
            self.view.log_message(f"Error: {data}")
        elif event == "current_lote_changed":
            self.view.log_message(f"Procesando lote {data} de {self.model.lote_final}")
        elif event == "no_distrito_changed":
            self.view.log_message(f"Opción 'No tiene distrito' cambiada a: {data}")
    
    def update_lote_inicial(self, lote):
        try:
            lote = int(lote)
            self.model.lote_inicial = lote
        except ValueError:
            logger.error("El lote inicial debe ser un número válido")
    
    def update_lote_final(self, lote):
        try:
            lote = int(lote)
            self.model.lote_final = lote
        except ValueError:
            logger.error("El lote final debe ser un número válido")
    
    def update_distrito(self, distrito):
        self.model.distrito = distrito
    
    def update_delay_time(self, time):
        try:
            time = int(time)
            self.model.delay_time = time
        except ValueError:
            logger.error("El tiempo de espera debe ser un número válido")
    
    def update_no_distrito(self, value):
        self.model.no_distrito = value
    
    def encontrar_ventana_archivo(self):
        """Busca la ventana de archivo usando template matching con reintentos inteligentes"""
        intentos = 1
        confianza_minima = 0.6
        tiempo_espera_base = 1
        tiempo_espera_largo = 10
        
        # Cargar template una sola vez fuera del bucle
        template = cv2.imread('img/cargarArchivo.png')
        if template is None:
            logger.error("No se pudo cargar la imagen 'cargarArchivo.png'")
            return None
        
        while self.model.is_running: 
            # Verificar si está pausado
            if self.model.is_paused:
                with self.model.pause_condition:
                    while self.model.is_paused and self.model.is_running:
                        self.model.pause_condition.wait()
                if not self.model.is_running:
                    return False
            
            try:
                # Capturar pantalla completa
                screenshot = pyautogui.screenshot()
                pantalla = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                # Realizar template matching
                result = cv2.matchTemplate(pantalla, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)
                
                if max_val >= confianza_minima:
                    logger.info(f"Ventana encontrada con confianza: {max_val:.2f}")
                    # Devolver tupla (x, y)
                    return max_loc
                else:
                    # Estrategia de espera progresiva
                    if intentos % 10 == 0 and intentos > 0:
                        logger.info(f"Intento {intentos}: Mejor coincidencia: {max_val:.2f}")
                        logger.info("Esperando 10 segundos...")
                        time.sleep(tiempo_espera_largo)
                    else:
                        time.sleep(tiempo_espera_base)
                    intentos += 1
                    
            except Exception as e:
                logger.error(f"Error durante la búsqueda: {e}")
                time.sleep(tiempo_espera_base)
                intentos += 1

        return None

    def handle_b4_special_behavior(self, imagen, clicks, confianza):
        """Maneja el comportamiento especial para la imagen b4"""
        # Precionamos el boton b4 (Documentos)
        success = self.model.click_button(imagen, clicks, confianza)
        
        # Esperar despues de precionar el boton
        time.sleep(3)

        # Buscar la ventana de archivo
        coordenadas_ventana = self.encontrar_ventana_archivo()

        if coordenadas_ventana:
            x_ventana, y_ventana = coordenadas_ventana
            logger.info(f"Coordenadas ventana: x={x_ventana}, y={y_ventana}")
            
            # Calcular coordenadas del campo de texto
            x_campo = x_ventana + 294
            y_campo = y_ventana + 500
            logger.info(f"Coordenadas campo texto: x={x_campo}, y={y_campo}")
            
            # Iniciar AHK si no está corriendo
            if not self.ahk_manager.start_ahk():
                logger.error("No se pudo iniciar AutoHotkey")
                return False
            
            # Enviar comandos a AHK
            if self.ahk_manager.ejecutar_acciones_ahk(x_campo, y_campo, self.nombre_archivo):
                time.sleep(10)  # Esperar a que AHK complete la acción
            else:
                logger.error("Error enviando comando a AHK")
                return False
        else:
            logger.error("No se pudo encontrar la ventana de archivo.")
            
        if success:
            self.model.alt_n_used = True
        return success
        
    def run_sequence(self):
        """Ejecuta la secuencia completa de imágenes"""
        for imagen, clicks, confianza in self.model.image_sequence:
            # Verificar si está pausado
            if self.model.is_paused:
                with self.model.pause_condition:
                    while self.model.is_paused and self.model.is_running:
                        self.model.pause_condition.wait()
                if not self.model.is_running:  # Verificar si se detuvo durante la pausa
                    return False
            
            # Manejar comportamiento especial para b4
            if "b4.png" in imagen:
                success = self.handle_b4_special_behavior(imagen, clicks, confianza)
            else:
                # Realizar la búsqueda y clic normal para otras imágenes
                success = self.model.click_button(imagen, clicks, confianza)
            
            if not success:
                self.view.log_message(f"Error: No se pudo encontrar el botón '{imagen}' después de {self.model.current_lote} intentos")
                return False
            
            # Esperar 2 segundos entre imágenes (como en el ejemplo)
            if imagen != self.model.image_sequence[-1][0] and self.model.is_running:
                time.sleep(2)
        
        return True
    
    def run_lotes(self):
        """Ejecuta los lotes de búsqueda con mejor manejo de estado"""
        try:
            # Siempre comenzar desde el lote inicial configurado
            current_lote = self.model.lote_inicial
            lote_final = self.model.lote_final
            
            # Actualizar el current_lote en el modelo
            self.model.current_lote = current_lote
            
            while current_lote <= lote_final and self.model.is_running:
                # Verificar pausa de manera más eficiente
                with self.model.pause_condition:
                    while self.model.is_paused and self.model.is_running:
                        self.model.pause_condition.wait()
                
                if not self.model.is_running:
                    break
                    
                self.model.current_lote = current_lote
                
                # Reiniciar flag de Alt+N para cada lote
                self.model.alt_n_used = False
                
                # Generar nombre de archivo según el distrito
                if self.model.no_distrito:
                    self.nombre_archivo = f"LT {current_lote}.KML"
                else:
                    self.nombre_archivo = f"{self.model.distrito}_LT {current_lote}.KML"
                
                self.view.log_message(f"Procesando archivo: {self.nombre_archivo}")
                
                # Realizar la secuencia completa
                success = self.run_sequence()
                
                if success:
                    # Presionar Enter 3 veces después de cada secuencia
                    self.view.log_message("Presionando Enter 3 veces")
                    pyautogui.press('enter', presses=3, interval=0.5)
                    time.sleep(1)
                    
                    # Cada 10 lotes, presionar 'S' para guardar
                    if current_lote % 10 == 0:
                        self.view.log_message("Presionando 'S' para guardar cambios")
                        pyautogui.press('s')
                        time.sleep(1)  # Pequeña espera después de guardar
                    
                    self.view.log_message(f"Secuencia completada para lote {current_lote} de {lote_final}")
                else:
                    self.view.log_message(f"Secuencia interrumpida para lote {current_lote} de {lote_final}")
                    break
                
                # Pasar al siguiente lote
                current_lote += 1
                
                # Esperar el tiempo configurado entre lotes (si no es el último lote)
                if current_lote <= lote_final and self.model.is_running:
                    self.view.log_message(f"Esperando {self.model.delay_time} segundos antes del próximo lote...")
                    
                    # Contar el tiempo de espera mostrando el progreso
                    for i in range(self.model.delay_time, 0, -1):
                        if not self.model.is_running:
                            break
                        if self.model.is_paused:
                            with self.model.pause_condition:
                                while self.model.is_paused and self.model.is_running:
                                    self.model.pause_condition.wait()
                            if not self.model.is_running:
                                break
                        # Actualizar el mensaje cada segundo
                        self.view.log_message(f"Tiempo restante: {i} segundos")
                        time.sleep(1)
                        # Eliminar el mensaje anterior
                        self.view.status_text.delete("end-2l", "end-1l")
            
            self.model.set_running(False)
            self.view.log_message("Proceso completado")
            
        except Exception as e:
            logger.error(f"Error inesperado en run_lotes: {str(e)}")
            self.model.set_running(False)
            self.view.log_message(f"Error inesperado: {str(e)}")
    
    def start_search(self):
        """Inicia la búsqueda en un hilo separado"""
        if not self.authenticated:
            self.view.log_message("Error: Debe iniciar sesión primero.")
            return
            
        # Validar inputs
        errors = self.validate_inputs()
        if errors:
            for error in errors:
                self.view.log_message(f"Error: {error}")
            return
            
        if not self.model.is_running:
            self.model.set_running(True)
            self.model.set_paused(False)
            with self.model.pause_condition:
                self.model.pause_condition.notify_all()
            self.view.log_message("Iniciando proceso de búsqueda...")
            if self.model.no_distrito:
                self.view.log_message("Distrito: No tiene distrito (usando LT)")
            else:
                self.view.log_message(f"Distrito: {self.model.distrito}")
            self.view.log_message(f"Lotes: {self.model.lote_inicial} a {self.model.lote_final}")
            self.view.log_message(f"Tiempo de espera entre lotes: {self.model.delay_time} segundos")
            
            # Mostrar la secuencia a ejecutar
            self.view.log_message("Secuencia predefinida a ejecutar:")
            for i, (imagen, clicks, confianza) in enumerate(self.model.image_sequence, 1):
                self.view.log_message(f"  {i}. {imagen} (clics: {clicks}, confianza: {confianza})")
            
            # Iniciar el hilo para ejecutar los lotes
            self.search_thread = threading.Thread(target=self.run_lotes)
            self.search_thread.daemon = True
            self.search_thread.start()
    
    def pause_search(self):
        """Pausa la búsqueda"""
        if not self.authenticated:
            return
            
        if self.model.is_running and not self.model.is_paused:
            self.model.set_paused(True)
            self.view.log_message("Búsqueda pausada (Presione ESC para reanudar)")
    
    def resume_search(self):
        """Reanuda la búsqueda"""
        if not self.authenticated:
            return
            
        if self.model.is_running and self.model.is_paused:
            self.model.set_paused(False)
            with self.model.pause_condition:
                self.model.pause_condition.notify_all()
            self.view.log_message("Búsqueda reanudada")
    
    def stop_search(self):
        """Detiene la búsqueda"""
        if not self.authenticated:
            return
            
        self.model.set_running(False)
        self.model.set_paused(False)
        with self.model.pause_condition:
            self.model.pause_condition.notify_all()
        self.ahk_manager.stop_ahk()
        self.view.log_message("Proceso detenido")

    def update_no_distrito(self, value):
        """Actualiza el estado de 'no distrito'"""
        self.model.no_distrito = value
        
        # Si se activa "no distrito", limpiar el campo de distrito
        if value and self.model.distrito:
            self.model.distrito = ""
            # Actualizar la vista si existe
            if hasattr(self, 'view') and self.view:
                self.view.distrito_var.set("")
        
        # Guardar en configuración
        self.model.config_manager.set('no_distrito', value)
        
    # def update_error(self, event, data=None):
    #  if event == "error_alert":
    #      # Mostrar diálogo de error con sonido
    #      self.show_error_dialog(data["message"])