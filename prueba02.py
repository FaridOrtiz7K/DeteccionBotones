import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import pyautogui
import cv2
import numpy as np

class ImageSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Búsqueda de Imágenes Automatizada")
        
        # Variables de control
        self.is_running = False
        self.is_paused = False
        self.pause_event = threading.Event()
        self.loop_count = tk.IntVar(value=1)
        self.delay_time = tk.IntVar(value=4)  # Tiempo de espera por defecto: 4 segundos
        self.current_loop = 0
        
        # Crear interfaz
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuración de bucles
        loop_frame = ttk.LabelFrame(main_frame, text="Configuración de Bucles", padding="5")
        loop_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(loop_frame, text="Número de bucles:").grid(row=0, column=0, sticky=tk.W, padx=5)
        loop_spin = ttk.Spinbox(loop_frame, from_=1, to=100, textvariable=self.loop_count, width=10)
        loop_spin.grid(row=0, column=1, padx=5)
        
        # Tiempo de espera entre ejecuciones
        ttk.Label(loop_frame, text="Tiempo de espera (segundos):").grid(row=0, column=2, sticky=tk.W, padx=5)
        delay_spin = ttk.Spinbox(loop_frame, from_=1, to=60, textvariable=self.delay_time, width=5)
        delay_spin.grid(row=0, column=3, padx=5)
        
        # Selección de imagen
        image_frame = ttk.LabelFrame(main_frame, text="Selección de Imagen", padding="5")
        image_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.image_var = tk.StringVar(value="image1.png")
        ttk.Radiobutton(image_frame, text="Imagen 1", variable=self.image_var, value="image1.png").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Radiobutton(image_frame, text="Imagen 2", variable=self.image_var, value="image2.png").grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Botones de control
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Iniciar", command=self.start_search)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.pause_button = ttk.Button(button_frame, text="Pausar", command=self.pause_search, state=tk.DISABLED)
        self.pause_button.grid(row=0, column=1, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Detener", command=self.stop_search, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=2, padx=5)
        
        # Área de estado
        status_frame = ttk.LabelFrame(main_frame, text="Estado", padding="5")
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.status_text = tk.Text(status_frame, height=10, width=50)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        # Configurar expansión de columnas
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        status_frame.columnconfigure(0, weight=1)
        
    def log_message(self, message):
        """Añade un mensaje al área de estado"""
        self.status_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.status_text.see(tk.END)
        
    def search_image(self):
        """Función que busca la imagen y realiza las acciones"""
        image_path = self.image_var.get()
        
        try:
            # Obtener las dimensiones de toda la pantalla
            ancho_pantalla, alto_pantalla = pyautogui.size()

            # Configuración de la región de la ventana de la VM (toda la pantalla)
            vm_region = (0, 0, ancho_pantalla, alto_pantalla)  # (x, y, ancho, alto)

            # Capturar pantalla de la VM
            screenshot = pyautogui.screenshot(region=vm_region)
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            # Cargar template del botón
            template = cv2.imread(image_path)
            # Verificar si la imagen se cargó correctamente
            if template is None:
                self.log_message(f"Error: No se pudo cargar la imagen '{image_path}'. Verifica la ruta y el formato.")
                return False

            h, w = template.shape[:2]

            # Buscar el botón
            result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            # Umbral de confianza para la detección
            umbral_confianza = 0.6

            if max_val > umbral_confianza:
                # Calcular centro del botón en coordenadas globales
                center_x = vm_region[0] + max_loc[0] + w//2
                center_y = vm_region[1] + max_loc[1] + h//2
                
                # Mover el mouse y hacer clic
                pyautogui.moveTo(center_x, center_y)
                pyautogui.click()
                
                self.log_message(f"Botón encontrado en coordenadas: ({center_x}, {center_y})")
                self.log_message(f"Nivel de confianza: {max_val:.2f}")
                return True
            else:
                self.log_message(f"Botón no encontrado. Mejor coincidencia con confianza: {max_val:.2f}")
                
                # Opcional: Mostrar dónde se encontró la mejor coincidencia (aunque no supere el umbral)
                if max_val > 0.5:  # Mostrar si hay al menos cierta similitud
                    center_x = vm_region[0] + max_loc[0] + w//2
                    center_y = vm_region[1] + max_loc[1] + h//2
                    self.log_message(f"Mejor coincidencia en: ({center_x}, {center_y})")
                return False
                
        except Exception as e:
            self.log_message(f"Error durante la búsqueda: {str(e)}")
            return False
    
    def run_loops(self):
        """Ejecuta los bucles de búsqueda"""
        self.current_loop = 0
        total_loops = self.loop_count.get()
        delay = self.delay_time.get()
        
        while self.current_loop < total_loops and self.is_running:
            # Verificar si está pausado
            if self.is_paused:
                self.pause_event.wait()
                if not self.is_running:  # Verificar si se detuvo durante la pausa
                    break
            
            self.current_loop += 1
            self.log_message(f"Ejecutando bucle {self.current_loop} de {total_loops}")
            
            # Realizar la búsqueda
            success = self.search_image()
            
            if success:
                self.log_message("Acción completada con éxito")
            else:
                self.log_message("No se pudo completar la acción")
            
            # Esperar el tiempo configurado entre bucles (si no es el último bucle)
            if self.current_loop < total_loops and self.is_running:
                self.log_message(f"Esperando {delay} segundos antes del próximo bucle...")
                
                # Contar el tiempo de espera mostrando el progreso
                for i in range(delay, 0, -1):
                    if not self.is_running:
                        break
                    if self.is_paused:
                        self.pause_event.wait()
                        if not self.is_running:
                            break
                    # Actualizar el mensaje cada segundo
                    if i != delay:  # No actualizar si es el primer segundo
                        self.status_text.delete("end-2l", "end-1l")
                    self.log_message(f"Tiempo restante: {i} segundos")
                    time.sleep(1)
        
        self.is_running = False
        self.log_message("Proceso completado")
        self.update_button_states()
    
    def start_search(self):
        """Inicia la búsqueda en un hilo separado"""
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.pause_event.set()
            self.log_message("Iniciando proceso de búsqueda...")
            self.log_message(f"Tiempo de espera entre ejecuciones: {self.delay_time.get()} segundos")
            
            # Iniciar el hilo para ejecutar los bucles
            self.thread = threading.Thread(target=self.run_loops)
            self.thread.daemon = True
            self.thread.start()
            
            self.update_button_states()
    
    def pause_search(self):
        """Pausa o reanuda la búsqueda"""
        if self.is_paused:
            self.is_paused = False
            self.pause_event.set()
            self.log_message("Búsqueda reanudada")
            self.pause_button.config(text="Pausar")
        else:
            self.is_paused = True
            self.pause_event.clear()
            self.log_message("Búsqueda pausada")
            self.pause_button.config(text="Reanudar")
    
    def stop_search(self):
        """Detiene la búsqueda"""
        self.is_running = False
        self.is_paused = False
        self.pause_event.set()  # Liberar la pausa si estaba activa
        self.log_message("Proceso detenido")
        self.update_button_states()
    
    def update_button_states(self):
        """Actualiza el estado de los botones según el estado actual"""
        if self.is_running:
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
        else:
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.DISABLED)
            self.pause_button.config(text="Pausar")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageSearchApp(root)
    root.mainloop()