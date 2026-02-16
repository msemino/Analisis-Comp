"""Configuracion centralizada — Analisis de competencia en Tigre."""

from pathlib import Path

# --- Competidores ---
# Tupla: (slug identificador, nombre corto, URL base, es_propio)
HOTELS = [
    ("albarellos",    "Tigre Centro Cochera Gratis",        "https://www.booking.com/hotel/ar/albarellos-delta.es-ar.html",              True),
    ("puerto-delta",  "Puerto Delta",                       "https://www.booking.com/hotel/ar/puerto-delta.es-ar.html",                  False),
    ("puerto-tigre",  "Puerto Tigre",                       "https://www.booking.com/hotel/ar/puerto-tigre.es-ar.html",                  False),
    ("vivanco",       "Hospedaje de la Costa",              "https://www.booking.com/hotel/ar/hospedaje-vivanco.es-ar.html",             False),
    ("awka",          "Awka Villa del Rio",                 "https://www.booking.com/hotel/ar/awka-villa-del-rio-tigre.es-ar.html",      False),
    ("rowing",        "Buenos Aires Rowing Club",           "https://www.booking.com/hotel/ar/buenos-aires-rowing-club.es-ar.html",      False),
    ("depto-tigre",   "Departamento En Tigre",              "https://www.booking.com/hotel/ar/departamento-en-tigre-tigre.es-ar.html",   False),
    ("casa-tigre",    "La casa de tigre Centro",            "https://www.booking.com/hotel/ar/la-casa-de-tigre-centro.es-ar.html",       False),
]

# --- Browser ---
HEADLESS = False       # False para ver, True para produccion
MAX_CONCURRENT = 4     # Browsers simultaneos (4 es seguro para 16GB+ RAM)

# --- Paths ---
PROJECT_DIR = Path(__file__).parent
EVIDENCIAS_DIR = PROJECT_DIR / "evidencias"
EVIDENCIAS_DIR.mkdir(exist_ok=True)
