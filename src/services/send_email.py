from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from pathlib import Path

import aiosmtplib

from schemas.user import UserCreate

from core.settings import settings

TEMPLATES_DIR = Path(__file__).parent / 'templates'


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

    message.set_content('Ваш почтовый клиент не поддерживает HTML-письма.')
    message.add_alternative(body, subtype='html')

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
    body = html.format(text=f'Пользователь {user.username} зарегистрирован!')
    await send_email(
        to=user.email,
        subject='Регистрация пользователя',
        body=body,
    )
