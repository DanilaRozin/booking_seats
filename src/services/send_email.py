from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from pathlib import Path

import aiosmtplib

from schemas.user import UserCreate

from core.settings import settings

SMTP_CONNECT_TIMEOUT = 10

TEMPLATES_DIR = Path(__file__).parent / 'templates'


async def send_email(to: str, subject: str, body_text: str, body_html: str) -> None:
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

    message.set_content(body_text)
    message.add_alternative(body_html, subtype='html')

    with smtplib.SMTP(
        settings.smtp.host,
        settings.smtp.port,
        timeout=SMTP_CONNECT_TIMEOUT,
    ) as server:
        server.starttls()
        server.login(settings.smtp.login, settings.smtp.password.get_secret_value())
        server.send_message(message)
    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_from,
        password=settings.smtp_password,
        use_tls=True,
    )


async def email_registration(user: UserCreate) -> None:
    """Функция отпарвки письма о регистрации."""
    html = (TEMPLATES_DIR / 'registration.html').read_text(encoding='utf-8')
    body_text = f'Пользователь {user.username} зарегистрирован!'
    body_html = html.format(text=body_text)
    await send_email(
        to=user.email,
        subject='Регистрация пользователя',
        body_text=body_text,
        body_html=body_html,
    )
