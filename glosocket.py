"""\
Module fournissant les fonctions d'envoi et de réception
de messages de taille arbitraire pour les sockets Python.
"""
import socket
import struct


class GLOSocketError(Exception):
    """
    Erreur levée par les fonctions du modules pour
    les erreurs liées aux sockets.
    """


def _recvall(source: socket.socket, size: int) -> bytes:
    """
    Fonction utilitaire pour recv_msg.

    Applique socket.recv en boucle pour jusqu'à la
    réception d'un message de la taille voulue.
    """
    msg = b""
    while size > 0:
        chunk_size = min(size, 4096)
        try:
            buffer = source.recv(chunk_size)
        except OSError as ex:
            raise GLOSocketError("The source socket is closed.") from ex
        if not buffer:
            raise GLOSocketError("The other socket is closed.")
        msg += buffer
        size -= len(buffer)
    return msg


def send_msg(dest_soc: socket.socket, message: str) -> None:
    """
    Encode le message puis le transmet à la destination.

    Lève une exception GLOSocketError en cas de problème
    de communication.
    """
    data = message.encode(encoding='utf-8')
    data_length = struct.pack("!I", len(data))
    try:
        dest_soc.sendall(data_length + data)
    except OSError as ex:
        raise GLOSocketError("Cannot send data with socket") from ex


def recv_msg(source_soc: socket.socket) -> str:
    """
    Récupère un message de la source et le décode.

    Lève une exception GLOSocketError en cas de problème
    de communication.
    """
    data_length = _recvall(source_soc, 4)
    try:
        length, = struct.unpack("!I", data_length)
    except struct.error as ex:
        raise GLOSocketError("The received data was"
                             " not the message's length") from ex

    data = _recvall(source_soc, length)
    return data.decode('utf-8')
