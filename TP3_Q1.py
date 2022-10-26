"""\
GLO-2000 Travail pratique 3
Noms et numéros étudiants:
- Alec Lévesque 111 269 901
- 
-
"""

import argparse
import re
import socket
import sys
from tkinter import E
from typing import NoReturn
import argparse
import random

from click import Argument

import glosocket
import glocrypto

def _parse_args(argv: 'list[str]') -> 'tuple[str, int]':
    """
    Utilise `argparse` pour récupérer les arguments contenus dans argv.

    Retourne un tuple contenant:
    - l'adresse IP du serveur (vide en mode serveur).
    - le port.
    """
    parser = argparse.ArgumentParser("desc")
    parser.add_argument("-p", "--port", dest='port', required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--server", action="store_true")
    group.add_argument("-d", "--destination", dest="destination")
    
    args = parser.parse_args(argv)

    return args.destination, int(args.port)


def _generate_modulus_base(destination: socket.socket) -> 'tuple[int, int]':
    """
    Cette fonction génère le modulo et la base à l'aide du module `glocrypto`.

    Elle les transmet respectivement dans deux
    messages distincts à la destination.

    Retourne un tuple contenant respectivement:
    - le modulo,
    - la base.
    """

    modulus = glocrypto.find_prime()
    base = random.randint(0, modulus)

    print(f"Modulus et base générée: {modulus}, {base}")

    print("Envoie du modulus au client")
    glosocket.send_msg(destination, str(modulus))

    print("Envoie de la base au client")
    glosocket.send_msg(destination, str(base))

    return modulus, base


def _receive_modulus_base(source: socket.socket) -> 'tuple[int, int]':
    """
    Cette fonction reçoit le modulo et la base depuis le socket source.

    Retourne un tuple contenant respectivement:
    - le modulo,
    - la base.
    """
    print("Réception du modulus et de la base")
    modulus = int(glosocket.recv_msg(source))
    base = int(glosocket.recv_msg(source))

    print(f"Modulus reçu: {modulus}")
    print(f"Base reçu: {base}")

    return modulus, base


def _compute_keys(modulus: int, base: int) -> 'tuple[int, int]':
    """
    Génère une clé privée et en déduit une clé publique.

    Retourne un tuple contenant respectivement:
    - la clé privée,
    - la clé publique.
    """
    cle_prive = random.randint(0, modulus)
    cle_publique = glocrypto.modular_exponentiation(base, cle_prive, modulus)

    return cle_prive, cle_publique

def _exchange_pubkeys(own_pubkey: int, peer: socket.socket) -> int:
    """
    Envoie sa propre clé publique, récupère la
    clé publique de l'autre et la retourne.
    """
    glosocket.send_msg(peer, str(own_pubkey))
    other_pub_key = int(glosocket.recv_msg(peer))
    return other_pub_key


def _compute_shared_key(private_key: int,
                        public_key: int,
                        modulus: int) -> int:
    """Calcule et retourne la clé partagée."""
    return glocrypto.modular_exponentiation(public_key, private_key, modulus)


def _server(port: int) -> NoReturn:
    """
    Boucle principale du serveur.

    Prépare son socket, puis gère les clients à l'infini.
    """

    socket_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_serveur.bind(("127.0.0.1", port))
    socket_serveur.listen(5)
    print(f"Ecoute sur le port : {port}")

    while True:
        (client_soc, client_addr) = socket_serveur.accept()

        print(f"Connexion détectée depuis: {client_addr}")

        modulus, base = _generate_modulus_base(client_soc)

        cle_prive, cle_publique = _compute_keys(modulus, base)

        print(f"Clé privée et publique calculée: {cle_prive}, {cle_publique}")

        cle_publique_client = _exchange_pubkeys(cle_publique, client_soc)

        print(f"Clé publique du client: {cle_publique_client}")

        cle_partagee = _compute_shared_key(cle_prive, cle_publique_client, modulus)
        print(f"La clé partagée est: {cle_partagee}")
        break


def _client(destination: str, port: int) -> None:
    """
    Point d'entrée du client.

    Crée et connecte son socket, puis procède aux échanges.
    """
    socket_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_serveur.connect((destination, port))

    print("Le client se connecte au serveur et demande Le modulo")

    modulus, base = _receive_modulus_base(socket_serveur)

    cle_prive, cle_publique = _compute_keys(modulus, base)
    print(f"Clé privée/publique générées: {cle_prive}, {cle_publique}")

    cle_publique_serveur = _exchange_pubkeys(cle_publique, socket_serveur)
    print(f"Clé publique du serveur : {cle_publique_serveur}")

    cle_partagee = _compute_shared_key(cle_prive, cle_publique_serveur, modulus)

    print(f"La clé partagée est : {cle_partagee}")

# NE PAS ÉDITER PASSÉ CE POINT


def _main() -> int:
    try:
        destination, port = _parse_args(sys.argv[1:])
        if destination:
            _client(destination, port)
        else:
            _server(port)
        return 0
    except Exception as e:
        print(e)
        return -1


if __name__ == '__main__':
    sys.exit(_main())
