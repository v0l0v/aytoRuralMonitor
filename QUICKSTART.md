# 🚀 INICIO RÁPIDO - Monitor de Convocatorias Europeas

Sigue estos pasos para tener el monitor funcionando en 5 minutos.

## 1️⃣ Instalación (2 min)

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## 2️⃣ Configuración (2 min)

```bash
# Copiar plantilla de configuración
cp .env.example .env

# Editar con tus datos
nano .env
```

### Opción más fácil: Telegram

1. Abre [@BotFather](https://t.me/botfather)
2. Escribe `/newbot` y copia el TOKEN
3. Escribe un mensaje a tu bot nuevo
4. Ve a `https://api.telegram.org/bot<TOKEN>/getUpdates` y copia tu CHAT_ID
5. Pega TOKEN y CHAT_ID en `.env`

## 3️⃣ Primera prueba (1 min)

```bash
# Ejecutar tests
python test_monitor.py
```

Deberías ver:
- ✅ TEST 1: Conexión a la API → exitosa
- ✅ TEST 2: Notificaciones → enviadas
- ✅ TEST 3: Ciclo completo → completado

## 4️⃣ ¡Listo! Elige cómo ejecutar:

### Opción A: Búsqueda puntual
```bash
python eu_api_monitor.py
```
Busca una sola vez.

### Opción B: Scheduler automático (RECOMENDADO)
```bash
python scheduler.py
```
Busca automáticamente cada 6 horas. Presiona Ctrl+C para detener.

### Opción C: CLI avanzada
```bash
python cli.py search                    # Búsqueda puntual
python cli.py notify --method telegram  # Enviar test
python cli.py scheduler                 # Iniciar scheduler
python cli.py stats                     # Ver estadísticas
```

## ✨ Cambios recomendados

Edita `config.py` para personalizar:

```python
# Tu municipio
MUNICIPALITY_CONFIG = {
    "name": "Tu Pueblo",          # ← Cambiar
    "population": 3500,            # ← Cambiar
    "autonomous_community": "Castilla-La Mancha",  # ← Cambiar si es necesario
}

# Términos de búsqueda
SEARCH_TERMS = [
    "Tu provincia",                # ← Añadir
    "Tu municipio específico",     # ← Añadir
]

# Intervalo de búsqueda
CHECK_INTERVAL_MINUTES = 360       # ← 6 horas. Cambiar si quieres más frecuente
```

## 🧪 Troubleshooting rápido

| Problema | Solución |
|----------|----------|
| "ModuleNotFoundError: No module named 'requests'" | `pip install -r requirements.txt` |
| No se envían notificaciones | Verifica que `.env` existe y tiene valores |
| API no responde | Espera un momento, puede estar saturada. Reintentar. |
| Necesito logs | `tail -f data/app.log` |

## 📞 Próximos pasos

- [ ] Configurar Telegram o WhatsApp
- [ ] Personalizar municipio en `config.py`
- [ ] Ejecutar `test_monitor.py` exitosamente
- [ ] Iniciar `scheduler.py` en background
- [ ] Recibir primera notificación de convocatoria
- [ ] Configurar ejecución permanente (systemd/Docker/cron)

## 🎯 Tips de productividad

- **Monitoreo remoto**: Ejecuta en un servidor VPS/cloud 24/7
- **Alertas prioritarias**: Personaliza `RELEVANT_KEYWORDS` en `config.py`
- **Múltiples municipios**: Copia toda la carpeta y cambia `config.py` en cada copia
- **Datos históricos**: El archivo `data/processed_calls.json` guarda todas las convocatorias

---

**¿Preguntas?** Ver README.md para documentación completa.
