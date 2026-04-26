"""
Scheduler para ejecutar el monitor de forma periódica
Utiliza APScheduler para gestionar las ejecuciones automáticas
"""

import logging
import signal
import sys
from datetime import datetime
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from config import CHECK_INTERVAL_MINUTES, DATA_DIR, LOG_FILE
from eu_api_monitor import EUAPIMonitor

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Variable global para el scheduler
scheduler = None


def setup_scheduler():
    """Configura y inicia el scheduler"""
    global scheduler

    scheduler = BackgroundScheduler()

    # Opción 1: Ejecutar cada X minutos
    scheduler.add_job(
        run_check,
        IntervalTrigger(minutes=CHECK_INTERVAL_MINUTES),
        id="eu_monitor_job",
        name="Monitor de Convocatorias Europeas",
        replace_existing=True,
    )

    # Opción 2 (alternativa): Ejecutar a horas específicas
    # scheduler.add_job(
    #     run_check,
    #     CronTrigger(hour='6,12,18'),  # A las 6, 12 y 18 horas
    #     id="eu_monitor_job",
    #     name="Monitor de Convocatorias Europeas",
    # )

    scheduler.start()
    logger.info(f"✅ Scheduler iniciado. Ejecución cada {CHECK_INTERVAL_MINUTES} minutos")

    # Ejecutar una primera búsqueda inmediatamente
    logger.info("🔍 Ejecutando búsqueda inicial...")
    run_check()


def run_check():
    """Función que ejecuta el ciclo de búsqueda"""
    try:
        logger.info("🔄 Iniciando ciclo de búsqueda...")
        monitor = EUAPIMonitor()
        new_opportunities = monitor.run_check_cycle(notify=True)

        if new_opportunities:
            logger.info(
                f"✨ Se detectaron {len(new_opportunities)} nuevas oportunidades"
            )
        else:
            logger.info("ℹ️ No hay nuevas oportunidades en este ciclo")

    except Exception as e:
        logger.error(f"❌ Error en ciclo de búsqueda: {e}", exc_info=True)


def signal_handler(sig, frame):
    """Maneja Ctrl+C para detener el scheduler"""
    logger.info("\n⏹️ Deteniendo scheduler...")
    if scheduler:
        scheduler.shutdown()
    logger.info("✅ Scheduler detenido")
    sys.exit(0)


def main():
    """Función principal"""
    logger.info("=" * 70)
    logger.info("🚀 MONITOR DE CONVOCATORIAS EUROPEAS - SCHEDULER")
    logger.info("=" * 70)
    logger.info(f"Inicio: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    logger.info(f"Intervalo de búsqueda: cada {CHECK_INTERVAL_MINUTES} minutos")
    logger.info("Presione Ctrl+C para detener")
    logger.info("=" * 70)

    # Configurar handler para Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Iniciar scheduler
    setup_scheduler()

    # Mantener el programa en ejecución
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()
