import os
import urllib.request
import zipfile
import shutil

# Configuración
STOCKFISH_URL = "https://github.com/official-stockfish/Stockfish/releases/download/sf_17.1/stockfish-windows-x86-64-avx2.zip"
BIN_DIR = "bin"
STOCKFISH_DIR = os.path.join(BIN_DIR, "stockfish")
ZIP_PATH = os.path.join(BIN_DIR, "stockfish.zip")

def setup_stockfish():
    print("--- Configurando Stockfish ---")
    
    # Crear carpeta bin si no existe
    if not os.path.exists(BIN_DIR):
        os.makedirs(BIN_DIR)
        print(f"Directorio {BIN_DIR} creado.")

    # Descargar el zip
    print(f"Descargando Stockfish desde {STOCKFISH_URL}...")
    try:
        urllib.request.urlretrieve(STOCKFISH_URL, ZIP_PATH)
        print("Descarga completada.")
    except Exception as e:
        print(f"Error al descargar: {e}")
        return

    # Extraer el zip
    print("Extrayendo archivos...")
    try:
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(STOCKFISH_DIR)
        print(f"Archivos extraídos en {STOCKFISH_DIR}.")
    except Exception as e:
        print(f"Error al extraer: {e}")
        return
    finally:
        # Limpiar el zip
        if os.path.exists(ZIP_PATH):
            os.remove(ZIP_PATH)

    # Buscar el ejecutable
    executable = None
    for root, dirs, files in os.walk(STOCKFISH_DIR):
        for file in files:
            if file.endswith(".exe"):
                executable = os.path.join(root, file)
                break
        if executable:
            break

    if executable:
        print(f"¡Stockfish configurado correctamente!")
        print(f"Ruta del ejecutable: {os.path.abspath(executable)}")
        
        # Guardar la ruta en un archivo de configuración simple o .env si es necesario
        # Por ahora lo dejaremos para que engine_analysis.py lo busque en bin/stockfish/
    else:
        print("No se encontró el ejecutable (.exe) después de la extracción.")

if __name__ == "__main__":
    setup_stockfish()
