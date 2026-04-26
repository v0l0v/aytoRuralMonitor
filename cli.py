#!/usr/bin/env python3
"""
CLI para el Monitor de Convocatorias Europeas
Permite ejecutar el monitor con diferentes opciones desde terminal
"""

import argparse
import sys
import logging

from eu_api_monitor import EUAPIMonitor
from notification_service import NotificationService
from config import DATA_DIR

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def cmd_search(args):
    """Ejecuta una búsqueda puntual"""
    logger.info("🔍 Ejecutando búsqueda puntual...")
    monitor = EUAPIMonitor()

    if args.term:
        logger.info(f"Búsqueda por: {args.term}")
        results = monitor.search_opportunities(args.term)
    else:
        logger.info("Búsqueda por todos los términos configurados")
        all_results = []
        for term in monitor.search_terms:
            results = monitor.search_opportunities(term)
            all_results.extend(results)
        results = all_results

    new_calls = monitor.process_search_results(results)

    logger.info(f"\n✅ Búsqueda completada: {len(new_calls)} nuevas convocatorias")
    for call in new_calls:
        print(f"\n📢 {call['title']}")
        print(f"   💰 {call['budget']}")
        print(f"   📅 {call['deadline']}")
        print(f"   🔗 {call['url']}")


def cmd_test(args):
    """Ejecuta tests de configuración"""
    from test_monitor import main as run_tests
    sys.exit(run_tests())


def cmd_notify(args):
    """Envía un mensaje de prueba"""
    logger.info("📤 Enviando mensaje de prueba...")

    service = NotificationService()

    if not service.telegram_enabled and not service.whatsapp_enabled:
        logger.error("❌ No hay canales de notificación configurados")
        logger.info("Configura variables de entorno en .env")
        return False

    method = args.method or "both"
    success = service.send_test_message(method)

    if success:
        logger.info(f"✅ Mensaje de prueba enviado por {method}")
    else:
        logger.error(f"❌ Error enviando mensaje por {method}")

    return success


def cmd_scheduler(args):
    """Inicia el scheduler automático"""
    from scheduler import main as run_scheduler
    run_scheduler()


def cmd_stats(args):
    """Muestra estadísticas"""
    import json

    logger.info("📊 Estadísticas del monitor")
    logger.info("=" * 60)

    monitor = EUAPIMonitor()
    stats = monitor.get_statistics()

    print(json.dumps(stats, indent=2, ensure_ascii=False))

    print(f"\nConvocatorias procesadas en historial:")
    print(f"  Total: {stats['total_processed']}")

    if monitor.processed_calls:
        print(f"\n  Últimas 5:")
        for i, (hash_id, call_data) in enumerate(
            list(monitor.processed_calls.items())[-5:], 1
        ):
            print(f"    {i}. {call_data['title'][:50]}")
            print(f"       {call_data['processed_at'][:10]}")


def cmd_clean(args):
    """Limpia el historial de convocatorias procesadas"""
    if args.confirm:
        confirm = "yes"
    else:
        confirm = input("⚠️  ¿Borrar todo el historial? (escribir 'yes' para confirmar): ")

    if confirm.lower() == "yes":
        import os
        try:
            processed_file = DATA_DIR / "processed_calls.json"
            if processed_file.exists():
                os.remove(processed_file)
                logger.info("✅ Historial borrado. Se renotificarán convocatorias previas.")
            else:
                logger.info("ℹ️ No hay historial para borrar")
        except Exception as e:
            logger.error(f"❌ Error al borrar historial: {e}")
            return False
    else:
        logger.info("Operación cancelada")
        return False

    return True


def main():
    parser = argparse.ArgumentParser(
        description="🚀 Monitor de Convocatorias Europeas para Municipios Rurales",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Búsqueda puntual
  python cli.py search
  python cli.py search --term "Castilla-La Mancha"

  # Ejecutar tests
  python cli.py test

  # Enviar mensaje de prueba
  python cli.py notify
  python cli.py notify --method telegram

  # Iniciar scheduler automático
  python cli.py scheduler

  # Ver estadísticas
  python cli.py stats

  # Limpiar historial
  python cli.py clean
  python cli.py clean --yes
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar")

    # Comando: search
    parser_search = subparsers.add_parser("search", help="Ejecutar búsqueda puntual")
    parser_search.add_argument(
        "--term", "-t", help="Término específico a buscar (opcional)"
    )
    parser_search.set_defaults(func=cmd_search)

    # Comando: test
    parser_test = subparsers.add_parser("test", help="Ejecutar tests de configuración")
    parser_test.set_defaults(func=cmd_test)

    # Comando: notify
    parser_notify = subparsers.add_parser("notify", help="Enviar mensaje de prueba")
    parser_notify.add_argument(
        "--method",
        "-m",
        choices=["telegram", "whatsapp", "both"],
        help="Método de notificación",
    )
    parser_notify.set_defaults(func=cmd_notify)

    # Comando: scheduler
    parser_scheduler = subparsers.add_parser(
        "scheduler", help="Iniciar scheduler automático"
    )
    parser_scheduler.set_defaults(func=cmd_scheduler)

    # Comando: stats
    parser_stats = subparsers.add_parser("stats", help="Ver estadísticas")
    parser_stats.set_defaults(func=cmd_stats)

    # Comando: clean
    parser_clean = subparsers.add_parser("clean", help="Limpiar historial")
    parser_clean.add_argument(
        "--yes", action="store_true", help="Confirmar sin preguntar"
    )
    parser_clean.set_defaults(func=cmd_clean)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    try:
        return args.func(args) or 0
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
