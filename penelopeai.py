#!/usr/bin/env python
# coding: utf-8

import imaplib
import email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import openai
import requests
import os
from flask import Flask

# Configurações para os servidores de e-mail
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ACCOUNT = os.getenv('EMAIL_ACCOUNT')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# Configurações da API da OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

def ler_emails():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select('inbox')

        status, messages = mail.search(None, 'UNSEEN')
        email_ids = messages[0].split()

        emails = []
        for e_id in email_ids:
            status, msg_data = mail.fetch(e_id, '(RFC822)')
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain':
                        emails.append({
                            'from': msg['From'],
                            'subject': msg['Subject'],
                            'body': part.get_payload(decode=True).decode()
                        })
            else:
                emails.append({
                    'from': msg['From'],
                    'subject': msg['Subject'],
                    'body': msg.get_payload(decode=True).decode()
                })

        mail.logout()
        return emails
    except Exception as e:
        print(f"Erro ao ler e-mails: {e}")
        return []

def gerar_imagens(prompt):
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=4,
            size="256x256"
        )
        return [img['url'] for img in response['data']]
    except Exception as e:
        print(f"Erro ao gerar imagens: {e}")
        return []

def enviar_email(destinatario, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ACCOUNT
        msg['To'] = destinatario
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ACCOUNT, destinatario, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

def main():
    emails = ler_emails()
    for email_data in emails:
        prompt = email_data['body']
        imagens_urls = gerar_imagens(prompt)

        body = f"Olá,\n\nAqui estão as imagens geradas com base no seu e-mail:\n\n"
        for url in imagens_urls:
            body += f"{url}\n\n"

        enviar_email(email_data['from'], f"Re: {email_data['subject']}", body)

app = Flask(__name__)

@app.route("/")
def home():
    return "Projeto do notebook rodando no Azure!"

@app.route("processar")
def processar():
    return "Processamento concluído!"

if __name__ == "__main__":
    main()
    app.run(host="0.0.0.0", port=8000)
