from typing import List, Optional

from fastapi import UploadFile
from fastapi_mail import (
    ConnectionConfig,
    FastMail,
    MessageSchema,
    MessageType,
    NameEmail,
)
from pydantic import BaseModel

from .settings import get_settings
from .logger import get_logger
import os

# Template Directory
TEMPLATE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__package__)), "app", "static", "mails"
)


# Environment Vars
SETTINGS = get_settings()

# Logger
logger = get_logger(__name__)


class MailSchematic(BaseModel):
    """
    Schema for email details.
    """

    email: List[
        NameEmail
    ]  # Supports both "user@example.com" and "Name <user@example.com>" formats


def get_mail_config() -> ConnectionConfig:
    """
    Get mail server configuration.

    :return: ConnectionConfig object with mail server settings
    :rtype: ConnectionConfig
    """
    mail_config = ConnectionConfig(
        MAIL_USERNAME=SETTINGS.SMTP_USERNAME,
        MAIL_FROM=SETTINGS.EMAIL_FROM,
        MAIL_PASSWORD=SETTINGS.SMTP_PASSWORD,
        MAIL_PORT=SETTINGS.SMTP_PORT,
        MAIL_SERVER=SETTINGS.SMTP_SERVER,
        MAIL_STARTTLS=SETTINGS.SMTP_STARTTLS,
        MAIL_SSL_TLS=SETTINGS.SMTP_SSL_TLS,
        USE_CREDENTIALS=SETTINGS.SMTP_USE_CREDENTIALS,
        VALIDATE_CERTS=SETTINGS.SMTP_VALIDATE_CERTS,
        TEMPLATE_FOLDER=TEMPLATE_DIR,
    )
    return mail_config


def get_mailer() -> FastMail:
    """
    Get FastMail instance for sending emails.

    :return: FastMail instance
    :rtype: FastMail
    """
    mail_config = get_mail_config()
    fast_mail = FastMail(mail_config)
    return fast_mail


def create_email_message(
    subject: str,
    recipients: List[NameEmail],
    body: str,
    files: Optional[List[UploadFile]] = None,
    subtype: MessageType = MessageType.html,
) -> MessageSchema:
    """
    Create an email message schema.

    :param subject: Subject of the email
    :type subject: str
    :param recipients: List of recipient email addresses
    :type recipients: List[NameEmail]
    :param body: Body content of the email
    :type body: str
    :param files: Optional list of files to attach
    :type files: Optional[List[UploadFile]], optional
    :param subtype: Message type (html or plain), defaults to MessageType.html
    :type subtype: MessageType, optional
    :return: MessageSchema object representing the email
    :rtype: MessageSchema
    """
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype=subtype,
        attachments=files,
    )
    return message


def create_email_template_message(
    subject: str,
    recipients: List[NameEmail],
    body: dict,
    template_name: Optional[str] = None,
    files: Optional[List[UploadFile]] = None,
    subtype: MessageType = MessageType.html,
) -> MessageSchema:
    """
    Create an email message schema with template body.

    :param subject: Subject of the email
    :type subject: str
    :param recipients: List of recipient email addresses
    :type recipients: List[NameEmail]
    :param body: Template body content of the email
    :type body: Dict[str, str | List | Dict | bool | float | int | None]
    :param template_name: Optional template file name (relative to TEMPLATE_FOLDER)
    :type template_name: Optional[str], optional
    :param files: Optional list of files to attach
    :type files: Optional[List[UploadFile]], optional
    :param subtype: Message type (html or plain), defaults to MessageType.html
    :type subtype: MessageType, optional
    :return: MessageSchema object representing the email
    :rtype: MessageSchema
    """
    try:
        message_params = {
            "subject": subject,
            "recipients": recipients,
            "template_body": body,
            "subtype": subtype,
            "attachments": files if files else [],
        }

        # Only add template_name if it's provided
        if template_name:
            message_params["template_name"] = template_name

        message = MessageSchema(**message_params)
        return message
    except Exception as e:
        logger.error("Error creating email template message: %s", e)
        raise e
