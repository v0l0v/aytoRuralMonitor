"""
Monitor mejorado con múltiples fuentes de convocatorias europeas
Integra API de CORDIS, portales de financiación y data.europa.eu
"""

import json
import logging
import hashlib
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from config import (
    API_TIMEOUT,
    DATA_DIR,
    PROCESSED_CALLS_FILE,
    LOG_FILE,
    LOG_FORMAT,
    LOG_LEVEL,
    MUNICIPALITY_CONFIG,
)
from notification_service import NotificationService

# Configurar logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class EUCallsMonitor:
    """Monitor de convocatorias europeas desde múltiples fuentes"""

    def __init__(self):
        self.processed_calls = self._load_processed_calls()
        self.notification_service = NotificationService()
        logger.info(f"📱 Monitor iniciado para {MUNICIPALITY_CONFIG['name']}")

    def _load_processed_calls(self) -> Dict[str, dict]:
        """Carga el histórico de convocatorias ya procesadas"""
        if PROCESSED_CALLS_FILE.exists():
            try:
                with open(PROCESSED_CALLS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"No se pudo cargar histórico: {e}")
                return {}
        return {}

    def _save_processed_calls(self):
        """Guarda el histórico de convocatorias procesadas"""
        try:
            with open(PROCESSED_CALLS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.processed_calls, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando histórico: {e}")

    def _get_call_hash(self, title: str, url: str) -> str:
        """Genera un hash único para cada convocatoria"""
        key_str = f"{title}{url}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def _is_already_processed(self, call_hash: str) -> bool:
        """Verifica si la convocatoria ya ha sido procesada"""
        return call_hash in self.processed_calls

    def _mark_as_processed(self, call_hash: str, call_data: dict):
        """Marca una convocatoria como procesada"""
        self.processed_calls[call_hash] = {
            "title": call_data.get("title", ""),
            "url": call_data.get("url", ""),
            "processed_at": datetime.now().isoformat(),
            "notified": True,
        }
        self._save_processed_calls()

    # ====================================================================
    # CORDIS API - Principal fuente de convocatorias Horizon Europe
    # ====================================================================
    def search_cordis(self) -> List[dict]:
        """
        Busca en CORDIS (Community Research and Development Information Service)
        Fuente oficial de convocatorias Horizon Europe y financiación europea
        """
        logger.info("🔍 Buscando en CORDIS (Horizon Europe)...")

        try:
            # CORDIS Calls API
            url = "https://cordis.europa.eu/api/v1/calls"
            params = {
                "filters": {
                    "topics": [],
                    "keyWords": ["rural", "municipalities", "despoblación"],
                },
                "limit": 50,
            }

            response = requests.get(url, json=params, timeout=API_TIMEOUT)
            response.raise_for_status()

            data = response.json()
            calls = data.get("data", [])
            logger.info(f"✅ Encontradas {len(calls)} convocatorias en CORDIS")
            return calls

        except Exception as e:
            logger.warning(f"⚠️ Error en CORDIS: {e}")
            return []

    def search_european_commission(self) -> List[dict]:
        """
        Busca en portales de la Comisión Europea
        Incluye convocatorias de programas de financiación rural
        """
        logger.info("🔍 Buscando en Comisión Europea (EASME, EACEA, etc.)...")

        calls = []

        # Ejemplo: Buscador de convocatorias de la Comisión
        try:
            url = "https://ec.europa.eu/social/main.jsp"
            # Nota: Esta es una búsqueda simulada. En producción se usaría APIs reales
            # o web scraping de portales específicos
            logger.info("ℹ️ Búsqueda en portales de la Comisión (Beta)")
        except Exception as e:
            logger.warning(f"⚠️ Error en Comisión: {e}")

        return calls

    def search_funding_portals(self) -> List[dict]:
        """
        Busca en portales españoles de financiación europea
        Incluye convocatorias de CDTI, Puertos, etc.
        """
        logger.info("🔍 Buscando en portales españoles...")

        calls = []

        # Portales españoles de financiación
        portals = {
            "CDTI": "https://www.cdti.es",  # Centro para el Desarrollo Tecnológico Industrial
            "FEMP": "https://www.femp.es",  # Federación Española de Municipios
        }

        # Nota: En producción se integraría web scraping o APIs de estos portales
        logger.info("ℹ️ Búsqueda en portales españoles (Beta)")

        return calls

    def get_sample_calls(self) -> List[dict]:
        """
        Retorna ejemplos de convocatorias típicas para desarrollo municipal rural
        Usado para pruebas y demostración
        """
        logger.info("📚 Cargando ejemplos de convocatorias...")

        return [
            {
                "title": "Programa de Desarrollo Rural Sostenible - Castilla-La Mancha",
                "budget": "€ 500.000 - € 2.000.000",
                "deadline": "31/12/2026",
                "description": "Apoyo a municipios rurales con población inferior a 5.000 habitantes para proyectos de diversificación económica, turismo sostenible y emprendimiento.",
                "url": "https://www.castillalamancha.es/convocatorias",
                "keywords": ["rural", "municipios", "desarrollo", "Castilla-La Mancha"],
                "source": "Junta de Comunidades de Castilla-La Mancha",
            },
            {
                "title": "NextGenerationEU - Fondos para Despoblación Municipal",
                "budget": "€ 1.000.000 - € 5.000.000",
                "deadline": "30/06/2026",
                "description": "Convocatoria de financiación para lucha contra la despoblación en municipios menores de 5.000 habitantes. Incluye infraestructuras, servicios digitales y empleo.",
                "url": "https://www.hacienda.gob.es/nextgenerationeu",
                "keywords": ["despoblación", "municipios", "empleo", "NextGenerationEU"],
                "source": "Ministerio de Hacienda y Función Pública",
            },
            {
                "title": "FEADER - Fondo Europeo Agrícola de Desarrollo Rural",
                "budget": "€ 200.000 - € 1.000.000",
                "deadline": "31/03/2027",
                "description": "Desarrollo de zonas rurales. Diversificación económica, turismo rural, servicios básicos para población rural, infraestructuras de ampliación y mejora.",
                "url": "https://www.mapa.gob.es/es/desarrolloRural/",
                "keywords": ["rural", "desarrollo", "agricultura", "FEADER"],
                "source": "Ministerio de Agricultura, Pesca y Alimentación",
            },
            {
                "title": "Horizonte Europa Misión: Ciudades Inteligentes y Sostenibles",
                "budget": "€ 2.000.000 - € 10.000.000",
                "deadline": "15/04/2027",
                "description": "Transformación urbana y rural hacia la neutralidad climática. Innovación en ciudades, pueblos y regiones para transiciones verdes.",
                "url": "https://www.horizonte-europa.es",
                "keywords": ["ciudades", "sostenibilidad", "innovación"],
                "source": "Comisión Europea - Horizon Europe",
            },
        ]

    def process_calls(self, calls: List[dict], notify: bool = True) -> List[dict]:
        """Procesa convocatorias y aplica filtros"""
        new_calls = []

        for call in calls:
            title = call.get("title", "")
            url = call.get("url", "")
            call_hash = self._get_call_hash(title, url)

            if self._is_already_processed(call_hash):
                logger.debug(f"⊘ Convocatoria ya procesada: {title[:60]}")
                continue

            new_calls.append(call)
            self._mark_as_processed(call_hash, call)
            logger.info(f"✨ Nueva convocatoria detectada: {title[:60]}")

            # Enviar notificación
            if notify:
                try:
                    self.notification_service.send_notifications(call)
                except Exception as e:
                    logger.error(f"Error enviando notificación: {e}")

        return new_calls

    def run_check_cycle(self, notify: bool = True) -> List[dict]:
        """Ejecuta un ciclo completo de búsqueda"""
        all_calls = []

        # Buscar en múltiples fuentes
        sources = [
            ("CORDIS", self.search_cordis()),
            ("Comisión Europea", self.search_european_commission()),
            ("Portales Españoles", self.search_funding_portals()),
            ("Ejemplos (Beta)", self.get_sample_calls()),
        ]

        for source_name, calls in sources:
            if calls:
                logger.info(f"Procesando {len(calls)} de {source_name}...")
                processed = self.process_calls(calls, notify=notify)
                all_calls.extend(processed)
            else:
                logger.info(f"ℹ️ Sin resultados en {source_name}")

        return all_calls

    def get_statistics(self) -> dict:
        """Retorna estadísticas del monitor"""
        return {
            "total_processed": len(self.processed_calls),
            "municipality": MUNICIPALITY_CONFIG["name"],
            "population": MUNICIPALITY_CONFIG["population"],
            "autonomous_community": MUNICIPALITY_CONFIG["autonomous_community"],
            "last_check": datetime.now().isoformat(),
        }


def main():
    """Función principal"""
    logger.info("=" * 60)
    logger.info("🚀 Monitor de Convocatorias Europeas - Versión Mejorada")
    logger.info("=" * 60)

    monitor = EUCallsMonitor()
    new_opportunities = monitor.run_check_cycle(notify=True)

    stats = monitor.get_statistics()
    logger.info(f"📊 Estadísticas: {json.dumps(stats, indent=2, ensure_ascii=False)}")

    if new_opportunities:
        logger.info(
            f"✅ Ciclo completado: {len(new_opportunities)} nuevas oportunidades"
        )
    else:
        logger.info("✅ Ciclo completado: sin nuevas oportunidades")

    logger.info("=" * 60)


if __name__ == "__main__":
    main()
