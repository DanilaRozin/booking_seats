from email.message import EmailMessage
from email.utils import formatdate, make_msgid

import aiosmtplib

from core.settings import settings


async def send_email(to: str, subject: str, body: str) -> None:
    """Отправляет письмо через SMTP.

    Принимает параметры:
    to - почтовый адрес получателя.
    subject - тема письма
    body - Текст письма
    """
    message = EmailMessage()
    message['From'] = settings.smtp_from
    message['To'] = to
    message['Subject'] = subject
    message['Date'] = formatdate(localtime=True)
    message['Message-ID'] = make_msgid()
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_from,
        password=settings.smtp_password,
        use_tls=True,
    )
