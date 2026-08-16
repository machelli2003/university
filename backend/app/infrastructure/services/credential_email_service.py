"""
Credential Email Service

Handles sending credential-related emails to applicants and students.
Supports:
- PIN + Serial after application form purchase
- Real credentials after admission decision
- Password reset links
- Email verification
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from jinja2 import Template

logger = logging.getLogger(__name__)


class CredentialEmailService:
    """
    Service for sending credential-related emails.
    
    This service provides methods to send various credential notifications
    to applicants and students.
    """
    
    def __init__(self):
        """Initialize email service"""
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL", "noreply@university.edu.gh")
        self.sender_password = os.getenv("SENDER_PASSWORD", "")
        self.university_name = os.getenv("UNIVERSITY_NAME", "University")
        self.support_email = os.getenv("SUPPORT_EMAIL", "support@university.edu.gh")
        self.logo_url = os.getenv("UNIVERSITY_LOGO_URL", "")
        self.web_url = os.getenv("WEB_URL", "https://university.edu.gh")
    
    async def send_application_form_credentials(
        self,
        recipient_email: str,
        first_name: str,
        pin: str,
        serial_number: str,
    ) -> bool:
        """
        Send PIN and Serial number after application form purchase.
        
        Args:
            recipient_email: Recipient's email
            first_name: Recipient's first name
            pin: Generated 6-digit PIN
            serial_number: Generated 8-character Serial
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            subject = "Your Application Form Credentials"
            
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; background: #f9f9f9; padding: 20px; border-radius: 8px;">
                        {self._header_section()}
                        
                        <h2 style="color: #0066cc; margin-top: 30px;">Application Form Purchase Successful</h2>
                        
                        <p>Dear {first_name},</p>
                        
                        <p>Thank you for purchasing your application form. Below are your login credentials:</p>
                        
                        <div style="background: #fff; border: 2px solid #0066cc; border-radius: 8px; padding: 20px; margin: 20px 0;">
                            <p style="font-size: 12px; color: #666; margin: 0 0 10px 0;">YOUR PIN AND SERIAL NUMBER</p>
                            
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                                <div>
                                    <label style="font-size: 12px; color: #999; text-transform: uppercase;">PIN</label>
                                    <div style="font-size: 28px; font-weight: bold; color: #0066cc; letter-spacing: 2px; font-family: monospace;">
                                        {pin}
                                    </div>
                                </div>
                                <div>
                                    <label style="font-size: 12px; color: #999; text-transform: uppercase;">SERIAL</label>
                                    <div style="font-size: 28px; font-weight: bold; color: #0066cc; letter-spacing: 2px; font-family: monospace;">
                                        {serial_number}
                                    </div>
                                </div>
                            </div>
                            
                            <p style="font-size: 12px; color: #999; margin: 0; border-top: 1px solid #eee; padding-top: 10px;">
                                Keep these credentials safe. You'll need them to login to the application portal.
                            </p>
                        </div>
                        
                        <h3 style="color: #333; margin-top: 30px;">Next Steps:</h3>
                        <ol style="color: #666;">
                            <li>Visit the application portal at <a href="{self.web_url}" style="color: #0066cc;">{self.web_url}</a></li>
                            <li>Select "Application Form Login"</li>
                            <li>Enter your PIN, Serial Number, and email address</li>
                            <li>Fill out and submit your application</li>
                        </ol>
                        
                        <div style="background: #e8f4f8; border-left: 4px solid #0066cc; padding: 15px; margin: 20px 0;">
                            <p style="margin: 0; color: #0066cc; font-weight: bold;">Important Reminders:</p>
                            <ul style="margin: 5px 0; color: #666;">
                                <li>The PIN and Serial can only be used once</li>
                                <li>Ensure all your information is accurate before submitting</li>
                                <li>The application deadline is <strong>[deadline date]</strong></li>
                            </ul>
                        </div>
                        
                        {self._support_section()}
                        {self._footer_section()}
                    </div>
                </body>
            </html>
            """
            
            await self._send_email(recipient_email, subject, html_body)
            logger.info(f"Application form credentials sent to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send application form credentials to {recipient_email}: {e}")
            return False
    
    async def send_real_credentials(
        self,
        recipient_email: str,
        first_name: str,
        username: str,
        temporary_password: str,
        activation_deadline: datetime,
    ) -> bool:
        """
        Send real credentials after admission decision (OFFERED).
        
        Args:
            recipient_email: Recipient's email
            first_name: Recipient's first name
            username: Generated username
            temporary_password: Temporary password (must change on first login)
            activation_deadline: Deadline to activate account
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            subject = f"Congratulations! Your {self.university_name} Account Credentials"
            
            deadline_str = activation_deadline.strftime("%B %d, %Y")
            
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; background: #f9f9f9; padding: 20px; border-radius: 8px;">
                        {self._header_section()}
                        
                        <h2 style="color: #22b14c; margin-top: 30px;">🎉 You Have Been Offered Admission!</h2>
                        
                        <p>Dear {first_name},</p>
                        
                        <p>Congratulations! You have been <strong>OFFERED ADMISSION</strong> to {self.university_name}.</p>
                        
                        <p>Below are your account credentials for the student portal:</p>
                        
                        <div style="background: #fff; border: 2px solid #22b14c; border-radius: 8px; padding: 20px; margin: 20px 0;">
                            <p style="font-size: 12px; color: #666; margin: 0 0 15px 0;">YOUR ACCOUNT CREDENTIALS</p>
                            
                            <div style="margin-bottom: 15px;">
                                <label style="font-size: 12px; color: #999; text-transform: uppercase;">Username</label>
                                <div style="font-size: 18px; font-weight: bold; color: #22b14c; letter-spacing: 1px; font-family: monospace; background: #f0f0f0; padding: 10px; border-radius: 4px;">
                                    {username}
                                </div>
                            </div>
                            
                            <div style="margin-bottom: 15px;">
                                <label style="font-size: 12px; color: #999; text-transform: uppercase;">Temporary Password</label>
                                <div style="font-size: 18px; font-weight: bold; color: #22b14c; letter-spacing: 1px; font-family: monospace; background: #f0f0f0; padding: 10px; border-radius: 4px;">
                                    {temporary_password}
                                </div>
                            </div>
                            
                            <p style="font-size: 12px; color: #f00; margin: 0; border-top: 1px solid #eee; padding-top: 10px;">
                                <strong>Important:</strong> On your first login, you MUST change this temporary password to a permanent one that only you know.
                            </p>
                        </div>
                        
                        <h3 style="color: #333; margin-top: 30px;">How to Access Your Account:</h3>
                        <ol style="color: #666;">
                            <li>Go to <a href="{self.web_url}/student/login" style="color: #22b14c;">{self.web_url}/student/login</a></li>
                            <li>Click "Student Portal Login"</li>
                            <li>Enter your username and temporary password</li>
                            <li>Change your password when prompted</li>
                            <li>Start registering for courses</li>
                        </ol>
                        
                        <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0;">
                            <p style="margin: 0; color: #856404; font-weight: bold;">⏰ Activation Deadline</p>
                            <p style="margin: 5px 0; color: #856404;">
                                You must activate your account by <strong>{deadline_str}</strong>. 
                                After this date, you may lose access to registration.
                            </p>
                        </div>
                        
                        <div style="background: #f0f7ff; border-left: 4px solid #0066cc; padding: 15px; margin: 20px 0;">
                            <p style="margin: 0; color: #004085; font-weight: bold;">📋 What's Next?</p>
                            <ul style="margin: 5px 0; color: #004085;">
                                <li>Review your program requirements</li>
                                <li>Check important dates and deadlines</li>
                                <li>Register for your courses</li>
                                <li>Review accommodation options (if available)</li>
                                <li>Pay any outstanding fees</li>
                            </ul>
                        </div>
                        
                        {self._support_section()}
                        {self._footer_section()}
                    </div>
                </body>
            </html>
            """
            
            await self._send_email(recipient_email, subject, html_body)
            logger.info(f"Real credentials sent to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send real credentials to {recipient_email}: {e}")
            return False
    
    async def send_password_reset_link(
        self,
        recipient_email: str,
        first_name: str,
        reset_token: str,
        expires_in_hours: int = 24,
    ) -> bool:
        """
        Send password reset link.
        
        Args:
            recipient_email: Recipient's email
            first_name: Recipient's first name
            reset_token: Password reset token
            expires_in_hours: How many hours the link is valid
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            subject = "Password Reset Request"
            
            reset_url = f"{self.web_url}/reset-password?token={reset_token}"
            
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; background: #f9f9f9; padding: 20px; border-radius: 8px;">
                        {self._header_section()}
                        
                        <h2 style="color: #d9534f; margin-top: 30px;">Password Reset Request</h2>
                        
                        <p>Dear {first_name},</p>
                        
                        <p>We received a request to reset your password. Click the button below to proceed:</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{reset_url}" style="display: inline-block; background: #d9534f; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; font-weight: bold;">
                                Reset Password
                            </a>
                        </div>
                        
                        <p style="color: #666; font-size: 12px;">
                            Or copy this link: <a href="{reset_url}" style="color: #0066cc; word-break: break-all;">{reset_url}</a>
                        </p>
                        
                        <div style="background: #fde7e7; border-left: 4px solid #d9534f; padding: 15px; margin: 20px 0;">
                            <p style="margin: 0; color: #a94442; font-weight: bold;">Security Notice</p>
                            <ul style="margin: 5px 0; color: #a94442; font-size: 12px;">
                                <li>This link expires in {expires_in_hours} hours</li>
                                <li>Only use this link if you requested a password reset</li>
                                <li>If you didn't request this, ignore this email</li>
                                <li>Never share this link with anyone</li>
                            </ul>
                        </div>
                        
                        {self._support_section()}
                        {self._footer_section()}
                    </div>
                </body>
            </html>
            """
            
            await self._send_email(recipient_email, subject, html_body)
            logger.info(f"Password reset link sent to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send password reset link to {recipient_email}: {e}")
            return False
    
    def _header_section(self) -> str:
        """Get email header section"""
        logo_html = f'<img src="{self.logo_url}" alt="{self.university_name}" style="height: 50px; margin-bottom: 20px;">' if self.logo_url else ""
        
        return f"""
        <div style="text-align: center; border-bottom: 2px solid #0066cc; padding-bottom: 20px; margin-bottom: 30px;">
            {logo_html}
            <h1 style="color: #0066cc; margin: 0;">{self.university_name}</h1>
            <p style="color: #666; margin: 5px 0 0 0; font-size: 12px;">Admissions Portal</p>
        </div>
        """
    
    def _support_section(self) -> str:
        """Get email support section"""
        return f"""
        <div style="border-top: 1px solid #ddd; padding-top: 20px; margin-top: 30px;">
            <h4 style="color: #333; margin-top: 0;">Need Help?</h4>
            <p style="color: #666; font-size: 14px; margin: 0;">
                If you have any questions or need assistance, contact us at:
            </p>
            <p style="color: #0066cc; font-weight: bold; margin: 5px 0 0 0;">
                📧 {self.support_email}
            </p>
        </div>
        """
    
    def _footer_section(self) -> str:
        """Get email footer section"""
        return f"""
        <div style="border-top: 1px solid #ddd; padding-top: 20px; margin-top: 30px; text-align: center;">
            <p style="color: #999; font-size: 11px; margin: 0;">
                © {datetime.now().year} {self.university_name}. All rights reserved.
            </p>
            <p style="color: #999; font-size: 11px; margin: 5px 0 0 0;">
                This is an automated email. Please do not reply directly.
            </p>
        </div>
        """
    
    async def _send_email(
        self,
        recipient_email: str,
        subject: str,
        html_body: str,
        plain_text: Optional[str] = None,
    ) -> bool:
        """
        Actually send the email.
        
        In production, this would use SMTP or a service like SendGrid.
        For now, we log it and would need proper email setup.
        
        Args:
            recipient_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            plain_text: Plain text alternative
        
        Returns:
            True if sent successfully
        """
        try:
            # TODO: Implement actual email sending via SMTP or SendGrid
            # For now, just log that we would send it
            logger.info(f"""
            ═════════════════════════════════════════════════════
            📧 EMAIL WOULD BE SENT
            ═════════════════════════════════════════════════════
            To: {recipient_email}
            Subject: {subject}
            ─────────────────────────────────────────────────────
            {html_body[:200]}... [truncated]
            ═════════════════════════════════════════════════════
            """)
            
            # In production, implement real email sending here
            # Example with smtplib:
            # import smtplib
            # from email.mime.multipart import MIMEMultipart
            # from email.mime.text import MIMEText
            # 
            # msg = MIMEMultipart("alternative")
            # msg["Subject"] = subject
            # msg["From"] = self.sender_email
            # msg["To"] = recipient_email
            # 
            # msg.attach(MIMEText(plain_text or "", "plain"))
            # msg.attach(MIMEText(html_body, "html"))
            # 
            # with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            #     server.starttls()
            #     server.login(self.sender_email, self.sender_password)
            #     server.sendmail(self.sender_email, recipient_email, msg.as_string())
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {recipient_email}: {e}")
            return False
