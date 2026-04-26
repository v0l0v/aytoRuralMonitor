# 🚀 Monitor de Convocatorias Europeas para Municipios Rurales

Un script inteligente en Python que monitorea automáticamente oportunidades de financiación europea en [data.europa.eu](https://data.europa.eu) y envía alertas a través de **Telegram** o **WhatsApp** al Alcalde y Secretario del municipio.

## 📋 Características principales

✅ **Consulta automática y periódica** de la API de data.europa.eu  
✅ **Filtrado inteligente** por términos relevantes (Castilla-La Mancha, Despoblación, NextGenerationEU, FEADER, etc.)  
✅ **Detección de relevancia** ajustada a municipios < 5.000 habitantes  
✅ **Almacenamiento local** de convocatorias procesadas para evitar duplicados  
✅ **Notificaciones inmediatas** por Telegram o WhatsApp  
✅ **Resúmenes ejecutivos** con presupuesto, plazo y enlace directo  
✅ **Historial y estadísticas** para auditoría y seguimiento  
✅ **Logs detallados** para debugging y monitoreo  

## 🏗️ Estructura del proyecto

```
aytorural/
├── config.py                 # Configuración centralizada
├── eu_api_monitor.py         # Motor principal de búsqueda
├── notification_service.py   # Servicio de notificaciones (Telegram/WhatsApp)
├── scheduler.py              # Scheduler para ejecución periódica
├── test_monitor.py           # Suite de tests
├── requirements.txt          # Dependencias Python
├── .env.example              # Plantilla de variables de entorno
├── .env                      # Variables de entorno (NO COMMITEAR)
├── README.md                 # Este archivo
└── data/
    ├── processed_calls.json  # Histórico de convocatorias procesadas
    └── app.log              # Logs de ejecución
```

## 📦 Instalación

### 1. Clonar el repositorio

```bash
cd /home/victor/Proyectos_ia/aytorural
```

### 2. Crear entorno virtual (recomendado)

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus credenciales
nano .env
```

## 🔐 Configuración de notificaciones

### Opción A: Telegram (Recomendado)

#### Paso 1: Crear bot en Telegram
1. Abre [@BotFather](https://t.me/botfather) en Telegram
2. Escribe `/newbot`
3. Sigue las instrucciones
4. Obtén tu **TOKEN** (ej: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

#### Paso 2: Obtener CHAT_ID
1. Escribe un mensaje a tu bot
2. Ve a: `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Busca `"chat":{"id":XXXXXX}` - ese es tu CHAT_ID

#### Paso 3: Configurar .env
```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID_ALCALDE=987654321
TELEGRAM_CHAT_ID_SECRETARIO=987654322
```

### Opción B: WhatsApp (Twilio)

#### Paso 1: Crear cuenta en Twilio
1. Regístrate en [twilio.com](https://www.twilio.com)
2. Verifica tu número de teléfono
3. Accede a la [consola](https://console.twilio.com)

#### Paso 2: Habilitar WhatsApp Sandbox
1. Ve a: Messaging → Try it out → Send an SMS
2. O ve a: Messaging → Sandbox
3. Sigue las instrucciones para habilitar WhatsApp

#### Paso 3: Obtener credenciales
1. En la consola, ve a Account
2. Copia **ACCOUNT_SID** y **AUTH_TOKEN**
3. En Messaging → Sandbox, obtén el número de WhatsApp asignado

#### Paso 4: Configurar .env
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+34600123456
WHATSAPP_ALCALDE=whatsapp:+34700987654
WHATSAPP_SECRETARIO=whatsapp:+34700987655
```

## ⚙️ Personalización del municipio

Edita `config.py` y personaliza:

```python
MUNICIPALITY_CONFIG = {
    "name": "Tu Pueblo",
    "population": 3500,           # Tus habitantes
    "autonomous_community": "Castilla-La Mancha",
    "province": "Cuenca",
    "postal_code": "16001",
    "contact_email": "alcaldia@tupueblo.es",
}

# Añade más términos de búsqueda si lo necesitas
SEARCH_TERMS = [
    "Castilla-La Mancha",
    "Tu provincia",
    "Tu municipio",
    # ...
]
```

## 🚀 Uso

### 1. Ejecutar prueba rápida

```bash
python test_monitor.py
```

Esto valida:
- ✅ Conexión a la API
- ✅ Configuración de notificaciones
- ✅ Ciclo completo de búsqueda

### 2. Ejecutar búsqueda única

```bash
python eu_api_monitor.py
```

Busca todas las convocatorias una sola vez.

### 3. Ejecutar scheduler (RECOMENDADO)

```bash
python scheduler.py
```

Ejecuta búsquedas automáticamente cada 6 horas (configurable en `config.py`).

Presiona `Ctrl+C` para detener.

## 📊 Ejemplo de notificación

```
🎯 CONVOCATORIA EUROPEA - TU PUEBLO

📢 Convocatoria de desarrollo rural 2024-2026

💰 Dotación: € 200.000 - € 500.000

📅 Plazo: 31/12/2026

📋 Resumen:
Programa de apoyo a municipios rurales con despoblación...

🎯 Perfil del municipio:
• Población: 3500 habitantes
• Comunidad: Castilla-La Mancha

🔗 Enlace: https://data.europa.eu/...

⏰ Detectado: 26/04/2026 14:32

⚡ ACCIÓN RECOMENDADA:
1. Revisar documentación completa
2. Contactar con asesor de subvenciones
3. Convocar reunión de coordinación
```

## 📝 Historial y logs

- **`data/processed_calls.json`**: Registro de convocatorias procesadas (evita duplicados)
- **`data/app.log`**: Logs detallados de cada ejecución

```bash
# Ver últimos logs
tail -f data/app.log

# Ver estadísticas de convocatorias
cat data/processed_calls.json | python -m json.tool
```

## 🔧 Configuración avanzada

### Cambiar intervalo de búsqueda

En `config.py`:
```python
CHECK_INTERVAL_MINUTES = 360  # Cambiar a 180 (3 horas), 120 (2 horas), etc.
```

### Ejecutar en horarios específicos

En `scheduler.py`, descomenta:
```python
# Ejecutar a las 6, 12 y 18 horas
scheduler.add_job(
    run_check,
    CronTrigger(hour='6,12,18'),
    id="eu_monitor_job",
)
```

### Añadir más términos de búsqueda

En `config.py`:
```python
SEARCH_TERMS = [
    "Castilla-La Mancha",
    "Tu provincia específica",
    "Nombre de tu municipio",
    "Términos personalizados",
]
```

### Cambiar nivel de relevancia

En `eu_api_monitor.py`, modifica `_is_relevant_to_municipality()` para ajustar qué convocatorias se consideran relevantes.

## 🐛 Troubleshooting

### Error: "No module named requests"
```bash
pip install -r requirements.txt
```

### Error: "TELEGRAM_BOT_TOKEN not set"
- Verifica que `.env` existe y tiene el TOKEN correcto
- Asegúrate de que estás activando el venv: `source venv/bin/activate`

### No se reciben notificaciones
1. Ejecuta: `python test_monitor.py`
2. Revisa que Telegram/WhatsApp están correctamente configurados
3. Verifica los logs: `tail -f data/app.log`

### API no responde
- Verifica conexión a internet
- data.europa.eu a veces puede estar lenta; el script reintentará en el siguiente ciclo

## 📚 API Reference

### data.europa.eu API

- **Endpoint**: `https://data.europa.eu/api/hub/search/search`
- **Parámetros principales**:
  - `query`: término de búsqueda
  - `limit`: máximo de resultados (default: 10, max: 1000)
  - `offset`: paginación

Documentación: https://data.europa.eu/api/hub/search

## 🛡️ Buenas prácticas

✅ Usa archivos `.env` para credenciales (NO los commits)  
✅ Crea bots de Telegram separados para desarrollo/producción  
✅ Revisa los logs regularmente  
✅ Prueba con `test_monitor.py` antes de activar el scheduler  
✅ Configura un máximo de habitantes conservador (ej: 5.000)  
✅ Monitorea el consumo de llamadas a API  

## 🚀 Despliegue en producción

### Opción 1: Ejecutar en background con systemd (Linux/macOS)

Crear archivo `/etc/systemd/system/aytorural-monitor.service`:

```ini
[Unit]
Description=Monitor de Convocatorias Europeas - AytoRural
After=network.target

[Service]
Type=simple
User=usuario
WorkingDirectory=/home/victor/Proyectos_ia/aytorural
ExecStart=/home/victor/Proyectos_ia/aytorural/venv/bin/python scheduler.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable aytorural-monitor
sudo systemctl start aytorural-monitor
sudo systemctl status aytorural-monitor
```

### Opción 2: Usar Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "scheduler.py"]
```

```bash
docker build -t aytorural-monitor .
docker run -d --env-file .env --name aytorural aytorural-monitor
```

### Opción 3: Heroku/PythonAnywhere

Simplemente despliega el repositorio y configura las variables de entorno.

## 📞 Soporte

- 📧 Email: alcaldia@tupueblo.es
- 🐛 Issues: Reporta problemas en el repositorio
- 📖 Wiki: Próximamente

## 📄 Licencia

MIT License - Libre para uso en municipios

## 🙏 Créditos

Desarrollado como herramienta de innovación pública para municipios rurales.

---

**Ventaja competitiva**: Con este script, tu municipio recibe notificaciones de nuevas convocatorias europeas días antes que otros municipios similares. ⚡
