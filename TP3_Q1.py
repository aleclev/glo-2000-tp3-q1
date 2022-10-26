"""\
GLO-2000 Travail pratique 3
Noms et numéros étudiants:
- Alec Lévesque 111 269 901
- Joey Fournier 111 267 602
- Zyed El Hidri 111 159 762
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
    print("Génération du modulus et de la base")

    modulus = glocrypto.find_prime()
    base = random.randint(0, modulus)

    print(f"Modulus généré: {modulus}")
    print(f"Base générée: {base}")

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
    print("Calcul de la clé privé et publique")
    cle_prive = random.randint(0, modulus)
    cle_publique = glocrypto.modular_exponentiation(base, cle_prive, modulus)

    print(f"Clé privé: {cle_prive}")
    print(f"Clé publique: {cle_publique}")

    return cle_prive, cle_publique

def _exchange_pubkeys(own_pubkey: int, peer: socket.socket) -> int:
    """
    Envoie sa propre clé publique, récupère la
    clé publique de l'autre et la retourne.
    """
    print("Envoi de la clé publique")
    glosocket.send_msg(peer, str(own_pubkey))
    other_pub_key = int(glosocket.recv_msg(peer))
    print(f"Réception de la clé publique: {other_pub_key}")
    return other_pub_key


def _compute_shared_key(private_key: int,
                        public_key: int,
                        modulus: int) -> int:
    """Calcule et retourne la clé partagée."""
    print("Calcul de la clé partagée")
    
    cle_partage = glocrypto.modular_exponentiation(public_key, private_key, modulus)
    print(f"Clé partagée calculée: {cle_partage}")
    
    return cle_partage


def _server(port: int) -> NoReturn:
    """
    Boucle principale du serveur.

    Prépare son socket, puis gère les clients à l'infini.
    """

    print("Démarrage du serveur")

    try:
        serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serveur.bind(("127.0.0.1", port))
        serveur.listen(5)
    except Exception as e:
        print(e)
        sys.exit(-1)
    
    print(f"Serveur près à recevoir sur le port {port}")

    while True:
        (client_soc, client_addr) = serveur.accept()

        try:
            print(f"Connexion détectée depuis: {client_addr}")
            modulus, base = _generate_modulus_base(client_soc)
            cle_prive, cle_publique = _compute_keys(modulus, base)
            cle_publique_client = _exchange_pubkeys(cle_publique, client_soc)
            cle_partagee = _compute_shared_key(cle_prive, cle_publique_client, modulus)
        except Exception as e:
            print(e)
            print("Ferneture de la connexion et attente d'une nouvelle connexion.")
            client_soc.close()

def _client(destination: str, port: int) -> None:
    """
    Point d'entrée du client.

    Crée et connecte son socket, puis procède aux échanges.
    """
    socket_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_serveur.connect((destination, port))

    modulus, base = _receive_modulus_base(socket_serveur)
    cle_prive, cle_publique = _compute_keys(modulus, base)
    cle_publique_serveur = _exchange_pubkeys(cle_publique, socket_serveur)
    cle_partagee = _compute_shared_key(cle_prive, cle_publique_serveur, modulus)

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
