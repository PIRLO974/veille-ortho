"""
Envoi du rapport de veille orthodontique via l'API Gmail (HTTPS/OAuth2).
Lit les credentials depuis les variables d'environnement.
"""

import os
import sys
import base64
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import date

# --- Credentials ---
CLIENT_ID = os.environ.get('GMAIL_CLIENT_ID')
CLIENT_SECRET = os.environ.get('GMAIL_CLIENT_SECRET')
REFRESH_TOKEN = os.environ.get('GMAIL_REFRESH_TOKEN')

if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
    print("Erreur : GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET et GMAIL_REFRESH_TOKEN sont requis.")
    print("Lancez d'abord scripts/setup_gmail_oauth.py pour les obtenir.")
    sys.exit(1)

# --- Obtenir un access token ---
def get_access_token():
    r = requests.post(
        'https://oauth2.googleapis.com/token',
        data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'refresh_token': REFRESH_TOKEN,
            'grant_type': 'refresh_token',
        }
    )
    r.raise_for_status()
    return r.json()['access_token']

# --- Lire le fichier de veille ---
FICHIER = os.path.join(os.path.dirname(__file__), '..', 'output', 'veille_orthodontie_2024_2025.md')
FICHIER = os.path.abspath(FICHIER)

with open(FICHIER, 'r', encoding='utf-8') as f:
    contenu = f.read()

# Extraire la section de cette semaine
lignes = contenu.split('\n')
section_semaine, capture = [], False
for ligne in lignes:
    if 'Semaine du' in ligne and date.today().strftime('%Y') in ligne:
        capture = True
    elif ligne.startswith('###') and capture:
        break
    if capture:
        section_semaine.append(ligne)

resume_semaine = '\n'.join(section_semaine) or 'Aucune nouvelle étude cette semaine.'

# --- Construire l'email ---
expediteur = destinataire = 'drpierrerouquette@gmail.com'

msg = MIMEMultipart()
msg['From'] = expediteur
msg['To'] = destinataire
msg['Subject'] = f'Veille Orthodontique Reuni Smiles — {date.today().strftime("%d/%m/%Y")}'

body = f"""Bonjour Pierre,

Voici le rapport hebdomadaire de veille orthodontique de Réuni Smiles.

--- NOUVEAUTÉS DE LA SEMAINE ---

{resume_semaine}

--- FIN DU RAPPORT ---

Le fichier complet est joint à cet email.

Bonne semaine,
Votre agent de veille Claude"""

msg.attach(MIMEText(body, 'plain', 'utf-8'))

pj = MIMEBase('application', 'octet-stream')
pj.set_payload(contenu.encode('utf-8'))
encoders.encode_base64(pj)
pj.add_header('Content-Disposition', f'attachment; filename=veille_orthodontie_{date.today()}.md')
msg.attach(pj)

# --- Envoyer via Gmail API ---
access_token = get_access_token()
raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

response = requests.post(
    'https://gmail.googleapis.com/gmail/v1/users/me/messages/send',
    headers={
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    },
    json={'raw': raw}
)

if response.status_code == 200:
    print('Email envoyé avec succès.')
else:
    print(f'Erreur {response.status_code} : {response.text}')
    sys.exit(1)
