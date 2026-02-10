import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import base64
import sys
import calendar
from datetime import datetime, date
import tkcalendar 

# --- IMPORTACIÓN DE MÓDULOS DE LÓGICA ---
# Se asume que los scripts están en carpetas separadas para evitar conflictos de nombres
try:
    from ecopetrol import main as main_ecopetrol
    from gecelca import main as main_gecelca
except ImportError as e:
    print(f"Error de importación: {e}")
    print("Asegúrate de tener las carpetas 'ecopetrol' y 'gecelca' con sus respectivos archivos main.py e __init__.py")
    # Mocks para que la GUI abra aunque falten archivos (para desarrollo)
    main_ecopetrol = None
    main_gecelca = None

def resource_path(relative_path):
    """
    Obtiene la ruta absoluta del recurso, funciona para desarrollo y para PyInstaller.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Configuración de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class FacturaProcessorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Procesador Unificado de Facturas")
        self.geometry("510x680") # Aumenté un poco la altura para acomodar el nuevo control
        
        # Variables para almacenar las selecciones del usuario
        self.has_selection = False
        self.selected_path = ""
        self.output_path = ""
        self.export_excel = True
        self.selected_date = None
        self.is_processing = False
        
        self.status_var = ctk.StringVar()
        
        # Crear el contenedor principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Título con logo
        self.title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.title_frame.grid(row=0, column=0, padx=15, pady=(15, 20), sticky="ew")
        self.title_frame.grid_columnconfigure(1, weight=1)
        
        self.load_and_display_logo()
        
        self.title_label = ctk.CTkLabel(
            self.title_frame, 
            text="Procesador de Facturas",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=1, sticky="w")
        
        # Sección de selección de archivos
        self.selection_frame = ctk.CTkFrame(self.main_frame)
        self.selection_frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        self.selection_frame.grid_columnconfigure(0, weight=1)
        self.selection_frame.grid_columnconfigure(1, weight=1)
        
        self.folder_button = ctk.CTkButton(
            self.selection_frame,
            text="Seleccionar carpeta",
            command=self.select_folder,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#3a7ebf",
            hover_color="#2b5d8b"
        )
        self.folder_button.grid(row=0, column=0, padx=(15, 8), pady=15, sticky="ew")
        
        self.pdf_button = ctk.CTkButton(
            self.selection_frame,
            text="Seleccionar archivo PDF",
            command=self.select_pdf,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#3a7ebf",
            hover_color="#2b5d8b"
        )
        self.pdf_button.grid(row=0, column=1, padx=(8, 15), pady=15, sticky="ew")
        
        # Mostrar ruta seleccionada
        self.path_frame = ctk.CTkFrame(self.main_frame)
        self.path_frame.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="ew")
        self.path_frame.grid_columnconfigure(0, weight=1)
        
        self.path_label_title = ctk.CTkLabel(
            self.path_frame,
            text="Ruta seleccionada:",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        self.path_label_title.grid(row=0, column=0, padx=15, pady=(10, 3), sticky="w")
        
        self.path_var = ctk.StringVar()
        self.path_var.set("No hay un archivo o carpeta seleccionada")
        
        self.path_label = ctk.CTkLabel(
            self.path_frame, 
            textvariable=self.path_var,
            wraplength=450,
            font=ctk.CTkFont(size=11),
            anchor="w",
            justify="left"
        )
        self.path_label.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")

        # Contenedor de los dos frames (calendar + opciones)
        self.row_frame = ctk.CTkFrame(self.main_frame) 
        self.row_frame.grid(row=3, column=0, padx=5, pady=(0, 15), sticky="ew")
        self.row_frame.grid_columnconfigure(0, weight=1)
        self.row_frame.grid_columnconfigure(1, weight=1)
        self.row_frame.grid_rowconfigure(0, weight=1)

        # --------- Frame de Fecha de consulta (calendar_frame) ---------
        self.calendar_frame = ctk.CTkFrame(self.row_frame)
        self.calendar_frame.grid(row=0, column=0, padx=5, pady=(10, 15), sticky="nsew")
        self.calendar_frame.grid_columnconfigure(0, weight=1)

        self.calendar_label = ctk.CTkLabel(
            self.calendar_frame,
            text="Fecha de consulta",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="center"
        )
        self.calendar_label.grid(row=0, column=0, padx=15, pady=(10, 3), sticky="ew")

        self.calendar_button = ctk.CTkButton(
            self.calendar_frame,
            text="Seleccionar fecha",
            command=self.select_date,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color="#3a7ebf",
            hover_color="#2b5d8b",
            anchor="center"
        )
        self.calendar_button.grid(row=1, column=0, padx=15, pady=(0, 5), sticky="ew")

        self.date_var = ctk.StringVar()
        self.date_var.set("No hay fecha seleccionada")

        self.date_label = ctk.CTkLabel(
            self.calendar_frame,
            textvariable=self.date_var,
            font=ctk.CTkFont(size=11),
            anchor="center"
        )
        self.date_label.grid(row=2, column=0, padx=15, pady=(0, 10), sticky="ew")

        # --------- Frame de Opciones (options_frame) ---------
        self.options_frame = ctk.CTkFrame(self.row_frame)
        self.options_frame.grid(row=0, column=1, padx=5, pady=(10, 15), sticky="nsew")
        self.options_frame.grid_columnconfigure(0, weight=1)

        self.options_label = ctk.CTkLabel(
            self.options_frame,
            text="Configuración",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="center"
        )
        self.options_label.grid(row=0, column=0, padx=5, pady=(10, 3), sticky="ew")

        # --- NUEVO DROPDOWN PARA TIPO DE PROCESADOR ---
        self.processor_type_label = ctk.CTkLabel(
            self.options_frame,
            text="Tipo de Factura:",
            font=ctk.CTkFont(size=11),
            anchor="center"
        )
        self.processor_type_label.grid(row=1, column=0, padx=5, pady=(5, 0), sticky="ew")

        self.processor_combobox = ctk.CTkOptionMenu(
            self.options_frame,
            values=["Ecopetrol", "Gecelca/XM"],
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color="#3a7ebf",
            button_color="#2b5d8b",
            button_hover_color="#204a70"
        )
        self.processor_combobox.grid(row=2, column=0, padx=15, pady=(0, 10), sticky="ew")
        self.processor_combobox.set("Ecopetrol") # Valor por defecto

        # Sub-frame para botón y texto de carpeta de salida
        self.output_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.output_frame.grid(row=3, column=0, padx=5, pady=(0, 10), sticky="ew")
        self.output_frame.grid_columnconfigure(0, weight=1)

        self.output_button = ctk.CTkButton(
            self.output_frame,
            text="Carpeta de salida",
            command=self.select_output_folder,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color="#3a7ebf",
            hover_color="#2b5d8b",
            anchor="center"
        )
        self.output_button.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="ew")

        self.output_var = ctk.StringVar()
        self.output_var.set("Usar carpeta predeterminada")

        self.output_label = ctk.CTkLabel(
            self.output_frame,
            textvariable=self.output_var,
            wraplength=200,
            font=ctk.CTkFont(size=10),
            anchor="center"
        )
        self.output_label.grid(row=1, column=0, padx=0, pady=0, sticky="ew")

        # Área de estado y progreso
        self.status_frame = ctk.CTkFrame(self.main_frame)
        self.status_frame.grid(row=4, column=0, padx=15, pady=(0, 10), sticky="ew")
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label_title = ctk.CTkLabel(
            self.status_frame,
            text="Estado:",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        self.status_label_title.grid(row=0, column=0, padx=15, pady=(5, 3), sticky="w")
        
        self.status_text = ctk.StringVar()
        self.status_text.set("Listo para procesar")
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            textvariable=self.status_text,
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        self.status_label.grid(row=1, column=0, padx=15, pady=(0, 2), sticky="w")
        
        self.spinner_text = ctk.StringVar()
        self.spinner_text.set("")
        self.spinner_label = ctk.CTkLabel(
            self.status_frame,
            textvariable=self.spinner_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="center"
        )
        self.spinner_label.grid(row=2, column=0, padx=15, pady=(0, 2), sticky="ew")
        
        # Botones de acción
        self.action_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.action_frame.grid(row=5, column=0, padx=15, pady=(5, 15), sticky="ew")
        self.action_frame.grid_columnconfigure(0, weight=1)
        
        self.theme_frame = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        self.theme_frame.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        
        self.theme_label = ctk.CTkLabel(
            self.theme_frame,
            text="Tema:",
            font=ctk.CTkFont(size=12),
        )
        self.theme_label.grid(row=0, column=0, padx=(0, 8))
        
        self.theme_option = ctk.CTkOptionMenu(
            self.theme_frame,
            values=["Oscuro", "Claro"],
            command=self.change_appearance_mode,
            width=100,
            height=28,
            font=ctk.CTkFont(size=11)
        )
        self.theme_option.grid(row=0, column=1)
        self.theme_option.set("Oscuro")
        
        self.cancel_button = ctk.CTkButton(
            self.action_frame,
            text="Salir",
            command=self.destroy,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        self.cancel_button.grid(row=0, column=1, padx=(0, 8), pady=5)
        
        self.process_button = ctk.CTkButton(
            self.action_frame,
            text="Procesar",
            command=self.process_selection,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.process_button.grid(row=0, column=2, padx=(0, 0), pady=5)
        self.process_button.configure(state="disabled")
    
    def load_and_display_logo(self):
        # (Aquí iría el código de carga de logo original, se mantiene igual)
        # Para simplificar el ejemplo, uso texto si no hay imagen
        self._show_text_logo()

    def _show_text_logo(self):
        # Método auxiliar fallback
        pass

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_path = folder
            self.path_var.set(folder)
            self.process_button.configure(state="normal")
            # Inferencia inteligente: si hay muchos PDFs, sugerir Gecelca, etc. (opcional)
    
    def select_pdf(self):
        filetypes = [("PDF files", "*.pdf")]
        file = filedialog.askopenfilename(filetypes=filetypes)
        if file:
            self.selected_path = file
            self.path_var.set(file)
            self.process_button.configure(state="normal")
    
    def select_date(self):
        top = ctk.CTkToplevel(self)
        top.geometry("300x280")
        cal = tkcalendar.Calendar(top, selectmode='day')
        cal.pack(pady=20)
        
        def grabar_fecha():
            date_obj = cal.selection_get()
            self.selected_date = date_obj.strftime("%Y-%m-%d")  
            self.date_var.set(date_obj.strftime("%d/%m/%Y"))
            top.destroy()
        
        select_btn = ctk.CTkButton(top, text="Seleccionar", command=grabar_fecha)
        select_btn.pack(pady=10)
    
    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_path = folder
            self.output_var.set(folder)
    
    def change_appearance_mode(self, new_mode):
        ctk.set_appearance_mode("dark" if new_mode == "Oscuro" else "light")
    
    def process_selection(self):
        self.status_text.set("Procesando...")
        self.is_processing = True
        self.process_button.configure(state="disabled")
        threading.Thread(target=self.run_processing, daemon=True).start()
    
    def run_processing(self):
        try:
            tipo_procesador = self.processor_combobox.get()
            is_directory = os.path.isdir(self.selected_path)
            
            if tipo_procesador == "Ecopetrol":
                if not main_ecopetrol:
                    raise Exception("El módulo de Ecopetrol no se pudo cargar.")
                
                if is_directory:
                    main_ecopetrol.procesar_directorio(
                        self.selected_path, 
                        self.output_path, 
                        self.selected_date
                    )
                else:
                    main_ecopetrol.procesar_factura(
                        self.selected_path, 
                        self.output_path, 
                        exportar_excel=True, 
                        fecha_seleccionada=self.selected_date
                    )
                    
            elif tipo_procesador == "Gecelca/XM":
                if not main_gecelca:
                    raise Exception("El módulo de Gecelca no se pudo cargar.")
                
                # Adaptador para las llamadas de función de Gecelca que varían ligeramente
                if is_directory:
                    # Gecelca main.py usa 'procesar_directorio_consolidado'
                    main_gecelca.procesar_directorio_consolidado(
                        self.selected_path, 
                        self.output_path
                    )
                else:
                    # Gecelca main.py usa 'procesar_individual' o 'procesar_pdf_a_datos'
                    # Usamos el wrapper 'procesar_individual' que exporta a Excel
                    main_gecelca.procesar_individual(
                        self.selected_path, 
                        self.output_path
                    )
                    
            self.status_text.set("Procesamiento completado con éxito")
            messagebox.showinfo("Éxito", f"El procesamiento de {tipo_procesador} finalizó correctamente.")
            
        except Exception as e:
            self.status_text.set("Error durante el procesamiento")
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")
            print(e)
        finally:
            self.is_processing = False
            self.process_button.configure(state="normal")

if __name__ == "__main__":
    app = FacturaProcessorGUI()
    app.mainloop()