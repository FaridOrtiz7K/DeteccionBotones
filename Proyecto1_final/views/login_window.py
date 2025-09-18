import tkinter as tk
from tkinter import ttk, messagebox
import logging
from utils.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class LoginWindow(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config_manager = ConfigManager()
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
        
        # Variables
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        
        # Crear widgets
        self.create_widgets()
        
        # Enfocar el campo de usuario
        self.after(100, lambda: self.focus_force())
    
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
        
        stored_username = self.config_manager.get("username", "admin")
        stored_password = self.config_manager.get("password", "123")
        
        if username == stored_username and password == stored_password:
            self.controller.authenticated = True
            self.destroy()
            self.controller.show_main_window()
            logger.info("Usuario autenticado correctamente")
        else:
            logger.warning("Intento de autenticación fallido")
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
    
    def quit_app(self):
        """Cierra la aplicación"""
        self.controller.root.quit()