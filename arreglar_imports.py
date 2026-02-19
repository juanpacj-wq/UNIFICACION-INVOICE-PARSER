import os
import re

carpetas_proyecto = ['ecopetrol', 'gecelca']

modulos_conocidos = [
    'extractores', 'extractores_pdf', 'extractores_patrones', 
    'extractores_componentes', 'procesamiento', 'exportacion', 
    'exportacion_excel', 'exportacion_batch', 'exportacion_excel_multiple',
    'utils', 'db_connector', 'db_connector_utils', 
    'db_connector_consultas', 'db_connector_comparacion',
    'main'
]

def obtener_indentacion(linea):
    """Devuelve el string de espacios al inicio de la línea."""
    return linea[:len(linea) - len(linea.lstrip())]

def arreglar_archivo(ruta_archivo):
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()

    lineas_modificadas = []
    cambios = False

    for linea in lineas:
        contenido = linea.strip()
        indent = obtener_indentacion(linea)
        nueva_linea = linea

        if contenido.startswith('from '):
            partes = contenido.split()
            if len(partes) >= 2:
                modulo = partes[1]
                if modulo in modulos_conocidos and not modulo.startswith('.'):
                    nueva_linea = linea.replace(f'from {modulo}', f'from .{modulo}', 1)
                    cambios = True
        
        elif contenido.startswith('import '):
            partes = contenido.split()
            modulo_raiz = partes[1].split('.')[0] 
            if modulo_raiz in modulos_conocidos:
                if ',' not in contenido:
                    if ' as ' in contenido:
                        alias = contenido.split(' as ')[1]
                        nueva_linea = f"{indent}from . import {modulo_raiz} as {alias}\n"
                    else:
                        nueva_linea = f"{indent}from . import {modulo_raiz}\n"
                    cambios = True

        lineas_modificadas.append(nueva_linea)

    if cambios:
        print(f"🔧 Reparando imports en: {ruta_archivo}")
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            f.writelines(lineas_modificadas)

def procesar_carpetas():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    print("Iniciando reparación de imports...")
    
    for carpeta in carpetas_proyecto:
        ruta_carpeta = os.path.join(base_dir, carpeta)
        if not os.path.exists(ruta_carpeta):
            print(f"⚠️ Alerta: No encuentro la carpeta '{carpeta}'")
            continue
            
        print(f"📂 Escaneando: {carpeta}")
        for root, dirs, files in os.walk(ruta_carpeta):
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    arreglar_archivo(os.path.join(root, file))

if __name__ == '__main__':
    procesar_carpetas()
    print("\n✅ ¡Listo! Imports corregidos. Ahora intenta ejecutar gui.py")