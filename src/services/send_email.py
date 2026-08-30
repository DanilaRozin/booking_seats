from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from pathlib import Path

import aiosmtplib
from aiosmtplib.errors import SMTPException
from loguru import logger

from schemas.user import UserCreate

from core.settings import settings

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
    try:
        await aiosmtplib.send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_from,
            password=settings.smtp_password,
            use_tls=True,
        )
        logger.info(f'Сообщение отправлено на {to}')
    except SMTPException:
        logger.exception(f'Ошибка при отправке сообщения на {to}.')


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
