"""\
GLO-2000 Travail pratique 3
Noms et numéros étudiants:
-
-
-
"""

import argparse
import socket
import sys
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

    modulo = glocrypto.find_prime()
    base = random.randint(0, modulo)
    return modulo, base


def _receive_modulus_base(source: socket.socket) -> 'tuple[int, int]':
    """
    Cette fonction reçoit le modulo et la base depuis le socket source.

    Retourne un tuple contenant respectivement:
    - le modulo,
    - la base.
    """
    msg = glosocket.recv_msg(socket).split(" ")
    return msg[0], msg[1]


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
    other_pub_key = int(glosocket.recv_msg(peer))
    glosocket.send_msg(peer, own_pubkey)
    return other_pub_key


def _compute_shared_key(private_key: int,
                        public_key: int,
                        modulus: int) -> int:
    """Calcule et retourne la clé partagée."""
    return 0


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
    
    client_num = 0

    while True:
        (client_soc, client_addr) = socket_serveur.accept()
        print(glosocket.recv_msg(client_soc))
        glosocket.send_msg(client_soc, "Hello user!")
        client_soc.close()


def _client(destination: str, port: int) -> None:
    """
    Point d'entrée du client.

    Crée et connecte son socket, puis procède aux échanges.
    """
    socket_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_serveur.connect((destination, port))

    glosocket.send_msg(socket_serveur, "Hello server!")

    print(glosocket.recv_msg(socket_serveur))

# NE PAS ÉDITER PASSÉ CE POINT


def _main() -> int:
    destination, port = _parse_args(sys.argv[1:])
    if destination:
        _client(destination, port)
    else:
        _server(port)
    return 0


if __name__ == '__main__':
    sys.exit(_main())
