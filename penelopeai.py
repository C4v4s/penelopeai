#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('pipx install tweepy openai requests')


# In[ ]:


import imaplib
import email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import openai
import requests

# Configurações para os servidores de e-mail
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ACCOUNT = 'spidermanfsta@gmail.com'
EMAIL_PASSWORD = 'Tatubolafsa1'

# Configurações da API da OpenAI
OPENAI_API_KEY = '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'
openai.api_key = OPENAI_API_KEY


# In[ ]:


def ler_emails():
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


# In[ ]:


def gerar_imagens(prompt):
    response = openai.Image.create(
        prompt=prompt,
        n=4,
        size="256x256"
    )
    return [img['url'] for img in response['data']]


# In[ ]:


def enviar_email(destinatario, subject, body):
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


# In[ ]:


def main():
    emails = ler_emails()
    for email_data in emails:
        prompt = email_data['body']
        imagens_urls = gerar_imagens(prompt)
        
        body = f"Olá,\n\nAqui estão as imagens geradas com base no seu e-mail:\n\n"
        for url in imagens_urls:
            body += f"{url}\n\n"
        
        enviar_email(email_data['from'], f"Re: {email_data['subject']}", body)


# In[ ]:


from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Projeto do notebook rodando no Azure!"

if __name__ == "__main__":
    main()
    app.run(host="0.0.0.0", port=8000)


# In[ ]:


get_ipython().system('jupyter nbconvert --to script penelopeai.ipynb')

