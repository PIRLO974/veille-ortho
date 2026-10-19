"""
Script de configuration OAuth2 Gmail — à exécuter UNE SEULE FOIS sur votre machine locale.

Prérequis :
  1. Aller sur https://console.cloud.google.com
  2. Créer un projet (ou en sélectionner un existant)
  3. Activer l'API Gmail : APIs & Services > Library > Gmail API > Enable
  4. Créer des identifiants OAuth2 : APIs & Services > Credentials
     > Create Credentials > OAuth client ID > Application type: Desktop app
  5. Télécharger le JSON et noter client_id et client_secret
  6. Lancer ce script :
     GMAIL_CLIENT_ID=xxx GMAIL_CLIENT_SECRET=yyy python3 setup_gmail_oauth.py
"""

import os
import sys
import requests
from urllib.parse import urlencode

CLIENT_ID = os.environ.get('GMAIL_CLIENT_ID')
CLIENT_SECRET = os.environ.get('GMAIL_CLIENT_SECRET')

if not CLIENT_ID or not CLIENT_SECRET:
    print("Erreur : définissez GMAIL_CLIENT_ID et GMAIL_CLIENT_SECRET")
    sys.exit(1)

REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

params = {
    'client_id': CLIENT_ID,
    'redirect_uri': REDIRECT_URI,
    'response_type': 'code',
    'scope': 'https://www.googleapis.com/auth/gmail.send',
    'access_type': 'offline',
    'prompt': 'consent',
}
auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

print("\n=== Étape 1 : Ouvrez cette URL dans votre navigateur ===\n")
print(auth_url)
print("\n=== Étape 2 : Autorisez l'accès, puis copiez le code affiché ===\n")

code = input("Collez le code ici : ").strip()

response = requests.post(
    'https://oauth2.googleapis.com/token',
    data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code',
    }
)

tokens = response.json()

if 'refresh_token' not in tokens:
    print(f"\nErreur : {tokens}")
    sys.exit(1)

refresh_token = tokens['refresh_token']

print("\n=== Succès ! ===\n")
print(f"GMAIL_REFRESH_TOKEN = {refresh_token}\n")
print("Ajoutez ces 3 variables dans .claude/settings.local.json :")
print(f"""
{{
  "env": {{
    "GMAIL_CLIENT_ID": "{CLIENT_ID}",
    "GMAIL_CLIENT_SECRET": "{CLIENT_SECRET}",
    "GMAIL_REFRESH_TOKEN": "{refresh_token}"
  }}
}}
""")
