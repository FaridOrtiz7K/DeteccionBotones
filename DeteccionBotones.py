import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import pyautogui
import cv2
import numpy as np
import keyboard  # Necesitarás instalar: pip install keyboard

class ImageSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Búsqueda de Imágenes Automatizada")
        
        # Variables de control
        self.is_running = False
        self.is_paused = False
        self.pause_event = threading.Event()
        self.lote_inicial = tk.IntVar(value=1)
        self.lote_final = tk.IntVar(value=256)
        self.distrito = tk.StringVar(value="")
        self.delay_time = tk.DoubleVar(value=2.5)  # Tiempo de espera entre acciones
        self.current_lote = 0
        self.lotes_faltantes = 0
        self.image_paths = [
            "image1.png", "image2.png", "image3.png", 
            "image4.png", "image5.png", "image6.png"
        ]
        
        # Crear interfaz
        self.create_widgets()
        
        # Configurar tecla ESC para pausar
        keyboard.on_press_key("esc", self.pause_with_esc)
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuración de distrito y lote
        config_frame = ttk.LabelFrame(main_frame, text="Configuración de Distrito y Lote", padding="5")
        config_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(config_frame, text="Distrito:").grid(row=0, column=0, sticky=tk.W, padx=5)
        distrito_entry = ttk.Entry(config_frame, textvariable=self.distrito, width=20)
        distrito_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(config_frame, text="Lote Inicial:").grid(row=1, column=0, sticky=tk.W, padx=5)
        lote_inicial_spin = ttk.Spinbox(config_frame, from_=1, to=9999, textvariable=self.lote_inicial, width=10)
        lote_inicial_spin.grid(row=1, column=1, padx=5)
        
        ttk.Label(config_frame, text="Lote Final:").grid(row=1, column=2, sticky=tk.W, padx=5)
        lote_final_spin = ttk.Spinbox(config_frame, from_=1, to=9999, textvariable=self.lote_final, width=10)
        lote_final_spin.grid(row=1, column=3, padx=5)
        
        ttk.Label(config_frame, text="Tiempo entre acciones (segundos):").grid(row=2, column=0, sticky=tk.W, padx=5)
        delay_spin = ttk.Spinbox(config_frame, from_=0.5, to=10.0, increment=0.5, textvariable=self.delay_time, width=5)
        delay_spin.grid(row=2, column=1, padx=5)
        
        # Información de formato
        info_frame = ttk.LabelFrame(main_frame, text="Formatos de Lote", padding="5")
        info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        info_text = tk.Text(info_frame, height=3, width=50)
        info_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        info_text.insert(tk.END, "1. Distrito: 'ABC0001FO' → Lote: 'ABC0001FO_LT1.KML'\n2. Distrito: 'NINUGO' → Lote: 'LT1.KML'")
        info_text.config(state=tk.DISABLED)
        
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
        
    def get_lote_name(self, lote_number):
        """Genera el nombre del lote según el formato especificado"""
        distrito = self.distrito.get().strip()
        
        if distrito == "NINUGO":
            return f"LT{lote_number}.KML"
        else:
            return f"{distrito}_LT{lote_number}.KML"
        
    def search_image(self, image_path):
        """Función que busca una imagen específica y realiza clic si la encuentra"""
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
                return False
                
        except Exception as e:
            self.log_message(f"Error durante la búsqueda: {str(e)}")
            return False
    
    def process_lote(self, lote_number):
        """Procesa un lote específico buscando todos los botones"""
        lote_name = self.get_lote_name(lote_number)
        self.log_message(f"Procesando lote: {lote_name}")
        
        # Buscar y hacer clic en los 6 botones
        for i, image_path in enumerate(self.image_paths, 1):
            if not self.is_running:
                break
                
            if self.is_paused:
                self.pause_event.wait()
                if not self.is_running:
                    break
                    
            self.log_message(f"Buscando botón {i} de 6")
            success = self.search_image(image_path)
            
            if success:
                self.log_message(f"Botón {i} presionado correctamente")
                time.sleep(self.delay_time.get())  # Esperar entre acciones
            else:
                self.log_message(f"No se encontró el botón {i}, reintentando...")
                # Reintentar después de un breve tiempo
                time.sleep(1)
                
    def run_loops(self):
        """Ejecuta los bucles de búsqueda"""
        lote_inicial = self.lote_inicial.get()
        lote_final = self.lote_final.get()
        self.current_lote = lote_inicial - 1  # Se incrementará al inicio del bucle
        
        if not self.distrito.get().strip():
            self.log_message("Error: Debe especificar un distrito")
            self.is_running = False
            self.update_button_states()
            return
            
        if lote_inicial > lote_final:
            self.log_message("Error: El lote inicial debe ser menor o igual al lote final")
            self.is_running = False
            self.update_button_states()
            return
            
        while self.current_lote < lote_final and self.is_running:
            # Verificar si está pausado
            if self.is_paused:
                self.pause_event.wait()
                if not self.is_running:  # Verificar si se detuvo durante la pausa
                    break
            
            self.current_lote += 1
            self.lotes_faltantes = lote_final - self.current_lote
            self.log_message(f"Procesando lote {self.current_lote} de {lote_final}")
            
            # Procesar el lote actual
            self.process_lote(self.current_lote)
            
            # Mostrar progreso
            self.log_message(f"Lote {self.current_lote} completado. Lotres faltantes: {self.lotes_faltantes}")
        
        self.is_running = False
        self.log_message("Proceso completado")
        self.update_button_states()
    
    def pause_with_esc(self, event=None):
        """Maneja la pausa con la tecla ESC"""
        if self.is_running and not self.is_paused:
            self.pause_search()
            self.show_pause_window()
    
    def show_pause_window(self):
        """Muestra la ventana de pausa con información"""
        pause_window = tk.Toplevel(self.root)
        pause_window.title("Proceso Pausado")
        pause_window.geometry("300x200")
        pause_window.resizable(False, False)
        pause_window.transient(self.root)
        pause_window.grab_set()
        
        # Centrar la ventana
        pause_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (pause_window.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (pause_window.winfo_height() // 2)
        pause_window.geometry(f"+{x}+{y}")
        
        # Frame principal
        main_frame = ttk.Frame(pause_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Información
        ttk.Label(main_frame, text="Proceso Pausado", font=("Arial", 12, "bold")).pack(pady=5)
        ttk.Label(main_frame, text=f"Lote actual: {self.current_lote}").pack(pady=2)
        ttk.Label(main_frame, text=f"Lotes faltantes: {self.lotes_faltantes}").pack(pady=2)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        def resume_with_countdown():
            """Reanuda con cuenta regresiva de 5 segundos"""
            countdown_window = tk.Toplevel(pause_window)
            countdown_window.title("Reanudando")
            countdown_window.geometry("200x100")
            countdown_window.resizable(False, False)
            countdown_window.transient(pause_window)
            countdown_window.grab_set()
            
            # Centrar la ventana
            countdown_window.update_idletasks()
            x = pause_window.winfo_x() + (pause_window.winfo_width() // 2) - (countdown_window.winfo_width() // 2)
            y = pause_window.winfo_y() + (pause_window.winfo_height() // 2) - (countdown_window.winfo_height() // 2)
            countdown_window.geometry(f"+{x}+{y}")
            
            countdown_label = ttk.Label(countdown_window, text="Reanudando en 5", font=("Arial", 14))
            countdown_label.pack(expand=True)
            
            def update_countdown(seconds):
                if seconds > 0:
                    countdown_label.config(text=f"Reanudando en {seconds}")
                    countdown_window.after(1000, update_countdown, seconds-1)
                else:
                    countdown_window.destroy()
                    pause_window.destroy()
                    self.pause_search()  # Reanudar el proceso
            
            update_countdown(5)
        
        ttk.Button(button_frame, text="Reanudar", command=resume_with_countdown).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Salir", command=self.stop_and_exit).grid(row=0, column=1, padx=5)
        
        # Hacer que la ventana sea modal
        pause_window.wait_window()
    
    def stop_and_exit(self):
        """Detiene el proceso y cierra la aplicación"""
        self.stop_search()
        self.root.quit()
        self.root.destroy()
    
    def start_search(self):
        """Inicia la búsqueda en un hilo separado"""
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.pause_event.set()
            self.log_message("Iniciando proceso de búsqueda...")
            self.log_message(f"Distrito: {self.distrito.get()}")
            self.log_message(f"Rango de lotes: {self.lote_inicial.get()} a {self.lote_final.get()}")
            self.log_message(f"Tiempo entre acciones: {self.delay_time.get()} segundos")
            
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