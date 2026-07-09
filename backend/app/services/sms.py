"""
KAVACH AI — Generic SMS Notification Service
Clean, pluggable interface for outbound SMS alerts.
"""

import abc
from typing import Dict, Optional
from app.config import get_settings

settings = get_settings()


class SMSProvider(abc.ABC):
    """Abstract Base Class (Interface) for SMS delivery adapters."""

    @abc.abstractmethod
    async def send_sms(
        self,
        phone: str,
        message: str,
        template_id: Optional[str] = None,
        variables: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Sends an SMS to the target destination."""
        pass


class MockSMSProvider(SMSProvider):
    """
    Default Free/Mock SMS Provider for local development & testing.
    Prints alerts to the application server standard output.
    100% Free, requires no signups, DLT registration, or API keys.
    """

    async def send_sms(
        self,
        phone: str,
        message: str,
        template_id: Optional[str] = None,
        variables: Optional[Dict[str, str]] = None,
    ) -> bool:
        import datetime
        import uuid

        time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        req_id = f"KAV-{str(uuid.uuid4())[:8].upper()}"
        
        if template_id:
            alert_category = f"Template Route ({template_id})"
        elif "warning" in message.lower() or "alert" in message.lower() or "suspicious" in message.lower():
            alert_category = "[ALERT] Cyber Threat warning"
        elif "status" in message.lower() or "updated" in message.lower():
            alert_category = "[UPDATE] Case Pipeline Status"
        else:
            alert_category = "[INFO] SMS Announcement"

        print("\n" + "+" + "="*70 + "+")
        print("|                   KAVACH AI -- NOTIFICATION DISPATCH                 |")
        print("+" + "="*70 + "+")
        print("| Channel      : SMS (Mock Gateway)                                   |")
        print(f"| Recipient    : {phone:<53} |")
        print(f"| Category     : {alert_category:<53} |")
        print(f"| Timestamp    : {time_str:<53} |")
        print(f"| Request ID   : {req_id:<53} |")
        print("| Status       : OK (Mock Success - No Credits/DLT required)           |")
        print("+" + "-"*70 + "+")
        print("| Message Content:                                                     |")
        
        # Safe ASCII wrap of message body
        words = message.split()
        current_line = []
        for word in words:
            if len(" ".join(current_line + [word])) <= 64:
                current_line.append(word)
            else:
                line_content = " ".join(current_line)
                print(f"|   {line_content:<66} |")
                current_line = [word]
        if current_line:
            line_content = " ".join(current_line)
            print(f"|   {line_content:<66} |")
            
        print("+" + "="*70 + "+\n")
        return True


class NotificationService:
    """Generic notification supervisor handling channels routing."""

    def __init__(self, provider: SMSProvider):
        self.provider = provider

    async def notify_suspect_alert(self, phone: str, details: str) -> bool:
        """Sends a high priority threat warning to client."""
        body = f"KAVACH AI ALERT: Suspicious activity/threat detected: {details}."
        return await self.provider.send_sms(phone=phone, message=body)

    async def notify_report_update(self, phone: str, case_id: str, status: str) -> bool:
        """Sends user progress notifications concerning their reported case."""
        body = f"KAVACH AI: Your case {case_id} has been updated to status: {status}."
        return await self.provider.send_sms(phone=phone, message=body)

    async def send_custom_alert(self, phone: str, message: str) -> bool:
        """Standard custom dispatch wrapper."""
        return await self.provider.send_sms(phone=phone, message=message)


def get_sms_provider() -> SMSProvider:
    """
    Instantiates the active SMS delivery adapter based on configuration.
    Ready to load TwilioSMSProvider or MSG91SMSProvider dynamically as needed.
    """
    return MockSMSProvider()


def get_notification_service() -> NotificationService:
    """Instantiates the notification manager bound to the active provider."""
    return NotificationService(provider=get_sms_provider())
