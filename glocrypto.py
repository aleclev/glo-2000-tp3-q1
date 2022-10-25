"""\
Module fournissant les fonctions cryptographiques pour le TP3

Attention : en cryptographie, les nombres doivent être impossibles à deviner,
ce qui n'est pas le cas ici. N'utilisez pas ce module dans un projet réel !
"""
import random

# Nombre de bits des nombres premiers générés. Plus ce nombre est grand, plus
# le protocole est securitaire, mais plus les operations sont lentes. Dans le
# cadre ce TP on utilisera toujours 256 bits.
_NB_BITS = 256


def random_integer(modulus: int) -> int:
    """Génère un entier aléatoire entre 0 (inclus) et `modulus` (exclus)."""
    return random.randrange(modulus)  # nosec B311


def _is_likely_prime(num: int) -> bool:
    """
    Fonction utilitaire pour find_prime.

    Vérifie si `num` est premier avec le test de Fermat.
    """
    if num in [0, 1]:
        return False
    elif num in [2, 3]:
        return True
    else:
        base = random.randint(2, num-2)  # nosec B311
        return pow(base, num-1, num) == 1


def find_prime() -> int:
    """Trouve un nombre premier sur `_NB_BITS`."""
    num = 0
    while not _is_likely_prime(num):
        num = random.getrandbits(_NB_BITS)
    return num


def modular_exponentiation(base: int, exponent: int, modulus: int) -> int:
    """Calcule (`base`^`exponent`) mod `modulus` de manière efficace."""
    return pow(base, exponent, modulus)
