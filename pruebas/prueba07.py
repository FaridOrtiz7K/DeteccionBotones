import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import pyautogui
import cv2
import numpy as np
from PIL import Image, ImageTk
import keyboard  # Necesitarás instalar: pip install keyboard
import os
import json

# -------------------- CONFIGURACIÓN --------------------
CONFIG_FILE = "config.json"
DEFAULT_CREDENTIALS = {
    "username": "admin",
    "password": "password123"
}

# -------------------- MODELO --------------------
class ImageSearchModel:
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.pause_event = threading.Event()
        self.lote_inicial = 1
        self.lote_final = 1
        self.distrito = ""
        self.delay_time = 2
        self.current_lote = 0
        self.observers = []
        self.alt_n_used = False  # Para controlar si ya se usó Alt+N en este lote
        
        # Secuencia predefinida de imágenes
        self.image_sequence = [
            ("img/b1.png", 2, 0.7),
            ("img/b2.png", 1, 0.7),
            ("img/b3.png", 1, 0.7),
            ("img/b4.png", 2, 0.7),
            ("img/b5.png", 1, 0.7),
            ("img/b6.png", 1, 0.7)
        ]
        
        # Cargar estado guardado si existe
        self.load_state()
    
    def load_state(self):
        """Carga el estado guardado desde el archivo de configuración"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.lote_inicial = config.get('lote_inicial', 1)
                    self.lote_final = config.get('lote_final', 1)
                    self.distrito = config.get('distrito', "")
                    self.delay_time = config.get('delay_time', 2)
                    self.current_lote = config.get('current_lote', 0)
        except Exception as e:
            print(f"Error al cargar configuración: {e}")
    
    def save_state(self):
        """Guarda el estado actual en el archivo de configuración"""
        try:
            config = {
                'lote_inicial': self.lote_inicial,
                'lote_final': self.lote_final,
                'distrito': self.distrito,
                'delay_time': self.delay_time,
                'current_lote': self.current_lote
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error al guardar configuración: {e}")
    
    def add_observer(self, observer):
        self.observers.append(observer)
    
    def notify_observers(self, event, data=None):
        for observer in self.observers:
            observer.update(event, data)
    
    def set_running(self, running):
        self.is_running = running
        self.notify_observers("running_changed", running)
        if not running:
            self.save_state()
    
    def set_paused(self, paused):
        self.is_paused = paused
        self.notify_observers("paused_changed", paused)
        if paused:
            self.save_state()
    
    def set_lote_inicial(self, lote):
        self.lote_inicial = lote
        self.notify_observers("lote_inicial_changed", lote)
        self.save_state()
    
    def set_lote_final(self, lote):
        self.lote_final = lote
        self.notify_observers("lote_final_changed", lote)
        self.save_state()
    
    def set_distrito(self, distrito):
        self.distrito = distrito
        self.notify_observers("distrito_changed", distrito)
        self.save_state()
    
    def set_delay_time(self, time):
        self.delay_time = time
        self.notify_observers("delay_time_changed", time)
        self.save_state()
    
    def set_current_lote(self, lote):
        self.current_lote = lote
        self.notify_observers("current_lote_changed", lote)
        self.save_state()
    
    def click_button(self, imagen, clicks=1, confianza_minima=0.6, max_intentos=10):
        """
        Busca un botón en pantalla y hace clic en él
        
        Args:
            imagen (str): Ruta de la imagen del botón a buscar
            clicks (int): Número de clics a realizar
            confianza_minima (float): Umbral de confianza para la detección (0-1)
            max_intentos (int): Número máximo de intentos para encontrar el botón
        
        Returns:
            bool: True si encontró el botón, False en caso contrario
        """
        intentos = 0
        while intentos < max_intentos and self.is_running:
            # Verificar si está pausado
            if self.is_paused:
                self.pause_event.wait()
                if not self.is_running:
                    return False
            
            # Obtener dimensiones de la pantalla
            ancho_pantalla, alto_pantalla = pyautogui.size()
            vm_region = (0, 0, ancho_pantalla, alto_pantalla)

            # Capturar pantalla
            screenshot = pyautogui.screenshot(region=vm_region)
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            # Cargar template
            template = cv2.imread(imagen)
            if template is None:
                self.notify_observers("error", f"No se pudo cargar la imagen '{imagen}'. Verifica la ruta y el formato.")
                return False

            h, w = template.shape[:2]

            # Buscar el botón
            result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val > confianza_minima:
                # Calcular centro del botón
                center_x = vm_region[0] + max_loc[0] + w//2
                center_y = vm_region[1] + max_loc[1] + h//2
                
                # Esperar 2.5 segundos antes de hacer clic
                time.sleep(2.5)
                
                # Realizar clic
                pyautogui.moveTo(center_x, center_y)
                pyautogui.click(clicks=clicks)
                
                self.notify_observers("image_found", {
                    "image": imagen,
                    "x": center_x,
                    "y": center_y,
                    "confidence": max_val
                })
                return True
            else:
                intentos += 1
                self.notify_observers("image_not_found", {
                    "image": imagen,
                    "confidence": max_val,
                    "intento": intentos
                })
                # Esperar un poco antes de intentar nuevamente
                time.sleep(1)
        
        return False


# -------------------- VISTA --------------------
class LoginWindow(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.title("Inicio de Sesión")
        self.geometry("300x200")
        self.resizable(False, False)
        
        # Centrar la ventana
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        # Hacer la ventana modal
        self.transient(parent)
        self.grab_set()
        
        # Intentar cargar el icono
        try:
            self.iconbitmap("icon.ico")
        except:
            pass
        
        # Variables
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        
        # Crear widgets
        self.create_widgets()
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Logo o título
        ttk.Label(main_frame, text="Sistema Automatizado", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Campos de usuario y contraseña
        ttk.Label(main_frame, text="Usuario:").grid(row=1, column=0, sticky=tk.W, pady=5)
        username_entry = ttk.Entry(main_frame, textvariable=self.username_var, width=20)
        username_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(main_frame, text="Contraseña:").grid(row=2, column=0, sticky=tk.W, pady=5)
        password_entry = ttk.Entry(main_frame, textvariable=self.password_var, show="*", width=20)
        password_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Ingresar", command=self.authenticate).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Salir", command=self.quit_app).grid(row=0, column=1, padx=5)
        
        # Configurar expansión
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Enlazar tecla Enter para autenticar
        self.bind('<Return>', lambda e: self.authenticate())
    
    def authenticate(self):
        """Verifica las credenciales del usuario"""
        username = self.username_var.get()
        password = self.password_var.get()
        
        if username == DEFAULT_CREDENTIALS["username"] and password == DEFAULT_CREDENTIALS["password"]:
            self.destroy()
            self.controller.show_main_window()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
    
    def quit_app(self):
        """Cierra la aplicación"""
        self.controller.root.quit()


class PauseWindow(tk.Toplevel):
    def __init__(self, parent, controller, current_lote, total_lotes):
        super().__init__(parent)
        self.controller = controller
        self.title("Proceso en Pausa")
        self.geometry("300x200")
        self.resizable(False, False)
        
        # Intentar cargar el icono
        try:
            self.iconbitmap("icon.ico")
        except:
            pass
        
        # Hacer la ventana modal
        self.transient(parent)
        self.grab_set()
        
        # Centrar la ventana
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        # Configurar el protocolo de cierre
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Variables
        self.countdown = 5
        self.countdown_running = False
        
        # Crear widgets
        self.create_widgets(current_lote, total_lotes)
    
    def create_widgets(self, current_lote, total_lotes):
        # Frame principal
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Información de progreso
        lotes_faltantes = total_lotes - current_lote
        ttk.Label(main_frame, text=f"Lote actual: {current_lote}").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text=f"Lotes completados: {current_lote - 1}").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text=f"Lotes faltantes: {lotes_faltantes}").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text=f"Total de lotes: {total_lotes}").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, pady=10)
        
        self.resume_button = ttk.Button(button_frame, text="Reanudar (5)", 
                                       command=self.start_countdown)
        self.resume_button.grid(row=0, column=0, padx=5)
        
        self.exit_button = ttk.Button(button_frame, text="Salir", 
                                     command=self.controller.stop_search)
        self.exit_button.grid(row=0, column=1, padx=5)
        
        # Configurar expansión
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
    
    def start_countdown(self):
        """Inicia la cuenta regresiva para reanudar"""
        if not self.countdown_running:
            self.countdown_running = True
            self.resume_button.config(state=tk.DISABLED)
            self.update_countdown()
    
    def update_countdown(self):
        """Actualiza la cuenta regresiva"""
        if self.countdown > 0 and self.countdown_running:
            self.resume_button.config(text=f"Reanudar ({self.countdown})")
            self.countdown -= 1
            self.after(1000, self.update_countdown)
        elif self.countdown_running:
            self.controller.pause_search()  # Reanudar
            self.destroy()
    
    def on_close(self):
        """Maneja el cierre de la ventana"""
        self.countdown_running = False
        self.destroy()


class ImageSearchView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding="10")
        self.controller = controller
        self.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Variables para los controles
        self.lote_inicial_var = tk.IntVar(value=self.controller.model.lote_inicial)
        self.lote_final_var = tk.IntVar(value=self.controller.model.lote_final)
        self.distrito_var = tk.StringVar(value=self.controller.model.distrito)
        self.delay_time_var = tk.IntVar(value=self.controller.model.delay_time)
        
        self.create_widgets()
    
    def create_widgets(self):
        # Configuración de distrito
        distrito_frame = ttk.LabelFrame(self, text="Configuración de Distrito", padding="5")
        distrito_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(distrito_frame, text="Distrito:").grid(row=0, column=0, sticky=tk.W, padx=5)
        distrito_entry = ttk.Entry(distrito_frame, textvariable=self.distrito_var, width=20)
        distrito_entry.grid(row=0, column=1, padx=5)
        distrito_entry.bind("<FocusOut>", lambda e: self.controller.update_distrito(self.distrito_var.get()))
        
        # Configuración de lotes
        lote_frame = ttk.LabelFrame(self, text="Configuración de Lotes", padding="5")
        lote_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(lote_frame, text="Lote inicial:").grid(row=0, column=0, sticky=tk.W, padx=5)
        lote_inicial_spin = ttk.Spinbox(lote_frame, from_=1, to=1000, textvariable=self.lote_inicial_var, width=10)
        lote_inicial_spin.grid(row=0, column=1, padx=5)
        lote_inicial_spin.bind("<FocusOut>", lambda e: self.controller.update_lote_inicial(self.lote_inicial_var.get()))
        
        ttk.Label(lote_frame, text="Lote final:").grid(row=0, column=2, sticky=tk.W, padx=5)
        lote_final_spin = ttk.Spinbox(lote_frame, from_=1, to=1000, textvariable=self.lote_final_var, width=10)
        lote_final_spin.grid(row=0, column=3, padx=5)
        lote_final_spin.bind("<FocusOut>", lambda e: self.controller.update_lote_final(self.lote_final_var.get()))
        
        ttk.Label(lote_frame, text="Tiempo de espera (segundos):").grid(row=0, column=4, sticky=tk.W, padx=5)
        delay_spin = ttk.Spinbox(lote_frame, from_=1, to=60, textvariable=self.delay_time_var, width=5)
        delay_spin.grid(row=0, column=5, padx=5)
        delay_spin.bind("<FocusOut>", lambda e: self.controller.update_delay_time(self.delay_time_var.get()))
        
        # Información de secuencia predefinida
        sequence_frame = ttk.LabelFrame(self, text="Secuencia Predefinida", padding="5")
        sequence_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Mostrar la secuencia predefinida
        sequence_text = "Secuencia predefinida:\n"
        for i, (imagen, clicks, confianza) in enumerate(self.controller.model.image_sequence, 1):
            sequence_text += f"{i}. {imagen} (clics: {clicks}, confianza: {confianza})\n"
        
        ttk.Label(sequence_frame, text=sequence_text).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Botones de control
        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Iniciar", command=self.controller.start_search)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.pause_button = ttk.Button(button_frame, text="Pausar", command=self.controller.pause_search, state=tk.DISABLED)
        self.pause_button.grid(row=0, column=1, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Detener", command=self.controller.stop_search, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=2, padx=5)
        
        # Área de estado
        status_frame = ttk.LabelFrame(self, text="Estado", padding="5")
        status_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=10, width=70)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Configurar expansión de columnas
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        sequence_frame.columnconfigure(0, weight=1)
        status_frame.columnconfigure(0, weight=1)
    
    def log_message(self, message):
        """Añade un mensaje al área de estado"""
        self.status_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.status_text.see(tk.END)
    
    def update_button_states(self, is_running, is_paused):
        """Actualiza el estado de los botones según el estado actual"""
        if is_running:
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
            self.pause_button.config(text="Reanudar" if is_paused else "Pausar")
        else:
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.DISABLED)
            self.pause_button.config(text="Pausar")
    
    def show_pause_window(self, current_lote, total_lotes):
        """Muestra la ventana de pausa"""
        PauseWindow(self.master, self.controller, current_lote, total_lotes)


# -------------------- CONTROLADOR --------------------
class ImageSearchController:
    def __init__(self, root):
        self.model = ImageSearchModel()
        self.root = root
        self.view = None
        self.pause_window = None
        self.authenticated = False
        
        # Configurar tecla ESC para pausar
        keyboard.on_press_key("esc", lambda e: self.pause_search())
        
        # Mostrar ventana de login
        self.show_login_window()
    
    def show_login_window(self):
        """Muestra la ventana de login"""
        self.login_window = LoginWindow(self.root, self)
    
    def show_main_window(self):
        """Muestra la ventana principal después del login exitoso"""
        self.authenticated = True
        self.view = ImageSearchView(self.root, self)
        self.model.add_observer(self)
        
        # Inicializar la vista con los valores del modelo
        self.view.lote_inicial_var.set(self.model.lote_inicial)
        self.view.lote_final_var.set(self.model.lote_final)
        self.view.distrito_var.set(self.model.distrito)
        self.view.delay_time_var.set(self.model.delay_time)
    
    def update(self, event, data):
        """Método para recibir actualizaciones del modelo"""
        if not self.authenticated:
            return
            
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
    
    def update_lote_inicial(self, lote):
        self.model.set_lote_inicial(lote)
    
    def update_lote_final(self, lote):
        self.model.set_lote_final(lote)
    
    def update_distrito(self, distrito):
        self.model.set_distrito(distrito)
    
    def update_delay_time(self, time):
        self.model.set_delay_time(time)
    
    def handle_b4_special_behavior(self, imagen, clicks, confianza):
        """Maneja el comportamiento especial para la imagen b4"""
        # Para el primer lote, hacer clic normal en b4
        if self.model.current_lote == self.model.lote_inicial:
            return self.model.click_button(imagen, clicks, confianza, max_intentos=10)
        else:
            # Para lotes posteriores, usar Alt+N
            if not self.model.alt_n_used:
                self.view.log_message("Usando Alt+N para seleccionar siguiente elemento")
                pyautogui.hotkey('alt', 'n')
                self.model.alt_n_used = True
                time.sleep(1)  # Pequeña espera después de Alt+N
            return True
    
    def run_sequence(self):
        """Ejecuta la secuencia completa de imágenes"""
        for imagen, clicks, confianza in self.model.image_sequence:
            # Verificar si está pausado
            if self.model.is_paused:
                self.model.pause_event.wait()
                if not self.model.is_running:  # Verificar si se detuvo durante la pausa
                    return False
            
            # Manejar comportamiento especial para b4
            if "b4.png" in imagen:
                success = self.handle_b4_special_behavior(imagen, clicks, confianza)
            else:
                # Realizar la búsqueda y clic normal para otras imágenes
                success = self.model.click_button(imagen, clicks, confianza, max_intentos=10)
            
            if not success:
                self.view.log_message(f"Error: No se pudo encontrar el botón '{imagen}' después de 10 intentos")
                return False
            
            # Esperar 2 segundos entre imágenes (como en el ejemplo)
            if imagen != self.model.image_sequence[-1][0] and self.model.is_running:
                time.sleep(2)
        
        return True
    
    def run_lotes(self):
        """Ejecuta los lotes de búsqueda"""
        current_lote = self.model.lote_inicial
        lote_final = self.model.lote_final
        
        while current_lote <= lote_final and self.model.is_running:
            # Reiniciar flag de Alt+N para cada lote
            self.model.alt_n_used = False
            
            # Verificar si está pausado
            if self.model.is_paused:
                self.model.pause_event.wait()
                if not self.model.is_running:  # Verificar si se detuvo durante la pausa
                    break
            
            self.model.set_current_lote(current_lote)
            
            # Generar nombre de archivo según el distrito
            if self.model.distrito == "NINUGO":
                nombre_archivo = f"LT{current_lote}.KML"
            else:
                nombre_archivo = f"{self.model.distrito}_LT{current_lote}.KML"
            
            self.view.log_message(f"Procesando archivo: {nombre_archivo}")
            
            # Realizar la secuencia completa
            success = self.run_sequence()
            
            if success:
                # Presionar Enter 3 veces después de cada secuencia
                self.view.log_message("Presionando Enter 3 veces")
                pyautogui.press('enter', presses=3, interval=0.25)
                
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
                        self.model.pause_event.wait()
                        if not self.model.is_running:
                            break
                    # Actualizar el mensaje cada segundo
                    if i != self.model.delay_time:  # No actualizar si es el primer segundo
                        self.view.status_text.delete("end-2l", "end-1l")
                    self.view.log_message(f"Tiempo restante: {i} segundos")
                    time.sleep(1)
        
        self.model.set_running(False)
        self.view.log_message("Proceso completado")
    
    def start_search(self):
        """Inicia la búsqueda en un hilo separado"""
        if not self.authenticated:
            messagebox.showerror("Error", "Debe iniciar sesión primero.")
            return
            
        # Validar que el distrito no esté vacío
        if not self.model.distrito:
            messagebox.showerror("Error", "Debe ingresar un distrito.")
            return
            
        # Validar que el lote inicial no sea mayor al lote final
        if self.model.lote_inicial > self.model.lote_final:
            messagebox.showerror("Error", "El lote inicial no puede ser mayor al lote final.")
            return
            
        if not self.model.is_running:
            self.model.set_running(True)
            self.model.set_paused(False)
            self.model.pause_event.set()
            self.view.log_message("Iniciando proceso de búsqueda...")
            self.view.log_message(f"Distrito: {self.model.distrito}")
            self.view.log_message(f"Lotes: {self.model.lote_inicial} a {self.model.lote_final}")
            self.view.log_message(f"Tiempo de espera entre lotes: {self.model.delay_time} segundos")
            
            # Mostrar la secuencia a ejecutar
            self.view.log_message("Secuencia predefinida a ejecutar:")
            for i, (imagen, clicks, confianza) in enumerate(self.model.image_sequence, 1):
                self.view.log_message(f"  {i}. {imagen} (clics: {clicks}, confianza: {confianza})")
            
            # Iniciar el hilo para ejecutar los lotes
            self.thread = threading.Thread(target=self.run_lotes)
            self.thread.daemon = True
            self.thread.start()
    
    def pause_search(self):
        """Pausa o reanuda la búsqueda"""
        if not self.authenticated:
            return
            
        if self.model.is_running:
            if self.model.is_paused:
                self.model.set_paused(False)
                self.model.pause_event.set()
                self.view.log_message("Búsqueda reanudada")
            else:
                self.model.set_paused(True)
                self.model.pause_event.clear()
                self.view.log_message("Búsqueda pausada (Presione ESC para reanudar)")
    
    def stop_search(self):
        """Detiene la búsqueda"""
        if not self.authenticated:
            return
            
        self.model.set_running(False)
        self.model.set_paused(False)
        self.model.pause_event.set()  # Liberar la pausa si estaba activa
        self.view.log_message("Proceso detenido")


# -------------------- APLICACIÓN PRINCIPAL --------------------
class ImageSearchApp:
    def __init__(self, root):
        # Intentar cargar el icono
        try:
            root.iconbitmap("icon.ico")
        except:
            pass
            
        self.controller = ImageSearchController(root)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Búsqueda de Imágenes Automatizada")
    root.withdraw()  # Ocultar ventana principal hasta que se autentique
    app = ImageSearchApp(root)
    root.mainloop()