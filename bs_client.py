import socket
import sys
import re
import os
import logging
from colorama import Fore, Style, init

# Initialiser colorama
init(autoreset=True)

class CustomFormatter(logging.Formatter):
    def format(self, record):
        if record.levelname == "ERROR":
            record.levelname = f"{Fore.RED}{record.levelname}{Style.RESET_ALL}"
            record.msg = f"{Fore.RED}{record.msg}{Style.RESET_ALL}"
        return super().format(record)
    
TEMP_DIR = '/tmp'
NETWORK_DIR = os.path.join(TEMP_DIR, 'bs_client')
os.makedirs(NETWORK_DIR, exist_ok=True)
LOG_FILE = os.path.join(NETWORK_DIR, 'bs_cliet.log')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Niveau global pour le logger

# Éviter la duplication des gestionnaires
if not logger.handlers:
    # Gestionnaire de fichier
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8", mode='a')
    file_handler.setFormatter(logging.Formatter("{asctime} {levelname} {message}", style="{", datefmt="%Y-%m-%d %H:%M:%S"))
    file_handler.setLevel(logging.INFO)  # Enregistre tous les logs INFO et supérieurs
    logger.addHandler(file_handler)  # Ajouter le gestionnaire de fichier

    # Gestionnaire de console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(CustomFormatter("{levelname} {message}", style="{"))
    console_handler.setLevel(logging.ERROR)  # N'affiche que les logs ERROR et supérieurs
    logger.addHandler(console_handler)  # Ajouter le gestionnaire de console


# On définit la destination de la connexion
host = '127.0.0.1'  # IP du serveur
port = int(input("Entrez le port du serveur : ").strip())

msg = input("Veuillez saisir une opération arithmétique: ")

pattern = re.compile(r"^(-?\d{1,5})\s*([+x-])\s*(-?\d{1,5})$")

if type(msg) is str :
    if pattern.search(msg):
        msg = bytes(msg, 'utf-8')
    else:
        raise TypeError("Ici on veut que additions, soustractions, multiplications avec des entiers entre -100000 et +100000")
else :
    raise TypeError("Ici on veut que des strings !")

# Création de l'objet socket de type TCP (SOCK_STREAM)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try :
    # Connexion au serveur
    s.connect((host, port))
    print(f"Connecté avec succès au serveur {host} sur le port {port}")
    logger.info(f"Connexion réussie à {host}:{port}")
    # note : la double parenthèse n'est pas une erreur : on envoie un tuple à la fonction connect()
except Exception as e:
    logger.error(f"Impossible de se connecter au serveur {host} sur le port {port}.")
    sys.exit()

# Envoi de data bidon
s.sendall(msg)
logger.info(f"Message envoyé au serveur {host} : {msg}")

# On reçoit 1024 bytes qui contiennent peut-être une réponse du serveur
data = s.recv(1024)

# On libère le socket TCP
s.close()

# Affichage de la réponse reçue du serveur
print(f"Le serveur a répondu {repr(data)}")

logger.info(f"Réponse reçue du serveur {host} : {repr(data)}")

sys.exit()
