import smtplib
from email.message import EmailMessage
from email.utils import formatdate, make_msgid

from core.settings import settings

SMTP_CONNECT_TIMEOUT = 10


def _send_email(
    to_addr: str,
    subject: str,
    body_text: str,
    body_html: str | None = None,
) -> None:
    """Отправляет письмо через SMTP.

    Args:
        to_addr (str): Почтовый адрес получателя.
        subject (str): Тема письма.
        body_text (str): Текст письма, если html отключён.
        body_html (str | None): Тело письма.

    """
    message = EmailMessage()
    message['From'] = settings.smtp.login
    message['To'] = to_addr
    message['Subject'] = subject
    message['Date'] = formatdate(localtime=True)
    message['Message-ID'] = make_msgid()

    message.set_content(body_text)
    if body_html is not None:
        message.add_alternative(body_html, subtype='html')

    with smtplib.SMTP(
        settings.smtp.host,
        settings.smtp.port,
        timeout=SMTP_CONNECT_TIMEOUT,
    ) as server:
        server.starttls()
        server.login(settings.smtp.login, settings.smtp.password.get_secret_value())
        server.send_message(message)
