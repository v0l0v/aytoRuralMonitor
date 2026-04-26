"""
Servicio de notificaciones por WhatsApp y Telegram
Envía resúmenes ejecutivos de convocatorias europeas
"""

import logging
from typing import Optional, List
from datetime import datetime
import requests
from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_RECIPIENTS,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_NUMBER,
    WHATSAPP_RECIPIENTS,
    MUNICIPALITY_CONFIG,
)

logger = logging.getLogger(__name__)


class NotificationService:
    """Servicio centralizado para enviar notificaciones"""

    def __init__(self):
        self.telegram_enabled = bool(TELEGRAM_BOT_TOKEN)
        self.whatsapp_enabled = bool(TWILIO_ACCOUNT_SID)
        self.municipality_name = MUNICIPALITY_CONFIG.get("name", "Municipio")

    def send_notifications(
        self, call_summary: dict, notification_method: str = "both"
    ) -> bool:
        """
        Envía notificación a todos los destinatarios configurados
        notification_method: 'telegram', 'whatsapp' o 'both'
        """
        message = self._format_message(call_summary)
        success = True

        if notification_method in ("telegram", "both"):
            if self.telegram_enabled:
                for chat_id in TELEGRAM_RECIPIENTS:
                    success &= self._send_telegram(
                        chat_id, message, f"Destinatario TG ({chat_id})"
                    )
            else:
                logger.warning("Telegram no está configurado")

        if notification_method in ("whatsapp", "both"):
            if self.whatsapp_enabled:
                for phone_number in WHATSAPP_RECIPIENTS:
                    success &= self._send_whatsapp(
                        phone_number, message, f"Destinatario WA ({phone_number})"
                    )
            else:
                logger.warning("WhatsApp/Twilio no está configurado")

        return success

    def _format_message(self, call_summary: dict) -> str:
        """Formatea el resumen ejecutivo de la convocatoria"""
        template = f"""
🎯 *CONVOCATORIA EUROPEA - {self.municipality_name.upper()}*

📢 *{call_summary.get('title', 'Convocatoria')}*

💰 *Dotación:* {call_summary.get('budget', 'N/A')}

📅 *Plazo:* {call_summary.get('deadline', 'Por confirmar')}

📋 *Resumen:*
{call_summary.get('summary', 'Sin descripción disponible')}

🎯 *Perfil del municipio:*
• Población: {MUNICIPALITY_CONFIG.get('population')} habitantes
• Comunidad: {MUNICIPALITY_CONFIG.get('autonomous_community')}

🔗 *Enlace:* {call_summary.get('url', 'N/A')}

⏰ *Detectado:* {datetime.now().strftime('%d/%m/%Y %H:%M')}

⚡ *ACCIÓN RECOMENDADA:*
1. Revisar documentación completa
2. Contactar con asesor de subvenciones
3. Convocar reunión de coordinación
"""
        return template.strip()

    def _send_telegram(self, chat_id: str, message: str, recipient: str) -> bool:
        """Envía mensaje por Telegram"""
        if not chat_id:
            logger.warning(f"No hay chat_id configurado para {recipient}")
            return False

        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown",
            }
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"✅ Notificación Telegram enviada a {recipient}")
            return True
        except Exception as e:
            logger.error(f"❌ Error enviando Telegram a {recipient}: {str(e)}")
            return False

    def _send_whatsapp(self, phone_number: str, message: str, recipient: str) -> bool:
        """Envía mensaje por WhatsApp usando Twilio"""
        if not phone_number:
            logger.warning(f"No hay número de WhatsApp configurado para {recipient}")
            return False

        try:
            from twilio.rest import Client

            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            message_obj = client.messages.create(
                from_=TWILIO_WHATSAPP_NUMBER,
                to=phone_number,
                body=message,
            )
            logger.info(
                f"✅ Notificación WhatsApp enviada a {recipient} (SID: {message_obj.sid})"
            )
            return True
        except Exception as e:
            logger.error(f"❌ Error enviando WhatsApp a {recipient}: {str(e)}")
            return False

    def send_test_message(self, notification_method: str = "both") -> bool:
        """Envía un mensaje de prueba para validar la configuración"""
        test_call = {
            "title": "PRUEBA - Convocatoria de Ejemplo",
            "budget": "€ 100.000 - € 500.000",
            "deadline": "31/12/2026",
            "summary": "Este es un mensaje de prueba para verificar que la configuración de notificaciones funciona correctamente.",
            "url": "https://data.europa.eu",
        }
        logger.info("📤 Enviando mensaje de prueba...")
        return self.send_notifications(test_call, notification_method)


# Función helper
def notify_new_call(call_data: dict, method: str = "both") -> bool:
    """Función simplificada para enviar una notificación"""
    service = NotificationService()
    return service.send_notifications(call_data, method)
