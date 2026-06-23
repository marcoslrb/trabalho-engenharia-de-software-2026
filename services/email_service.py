"""
services/email_service.py
Camada de serviço para envio de e-mails — desacoplada da interface.
RF15, RF16 — Notificações de protocolo e status.

Por padrão (EMAIL_ENABLED=false), todas as notificações são logadas no console.
Para ativar: defina EMAIL_ENABLED=true e as variáveis SMTP no ambiente.
"""

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config.settings import (
    EMAIL_ENABLED, EMAIL_HOST, EMAIL_PORT,
    EMAIL_USER, EMAIL_PASSWORD, EMAIL_FROM, EMAIL_FROM_NAME,
)

logger = logging.getLogger(__name__)


def _enviar_smtp(destinatario: str, assunto: str, corpo_html: str) -> bool:
    """Envia e-mail via SMTP. Retorna True em sucesso, False em falha."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = assunto
        msg["From"] = f"{EMAIL_FROM_NAME} <{EMAIL_FROM}>"
        msg["To"] = destinatario
        msg.attach(MIMEText(corpo_html, "html", "utf-8"))

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, [destinatario], msg.as_string())

        logger.info("E-mail enviado para %s | Assunto: %s", destinatario, assunto)
        return True
    except Exception as e:
        logger.error("Falha ao enviar e-mail para %s: %s", destinatario, e)
        return False


def _log_email(destinatario: str, assunto: str, corpo: str) -> None:
    """Simula envio logando no console (modo desenvolvimento)."""
    logger.info(
        "\n=== [EMAIL SIMULADO] ===\n"
        "Para: %s\nAssunto: %s\n\n%s\n"
        "=======================",
        destinatario, assunto, corpo,
    )


def enviar(destinatario: str, assunto: str, corpo_html: str) -> bool:
    """
    Ponto de entrada principal para envio de e-mail.
    Roteia para SMTP real ou log dependendo de EMAIL_ENABLED.
    Manifestações anônimas nunca chegam aqui — garantido pelo service layer.
    """
    if not destinatario:
        return False  # Silenciosamente ignora (manifestação anônima)

    if EMAIL_ENABLED:
        return _enviar_smtp(destinatario, assunto, corpo_html)
    else:
        _log_email(destinatario, assunto, corpo_html)
        return True


# ── Templates de e-mail ────────────────────────────────────────────────────────

def notificar_protocolo_gerado(email: str, nome: str, protocolo: str) -> bool:
    """RF16 — Envia protocolo por e-mail ao cidadão após registro."""
    assunto = f"[Ouvidoria] Sua manifestação foi registrada — Protocolo {protocolo}"
    corpo = f"""
    <html><body style="font-family: Arial, sans-serif; color: #333;">
    <div style="max-width:600px; margin:auto; padding:24px; border:1px solid #e0e0e0; border-radius:8px;">
      <h2 style="color:#1f77b4;">📋 Manifestação Registrada com Sucesso</h2>
      <p>Olá, <strong>{nome or 'Cidadão'}</strong>!</p>
      <p>Sua manifestação foi recebida pelo Sistema de Ouvidoria.</p>
      <div style="background:#e7f3ff; border-left:4px solid #1f77b4; padding:16px; margin:16px 0; border-radius:4px;">
        <p style="margin:0; font-size:0.9em; color:#555;">Número de Protocolo:</p>
        <h1 style="margin:8px 0; color:#1f77b4; font-family:monospace;">{protocolo}</h1>
      </div>
      <p><strong>Guarde este número</strong> — ele será necessário para acompanhar o andamento da sua manifestação.</p>
      <p style="color:#888; font-size:0.85em;">Este é um e-mail automático. Não responda a esta mensagem.</p>
    </div>
    </body></html>
    """
    return enviar(email, assunto, corpo)


def notificar_atualizacao_status(email: str, nome: str, protocolo: str, status_novo: str) -> bool:
    """RF15 — Notifica o cidadão sobre atualização de status."""
    assunto = f"[Ouvidoria] Sua manifestação foi atualizada — {protocolo}"
    corpo = f"""
    <html><body style="font-family: Arial, sans-serif; color: #333;">
    <div style="max-width:600px; margin:auto; padding:24px; border:1px solid #e0e0e0; border-radius:8px;">
      <h2 style="color:#1f77b4;">🔄 Atualização de Status</h2>
      <p>Olá, <strong>{nome or 'Cidadão'}</strong>!</p>
      <p>A manifestação <strong>{protocolo}</strong> teve seu status atualizado:</p>
      <div style="background:#f0f8f0; border-left:4px solid #28a745; padding:16px; margin:16px 0; border-radius:4px;">
        <p style="margin:0; font-size:1.1em; font-weight:bold; color:#28a745;">{status_novo}</p>
      </div>
      <p>Para acompanhar o histórico completo, acesse o sistema e consulte seu protocolo.</p>
      <p style="color:#888; font-size:0.85em;">Este é um e-mail automático. Não responda a esta mensagem.</p>
    </div>
    </body></html>
    """
    return enviar(email, assunto, corpo)


def notificar_encerramento(email: str, nome: str, protocolo: str, parecer: str) -> bool:
    """RF15 — Notifica o cidadão sobre o encerramento da manifestação."""
    assunto = f"[Ouvidoria] Manifestação encerrada — {protocolo}"
    corpo = f"""
    <html><body style="font-family: Arial, sans-serif; color: #333;">
    <div style="max-width:600px; margin:auto; padding:24px; border:1px solid #e0e0e0; border-radius:8px;">
      <h2 style="color:#28a745;">✅ Manifestação Encerrada</h2>
      <p>Olá, <strong>{nome or 'Cidadão'}</strong>!</p>
      <p>A manifestação <strong>{protocolo}</strong> foi encerrada.</p>
      <div style="background:#f0f8f0; border-left:4px solid #28a745; padding:16px; margin:16px 0; border-radius:4px;">
        <p style="margin:0; font-weight:bold; color:#555; font-size:0.9em;">Parecer de Encerramento:</p>
        <p style="margin:8px 0;">{parecer}</p>
      </div>
      <p>Obrigado por utilizar nossa Ouvidoria. Sua participação é fundamental para a melhoria dos nossos serviços.</p>
      <p style="color:#888; font-size:0.85em;">Este é um e-mail automático. Não responda a esta mensagem.</p>
    </div>
    </body></html>
    """
    return enviar(email, assunto, corpo)
