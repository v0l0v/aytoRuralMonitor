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
        metadata = call_data.get("metadata", {})
        identifier_list = metadata.get("identifier", [])
        identifier = identifier_list[0] if identifier_list else ""
        key_str = f"{identifier}"
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
        """
        metadata = call_data.get("metadata", {})
        title_list = metadata.get("title", [])
        title = (title_list[0] if title_list else "").lower()
        
        desc_list = metadata.get("description", [])
        description = (desc_list[0] if desc_list else "").lower()
        
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
        if "municipios pequeños" in full_text or "habitantes" in full_text:
            return has_location

        # Si no especifica población pero es relevante, considerarla válida
        return has_location and has_relevant_keywords

    def _extract_budget(self, call_data: dict) -> str:
        """Extrae información de presupuesto"""
        metadata = call_data.get("metadata", {})
        budget = metadata.get("estimatedOverallContractAmount", []) or metadata.get("budgetAmount", [])
        if budget:
            return str(budget[0])
        return "Presupuesto no especificado"

    def _extract_deadline(self, call_data: dict) -> str:
        """Extrae la fecha límite"""
        metadata = call_data.get("metadata", {})
        deadline = metadata.get("deadlineDate", []) or metadata.get("cftDeadlineDate", [])
        if deadline:
            try:
                date_obj = datetime.fromisoformat(str(deadline[0]).split("T")[0])
                return date_obj.strftime("%d/%m/%Y")
            except:
                return str(deadline[0])
        return "Consultar en el sitio web"

    def _create_summary(self, call_data: dict) -> dict:
        """Crea un resumen ejecutivo de la convocatoria"""
        metadata = call_data.get("metadata", {})
        title_list = metadata.get("title", [])
        title = title_list[0] if title_list else "Sin título"
        
        desc_list = metadata.get("description", [])
        description = desc_list[0] if desc_list else ""
        
        summary = (description or "")[:500]
        if len(summary) > 0 and not summary.endswith("."):
            summary += "..."

        identifier_list = metadata.get("identifier", [])
        identifier = identifier_list[0] if identifier_list else ""
        
        cft_id_list = metadata.get("cftId", [])
        cft_id = cft_id_list[0] if cft_id_list else ""

        if cft_id:
            url = f"https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/tender-details/{cft_id}"
        elif identifier:
            url = f"https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-details/{identifier}"
        else:
            url = "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/calls-for-proposals"
        return {
            "title": title,
            "url": url,
            "budget": self._extract_budget(call_data),
            "deadline": self._extract_deadline(call_data),
            "summary": summary,
            "source": "EU Funding & Tenders Portal",
        }

    def search_opportunities(self, term: Optional[str] = None) -> List[dict]:
        """
        Busca convocatorias en el portal SEDIA de la Comisión Europea
        """
        if term is None:
            term = self.search_terms[0]

        logger.info(f"🔍 Buscando: '{term}'...")

        try:
            params = {"apiKey": "SEDIA", "text": term, "pageSize": "50", "pageNumber": "1"}
            query = {"bool": {"must": [{"terms": {"type": ["0","1","2"]}}]}}
            languages = ["es", "en"]
            sort = {"field": "sortStatus", "order": "ASC"}

            response = requests.post(
                self.api_url,
                params=params,
                files={
                    "query": (None, json.dumps(query), "application/json"),
                    "languages": (None, json.dumps(languages), "application/json"),
                    "sort": (None, json.dumps(sort), "application/json"),
                },
                timeout=API_TIMEOUT,
                headers={"User-Agent": "AytoRural-Monitor/2.0"}
            )
            response.raise_for_status()

            data = response.json()
            results = data.get('results', [])
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

    def process_search_results(self, results: List[dict], only_new: bool = True, strict_rural_filter: bool = True) -> List[dict]:
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

            # Verificar relevancia si el filtro estricto está activado
            if strict_rural_filter and not self._is_relevant_to_municipality(call):
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
