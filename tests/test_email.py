import pytest
from unittest.mock import AsyncMock, patch
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager

@pytest.mark.asyncio
@patch('app.utils.smtp_connection.SMTPClient')
async def test_send_email_directly(mock_smtp_client_class):
    # Mock the send_email method inside the SMTPClient class
    mock_send_email = AsyncMock()
    mock_smtp_client_instance = mock_smtp_client_class.return_value
    mock_smtp_client_instance.send_email = mock_send_email
    
    # Now test your email sending logic
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "verification_url": "http://example.com/verify?token=abc123"
    }
    
    # Call your method that uses the SMTPClient (via EmailService)
    template_manager = TemplateManager()
    email_service = EmailService(template_manager)
    
    await email_service.send_user_email(user_data, 'email_verification')
