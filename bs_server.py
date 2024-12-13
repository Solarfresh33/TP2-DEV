import socket
import socket
import os
import logging
import time
import threading
from colorama import Fore, Style, init

# Initialiser colorama
init(autoreset=True)

class CustomFormatter(logging.Formatter):
    def format(self, record):
        if record.levelname == "WARNING":
            record.levelname = f"{Fore.YELLOW}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)
    
TEMP_DIR = '/var/log'
NETWORK_DIR = os.path.join(TEMP_DIR, 'bs_server')
os.makedirs(NETWORK_DIR, exist_ok=True)
LOG_FILE = os.path.join(NETWORK_DIR, 'bs_server.log')

logging.basicConfig(
    filename=LOG_FILE,
    encoding="utf-8",
    filemode="a",
    format="{asctime} {levelname} {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S", 
    level=logging.DEBUG
)


logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter("{asctime} {levelname} {message}", style="{"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# On choisit une IP et un port où on va écouter
host = "0.0.0.0" # string vide signifie, dans ce conetxte, toutes les IPs de la machine
port = os.environ.get("CALC_PORT", "13337")
try:
    port = int(port)
except ValueError:
    print("CALC_PORT doit être un entier. Utilisation du port par défaut : 13337")
    port = 13337

# On crée un objet socket
# SOCK_STREAM c'est pour créer un socket TCP (pas UDP donc)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# On demande à notre programme de se bind sur notre port
s.bind((host, port))
# Place le programme en mode écoute derrière le port auquel il s'est bind
s.listen(1)

last_connection_time = time.time()

def check_client_timeout():
    global last_connection_time
    while True:
        current_time = time.time()
        if current_time - last_connection_time >= 60:
            logger.warning("Aucun client depuis plus de une minute.")
        time.sleep(60)


threading.Thread(target=check_client_timeout, daemon=True).start()

logging.info(f"Le serveur tourne sur {host}:{port}")
conn, addr = s.accept()
logging.info(f"Un client {addr} s'est connecté.")

while True:
    last_connection_time = time.time()  # Mettre à jour le temps de connexion
    try:
        # On reçoit 1024 bytes de données
        data = conn.recv(1024)

        # Si on a rien reçu, on continue
        if not data: break

        client_request = data.decode('utf-8')

        logging.info(f"Le client {addr} a envoyé \"{data}\"")

        client_request = client_request.replace('x', '*')
        result = eval(client_request)
        msg = f"Resultat de {data} = {result}"
        msg = bytes(msg, 'utf-8')
        conn.sendall(msg)
        logging.info(f"Réponse envoyée au client {addr} : {msg}")

    except socket.error:
        print("Error Occured.")
        break
    
conn.close()


