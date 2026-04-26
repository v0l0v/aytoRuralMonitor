from notification_service import NotificationService
from dotenv import load_dotenv

load_dotenv()
service = NotificationService()
success = service.send_test_message('telegram')
if success:
    print("Test message sent successfully to group!")
else:
    print("Failed to send test message.")
