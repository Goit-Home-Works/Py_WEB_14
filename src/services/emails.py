import logging
from pathlib import Path

from pydantic import EmailStr
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

from config.config import settings
from services.auth import auth_service

logger = logging.getLogger(f"{settings.app_name}.{__name__}")

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)

async def send_email(email: EmailStr, username: str, host: str):
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={
                "token": token_verification,
                "host": host,
                "username": username,
            },
            subtype=MessageType.html,
        )
        logger.debug(message)

        fm = FastMail(conf)
        await fm.send_message(message, template_name="confirm_email.html")
    except ConnectionError as err:
        logger.error(err)
        return None
    return {"message": "email has been set to sending query"}
#
# ...............................................................

# import os
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail
#
#
# async def send_email(email: EmailStr, username: str, host: str):
#     try:
#         token_verification = auth_service.create_email_token({"sub": email})
#
#         # file_path = ".templates/confirm_email.html" 
#         # print(f"File path: {file_path}")
#
#         # with open(file_path, "r") as file:  
#         #     html_content = file.read()
#
#         # Replace placeholders with actual values
#         html_content = html_content.replace("{username}", username)
#         html_content = html_content.replace("{host}", host)
#         html_content = html_content.replace("{token_verification}", token_verification)
#         print(f"{html_content=}")
#         message = Mail(
#             from_email=settings.mail_from,
#             to_emails=email,
#             subject="Confirm your email",
#             html_content=html_content,
#         )
#         print(f"{message=}")
#
#         sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
#         response = sg.send(message)
#
#         if response.status_code == 202:
#             return {"message": "email has been set to sending query"}
#         else:
#             logger.error(
#                 f"Failed to send email. Status code: {response.status_code}, Body: {response.body}"
#             )
#             return None
#     except Exception as e:
#         logger.error(f"An error occurred: {str(e)}")
#         return None


# ........................................................................
