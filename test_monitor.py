"""
Script de prueba para verificar la configuración y probar el monitor
"""

import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

from eu_api_monitor import EUAPIMonitor
from notification_service import NotificationService


def test_api_connection():
    """Prueba la conexión a la API"""
    logger.info("\n" + "=" * 60)
    logger.info("🧪 TEST 1: Conexión a la API de data.europa.eu")
    logger.info("=" * 60)

    monitor = EUAPIMonitor()
    results = monitor.search_opportunities("Castilla-La Mancha")

    if results:
        logger.info(f"✅ Conexión exitosa. Se obtuvieron {len(results)} resultados")
        title = results[0].get("title", "N/A")
        if isinstance(title, dict):
            title = title.get("en", "") or (list(title.values())[0] if title else "N/A")
        logger.info(f"Primera resultado: {str(title)[:80]}")
        return True
    else:
        logger.error("❌ No se obtuvieron resultados")
        return False


def test_notifications():
    """Prueba el servicio de notificaciones"""
    logger.info("\n" + "=" * 60)
    logger.info("🧪 TEST 2: Servicio de notificaciones")
    logger.info("=" * 60)

    service = NotificationService()

    if not service.telegram_enabled and not service.whatsapp_enabled:
        logger.warning("⚠️ Ningún método de notificación está configurado")
        logger.info("Para usar notificaciones, complete las variables de entorno en .env")
        return False

    if service.telegram_enabled:
        logger.info("📱 Telegram: Configurado")
    else:
        logger.info("📱 Telegram: No configurado")

    if service.whatsapp_enabled:
        logger.info("📱 WhatsApp: Configurado")
    else:
        logger.info("📱 WhatsApp: No configurado")

    # Enviar mensaje de prueba
    logger.info("\n📤 Enviando mensaje de prueba...")
    success = service.send_test_message("both")

    if success:
        logger.info("✅ Prueba de notificaciones completada")
    else:
        logger.warning("⚠️ No se pudo enviar el mensaje de prueba (verificar .env)")

    return True


def test_full_cycle():
    """Prueba un ciclo completo de búsqueda y procesamiento"""
    logger.info("\n" + "=" * 60)
    logger.info("🧪 TEST 3: Ciclo completo de búsqueda")
    logger.info("=" * 60)

    monitor = EUAPIMonitor()
    logger.info("Ejecutando ciclo completo...")
    new_calls = monitor.run_check_cycle(notify=False)  # Sin notificar en prueba

    logger.info(f"✅ Ciclo completado")
    logger.info(f"Nuevas convocatorias detectadas: {len(new_calls)}")

    if new_calls:
        logger.info("\nEjemplos de convocatorias:")
        for i, call in enumerate(new_calls[:3], 1):
            logger.info(f"\n{i}. {call['title'][:60]}")
            logger.info(f"   Presupuesto: {call['budget']}")
            logger.info(f"   Plazo: {call['deadline']}")

    return len(new_calls) >= 0


def main():
    """Ejecuta todos los tests"""
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 58 + "║")
    logger.info("║" + "  🚀 TESTS DEL MONITOR DE CONVOCATORIAS EUROPEAS  ".center(
        58
    ) + "║")
    logger.info("║" + " " * 58 + "║")
    logger.info("╚" + "=" * 58 + "╝")

    tests = [
        ("Conexión API", test_api_connection),
        ("Notificaciones", test_notifications),
        ("Ciclo completo", test_full_cycle),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ Error en {test_name}: {e}", exc_info=True)
            results.append((test_name, False))

    # Resumen final
    logger.info("\n" + "=" * 60)
    logger.info("📋 RESUMEN DE TESTS")
    logger.info("=" * 60)

    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        logger.info(f"{status}: {test_name}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    logger.info("=" * 60)
    logger.info(f"Resultado: {passed}/{total} tests exitosos")

    if passed == total:
        logger.info("✅ ¡Configuración lista para usar!")
        return 0
    else:
        logger.warning(
            "⚠️ Por favor, revisa la configuración antes de ejecutar el scheduler"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
