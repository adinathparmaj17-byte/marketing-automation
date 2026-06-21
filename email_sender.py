"""
Email sending module.
Uses SMTP (Gmail by default) to send personalized emails.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_ADDRESS, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT, EMAIL_SUBJECT


def send_email(name, to_email, message_body, logger):
    """
    Send a personalized email to one recipient.
    
    Args:
        name (str): Recipient's name for personalization
        to_email (str): Recipient's email address
        message_body (str): Email body content
        logger: Logger instance for recording results
    
    Returns:
        bool: True if sent successfully, False if failed
    """
    
    try:
        # Validate inputs
        if not to_email or "@" not in str(to_email):
            logger.warning(f"SKIP EMAIL | Invalid email for {name}: '{to_email}'")
            return False
        
        if not message_body or str(message_body).strip() == "":
            logger.warning(f"SKIP EMAIL | Empty message for {name} ({to_email})")
            return False
        
        # Personalize the message — replace {name} placeholder
        personalized_message = str(message_body).replace("{name}", str(name))
        
        # Build the email
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = EMAIL_SUBJECT.replace("{name}", str(name))
        
        # Create HTML body for better formatting
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <p>Hi {name},</p>
            <p>{personalized_message}</p>
            <br>
            <p style="color: #666; font-size: 12px;">
                If you wish to unsubscribe, please reply with "STOP".
            </p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, "html"))
        
        # Connect to SMTP server and send
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Enable encryption
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"EMAIL SENT  | To: {to_email} | Name: {name}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        logger.error(f"EMAIL FAIL  | Authentication failed. Check email/password in .env")
        return False
        
    except smtplib.SMTPRecipientsRefused:
        logger.error(f"EMAIL FAIL  | Recipient refused: {to_email}")
        return False
        
    except Exception as e:
        logger.error(f"EMAIL FAIL  | To: {to_email} | Error: {str(e)}")
        return False
