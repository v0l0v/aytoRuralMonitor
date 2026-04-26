"""
Monitor de convocatorias europeas para municipios rurales
Consulta periódicamente data.europa.eu y notifica sobre oportunidades de financiación
"""

import json
import logging
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import requests
from urllib.parse import urlencode

from config import (
    API_BASE_URL,
    API_TIMEOUT,
    SEARCH_TERMS,
    RELEVANT_KEYWORDS,
    DATA_DIR,
    PROCESSED_CALLS_FILE,
    LOG_FILE,
    LOG_FORMAT,
    LOG_LEVEL,
    CACHE_DURATION_MINUTES,
    MUNICIPALITY_CONFIG,
)
from notification_service import NotificationService

# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class EUAPIMonitor:
    """Monitor principal para convocatorias europeas"""

    def __init__(self):
        self.api_url = API_BASE_URL
        self.search_terms = SEARCH_TERMS
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

    def _get_call_hash(self, call_data: dict) -> str:
        """Genera un hash único para cada convocatoria"""
        key_str = f"{call_data.get('title', '')}{call_data.get('url', '')}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def _is_already_processed(self, call_hash: str) -> bool:
        """Verifica si la convocatoria ya ha sido procesada"""
        if call_hash in self.processed_calls:
            processed_time = datetime.fromisoformat(
                self.processed_calls[call_hash]["processed_at"]
            )
            age = datetime.now() - processed_time
            # Renotificar si han pasado más de 30 días
            if age.days > 30:
                return False
            return True
        return False

    def _mark_as_processed(self, call_hash: str, call_data: dict):
        """Marca una convocatoria como procesada"""
        self.processed_calls[call_hash] = {
            "title": call_data.get("title", ""),
            "url": call_data.get("url", ""),
            "processed_at": datetime.now().isoformat(),
            "notified": True,
        }
        self._save_processed_calls()

    def _is_relevant_to_municipality(self, call_data: dict) -> bool:
        """
        Determina si una convocatoria es relevante para el municipio
        Verifica:
        - Palabras clave
        - Población objetivo
        - Ubicación geográfica
        """
        # Extraer título y descripción (pueden estar en formato dict con idiomas)
        title = call_data.get("title", {})
        if isinstance(title, dict):
            title = title.get("en", "") or list(title.values())[0] if title else ""
        title = (title or "").lower()
        
        description = call_data.get("description", {})
        if isinstance(description, dict):
            description = description.get("en", "") or list(description.values())[0] if description else ""
        description = (description or "").lower()
        
        full_text = f"{title} {description}"

        # Verificar palabras clave
        has_relevant_keywords = any(kw in full_text for kw in RELEVANT_KEYWORDS)

        if not has_relevant_keywords:
            return False

        # Verificar ubicación (Castilla-La Mancha, comunidad autónoma, etc.)
        location_terms = [
            "castilla",
            "españa",
            "europa",
            "nacional",
            "regional",
            "local",
        ]
        has_location = any(loc in full_text for loc in location_terms)

        # Convocatorias sin restricción de población son válidas
        # Si menciona "municipios pequeños" o "habitantes", considerarla válida
        if "municipios pequeños" in full_text or "habitantes" in full_text:
            return has_location

        # Si no especifica población pero es relevante, considerarla válida
        return has_location and has_relevant_keywords

    def _extract_budget(self, call_data: dict) -> str:
        """Extrae información de presupuesto"""
        budget = call_data.get("budget", "")
        if budget:
            return str(budget)
        return "Presupuesto no especificado"

    def _extract_deadline(self, call_data: dict) -> str:
        """Extrae la fecha límite"""
        deadline = call_data.get("deadline", "")
        if deadline:
            try:
                # Intentar parsear y formatear la fecha
                date_obj = datetime.fromisoformat(str(deadline).split("T")[0])
                return date_obj.strftime("%d/%m/%Y")
            except:
                return str(deadline)
        return "Consultar en el sitio web"

    def _create_summary(self, call_data: dict) -> dict:
        """Crea un resumen ejecutivo de la convocatoria"""
        # Extraer título (puede ser string o dict con idiomas)
        title = call_data.get("title", "Sin título")
        if isinstance(title, dict):
            title = title.get("en", "") or list(title.values())[0] if title else "Sin título"
        
        # Extraer descripción (puede ser string o dict con idiomas)
        description = call_data.get("description", "")
        if isinstance(description, dict):
            description = description.get("en", "") or list(description.values())[0] if description else ""
        
        summary = (description or "")[:500]
        if len(summary) > 0 and not summary.endswith("."):
            summary += "..."

        return {
            "title": title,
            "url": call_data.get("url", "https://data.europa.eu"),
            "budget": self._extract_budget(call_data),
            "deadline": self._extract_deadline(call_data),
            "summary": summary,
            "source": call_data.get("source", "EU Portal"),
        }

    def search_opportunities(self, term: Optional[str] = None) -> List[dict]:
        """
        Busca convocatorias en data.europa.eu
        """
        if term is None:
            term = self.search_terms[0]

        logger.info(f"🔍 Buscando: '{term}'...")

        try:
            # Parámetros de búsqueda
            params = {
                "query": term,
                "limit": 50,
                "offset": 0,
            }

            response = requests.get(
                self.api_url, params=params, timeout=API_TIMEOUT, headers={"User-Agent": "AytoRural-Monitor/1.0"}
            )
            response.raise_for_status()

            data = response.json()
            # La API devuelve resultados en data["result"]["results"]
            results = data.get("result", {}).get("results", [])
            logger.info(f"✅ Encontradas {len(results)} convocatorias para '{term}'")
            return results

        except requests.exceptions.Timeout:
            logger.error(f"⏱️ Timeout al consultar API para '{term}'")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error en consulta API: {e}")
            return []
        except json.JSONDecodeError:
            logger.error("❌ Respuesta API no es JSON válido")
            return []

    def process_search_results(self, results: List[dict], only_new: bool = True) -> List[dict]:
        """
        Procesa resultados de búsqueda y filtra por relevancia
        """
        new_calls = []

        for call in results:
            call_hash = self._get_call_hash(call)

            # Saltar si ya fue procesado (solo si buscamos solo nuevas)
            if only_new and self._is_already_processed(call_hash):
                logger.debug(f"⊘ Convocatoria ya procesada: {call.get('title', '')}")
                continue

            # Verificar relevancia
            if not self._is_relevant_to_municipality(call):
                logger.debug(f"⊘ No relevante: {call.get('title', '')}")
                continue

            summary = self._create_summary(call)
            new_calls.append(summary)

            # Marcar como procesada
            self._mark_as_processed(call_hash, call)
            logger.info(f"✨ Nueva convocatoria detectada: {summary['title']}")

        return new_calls

    def run_check_cycle(self, notify: bool = True) -> List[dict]:
        """
        Ejecuta un ciclo completo de búsqueda y procesamiento
        """
        all_new_calls = []

        for term in self.search_terms:
            try:
                results = self.search_opportunities(term)
                new_calls = self.process_search_results(results)
                all_new_calls.extend(new_calls)

                # Pequeña pausa entre búsquedas para no saturar
                import time
                time.sleep(2)

            except Exception as e:
                logger.error(f"Error procesando término '{term}': {e}")
                continue

        # Enviar notificaciones de nuevas convocatorias
        if notify and all_new_calls:
            logger.info(f"📢 Enviando {len(all_new_calls)} notificaciones...")
            for call in all_new_calls:
                try:
                    self.notification_service.send_notifications(call)
                except Exception as e:
                    logger.error(f"Error enviando notificación: {e}")

        return all_new_calls

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
    """Función principal para ejecutar el monitor"""
    logger.info("=" * 60)
    logger.info("🚀 Iniciando Monitor de Convocatorias Europeas")
    logger.info("=" * 60)

    monitor = EUAPIMonitor()

    # Ejecutar ciclo de búsqueda
    new_opportunities = monitor.run_check_cycle(notify=True)

    # Mostrar estadísticas
    stats = monitor.get_statistics()
    logger.info(f"📊 Estadísticas: {json.dumps(stats, indent=2, ensure_ascii=False)}")

    if new_opportunities:
        logger.info(
            f"✅ Ciclo completado: {len(new_opportunities)} nuevas oportunidades detectadas"
        )
    else:
        logger.info("✅ Ciclo completado: sin nuevas oportunidades")

    logger.info("=" * 60)


if __name__ == "__main__":
    main()
