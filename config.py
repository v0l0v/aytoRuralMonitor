"""
Configuración central para el monitor de convocatorias europeas
Adaptada para municipios rurales < 5.000 habitantes
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent

# ============================================================================
# CONFIGURACIÓN DE LA API
# ============================================================================
API_BASE_URL = "https://data.europa.eu/api/hub/search/search"
API_TIMEOUT = 30  # segundos

# Términos de búsqueda para filtrar convocatorias relevantes
SEARCH_TERMS = [
    "Castilla-La Mancha",
    "Despoblación",
    "NextGenerationEU",
    "municipios rurales",
    "zonas rurales",
    "desarrollo rural",
    "fondos europeos municipios",
    "PRTR",  # Plan de Recuperación, Transformación y Resiliencia
    "FEADER",  # Fondo Europeo Agrícola de Desarrollo Rural
]

# Palabras clave para identificar convocatorias relevantes
RELEVANT_KEYWORDS = {
    "despoblación",
    "rural",
    "municipios pequeños",
    "habitantes",
    "desarrollo local",
    "cofinanciación",
    "europeo",
}

# Máximo número de habitantes para considerar el municipio
MAX_INHABITANTS = 5000

# ============================================================================
# CONFIGURACIÓN DE NOTIFICACIONES
# ============================================================================

# TELEGRAM
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")  # Obtener del archivo .env
# IDs de destinatarios (pueden ser varios separados por coma)
_tg_ids = os.getenv("TELEGRAM_RECIPIENTS", os.getenv("TELEGRAM_CHAT_ID_ALCALDE", ""))
TELEGRAM_RECIPIENTS = [i.strip() for i in _tg_ids.split(",") if i.strip()]

# WHATSAPP (usando Twilio)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "")  # ej: "whatsapp:+34600123456"
# Números de destinatarios (pueden ser varios separados por coma)
_wa_nums = os.getenv("WHATSAPP_RECIPIENTS", os.getenv("WHATSAPP_ALCALDE", ""))
WHATSAPP_RECIPIENTS = [n.strip() for n in _wa_nums.split(",") if n.strip()]

# ============================================================================
# CONFIGURACIÓN DE ALMACENAMIENTO LOCAL
# ============================================================================
DATA_DIR = BASE_DIR / "data"
PROCESSED_CALLS_FILE = DATA_DIR / "processed_calls.json"
LOG_FILE = DATA_DIR / "app.log"

# ============================================================================
# CONFIGURACIÓN DEL SCHEDULER
# ============================================================================
# Intervalo de consulta en minutos (cada 6 horas = 360 minutos)
CHECK_INTERVAL_MINUTES = 60

# ============================================================================
# INFORMACIÓN DEL MUNICIPIO (PERSONALIZAR)
# ============================================================================
MUNICIPALITY_CONFIG = {
    "name": "Uclés", # Nombre dgún el pueblo
    "population": 230,  # Ajustar según el pueblo
    "autonomous_community": "Castilla-La Mancha",
    "province": "Cuenca",
    "postal_code": "16452",
    "contact_email": "vict0rl0pez@protonmail.com",
}

# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

# ============================================================================
# CONFIGURACIÓN DE CACHING
# ============================================================================
# Tiempo de cacheo de resultados en minutos (evita consultas duplicadas)
CACHE_DURATION_MINUTES = 60

# ============================================================================
# DATOS GEOGRÁFICOS DE ESPAÑA
# ============================================================================
SPAIN_GEOGRAPHY = {
    "Andalucía": ["Almería", "Cádiz", "Córdoba", "Granada", "Huelva", "Jaén", "Málaga", "Sevilla"],
    "Aragón": ["Huesca", "Teruel", "Zaragoza"],
    "Asturias": ["Asturias"],
    "Baleares": ["Islas Baleares"],
    "Canarias": ["Las Palmas", "Santa Cruz de Tenerife"],
    "Cantabria": ["Cantabria"],
    "Castilla y León": ["Ávila", "Burgos", "León", "Palencia", "Salamanca", "Segovia", "Soria", "Valladolid", "Zamora"],
    "Castilla-La Mancha": ["Albacete", "Ciudad Real", "Cuenca", "Guadalajara", "Toledo"],
    "Cataluña": ["Barcelona", "Gerona", "Lérida", "Tarragona"],
    "Comunidad Valenciana": ["Alicante", "Castellón", "Valencia"],
    "Extremadura": ["Badajoz", "Cáceres"],
    "Galicia": ["La Coruña", "Lugo", "Orense", "Pontevedra"],
    "Madrid": ["Madrid"],
    "Murcia": ["Murcia"],
    "Navarra": ["Navarra"],
    "País Vasco": ["Álava", "Guipúzcoa", "Vizcaya"],
    "La Rioja": ["La Rioja"],
    "Ceuta": ["Ceuta"],
    "Melilla": ["Melilla"]
}
