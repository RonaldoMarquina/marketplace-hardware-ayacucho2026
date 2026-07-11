import smtplib
from email.message import EmailMessage


class EmailService:
    @staticmethod
    def send_verification_email(app, recipient, token):
        frontend_url = app.config.get("FRONTEND_URL") or "http://localhost:5173"
        verification_link = f"{frontend_url}/verificar?token={token}"
        subject = "Verifica tu cuenta"
        body = (
            "Hola,\n\n"
            "Gracias por registrarte en HardwareAyacucho.\n"
            f"Usa este enlace para verificar tu cuenta:\n{verification_link}\n\n"
            "Si no realizaste este registro, puedes ignorar este mensaje.\n"
        )
        EmailService._deliver_email(
            app,
            recipient=recipient,
            subject=subject,
            body=body,
            metadata={
                "kind": "email_verification",
                "token": token,
                "link": verification_link,
            },
        )

    @staticmethod
    def send_password_reset_email(app, recipient, token):
        frontend_url = app.config.get("FRONTEND_URL") or "http://localhost:5173"
        reset_link = f"{frontend_url}/reset-password?token={token}"
        subject = "Recupera tu contrasena"
        body = (
            "Hola,\n\n"
            "Recibimos una solicitud para restablecer tu contrasena.\n"
            f"Usa este enlace para continuar:\n{reset_link}\n\n"
            "Si no solicitaste este cambio, puedes ignorar este mensaje.\n"
        )
        EmailService._deliver_email(
            app,
            recipient=recipient,
            subject=subject,
            body=body,
            metadata={
                "kind": "password_reset",
                "token": token,
                "link": reset_link,
            },
        )

    @staticmethod
    def _deliver_email(app, recipient, subject, body, metadata):
        mode = app.config.get("EMAIL_DELIVERY_MODE", "log")
        prefixed_subject = EmailService._build_subject(app, subject)
        payload = {
            "to": recipient,
            "from": app.config.get("EMAIL_FROM"),
            "subject": prefixed_subject,
            "body": body,
            **metadata,
        }

        if mode == "testing":
            app.extensions.setdefault("mail_outbox", []).append(payload)
            return

        if mode == "log":
            app.logger.info("Correo %s para %s: %s", metadata["kind"], recipient, metadata["link"])
            return

        EmailService._deliver_smtp(app, payload)

    @staticmethod
    def _deliver_smtp(app, payload):
        message = EmailMessage()
        message["Subject"] = payload["subject"]
        message["From"] = payload["from"]
        message["To"] = payload["to"]
        message.set_content(payload["body"])

        smtp_host = app.config["SMTP_HOST"]
        smtp_port = int(app.config["SMTP_PORT"])
        smtp_username = app.config["SMTP_USERNAME"]
        smtp_password = app.config["SMTP_PASSWORD"]
        smtp_timeout = int(app.config.get("SMTP_TIMEOUT_SECONDS", 15))

        if app.config.get("SMTP_USE_SSL"):
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=smtp_timeout) as server:
                server.login(smtp_username, smtp_password)
                server.send_message(message)
            return

        with smtplib.SMTP(smtp_host, smtp_port, timeout=smtp_timeout) as server:
            if app.config.get("SMTP_USE_TLS"):
                server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(message)

    @staticmethod
    def _build_subject(app, subject):
        prefix = app.config.get("EMAIL_SUBJECT_PREFIX", "").strip()
        if not prefix:
            return subject
        return f"{prefix} {subject}"
