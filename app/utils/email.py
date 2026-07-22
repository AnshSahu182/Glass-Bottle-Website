"""
Email utilities
OTP generation, storage, and email sending
"""
import os
import random
import string
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def generate_otp(length: int = 6) -> str:
    """
    Generate a random OTP
    
    Args:
        length: Length of OTP (default 6 digits)
    
    Returns:
        OTP string
    """
    return ''.join(random.choices(string.digits, k=length))


def send_otp_email(recipient_email: str, otp: str, user_name: str = "User") -> bool:
    """
    Send OTP to user's email address
    
    Args:
        recipient_email: Email address to send OTP to
        otp: OTP string
        user_name: User's name for personalization
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        # Email content
        subject = "Glass Bottles - Email Verification Code"
        otp_expiry_minutes = int(os.getenv("OTP_EXPIRY_MINUTES", 10))
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px;">
                    <h2 style="color: #333; text-align: center;">Email Verification</h2>
                    <p>Hi {user_name},</p>
                    <p>Thank you for signing up with Glass Bottles! To complete your registration, please use the verification code below:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <p style="font-size: 32px; font-weight: bold; color: #007bff; letter-spacing: 5px;">{otp}</p>
                    </div>
                    <p>This code will expire in {otp_expiry_minutes} minutes.</p>
                    <p>If you didn't create this account, please ignore this email.</p>
                    <p style="color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
                        © 2026 Glass Bottles. All rights reserved.
                    </p>
                </div>
            </body>
        </html>
        """
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = os.getenv("MAIL_DEFAULT_SENDER", "noreply@glassbottles.com")
        msg['To'] = recipient_email
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email via SMTP
        server = smtplib.SMTP(
            os.getenv("MAIL_SERVER", "smtp.gmail.com"),
            int(os.getenv("MAIL_PORT", 587))
        )
        server.starttls()
        server.login(
            os.getenv("MAIL_USERNAME"),
            os.getenv("MAIL_PASSWORD")
        )
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


def send_order_confirmation_email(recipient_email: str, order_id: str, user_name: str = "User") -> bool:
    """
    Send order confirmation email to user
    
    Args:
        recipient_email: Email address to send to
        order_id: Order ID
        user_name: User's name for personalization
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        subject = f"Glass Bottles - Order Confirmation #{order_id}"
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px;">
                    <h2 style="color: #333; text-align: center;">Order Confirmed!</h2>
                    <p>Hi {user_name},</p>
                    <p>Thank you for your order! We've received your order and it's being processed.</p>
                    <p><strong>Order ID:</strong> {order_id}</p>
                    <p>You'll receive updates about your order status via email.</p>
                    <p style="color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
                        © 2026 Glass Bottles. All rights reserved.
                    </p>
                </div>
            </body>
        </html>
        """
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = os.getenv("MAIL_DEFAULT_SENDER", "noreply@glassbottles.com")
        msg['To'] = recipient_email
        
        msg.attach(MIMEText(html_body, 'html'))
        
        server = smtplib.SMTP(
            os.getenv("MAIL_SERVER", "smtp.gmail.com"),
            int(os.getenv("MAIL_PORT", 587))
        )
        server.starttls()
        server.login(
            os.getenv("MAIL_USERNAME"),
            os.getenv("MAIL_PASSWORD")
        )
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False
