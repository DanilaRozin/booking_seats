import smtplib
from email.message import EmailMessage
from email.utils import formatdate, make_msgid

from core.settings import settings


def _send_email(to_addr: str, subject: str, body_text: str, body_html: str) -> None:
    """Отправляет письмо через SMTP.

    Args:
        to_addr (str): Почтовый адрес получателя.
        subject (str): Тема письма.
        body_text (str): Текст письма, если html отключён.
        body_html (str): Тело письма.

    """
    message = EmailMessage()
    message['From'] = settings.smtp_from
    message['To'] = to_addr
    message['Subject'] = subject
    message['Date'] = formatdate(localtime=True)
    message['Message-ID'] = make_msgid()

    message.set_content(body_text)
    message.add_alternative(body_html, subtype='html')

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_from, settings.smtp_password)
        server.send_message(message)
