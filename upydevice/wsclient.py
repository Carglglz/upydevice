"""
Websockets client for micropython

Based very heavily off
https://github.com/aaugustin/websockets/blob/master/websockets/client.py
"""

import logging
import socket
import binascii
import random
import ssl

from upydevice.protocol import Websocket, urlparse

LOGGER = logging.getLogger(__name__)

#  ws.send('8KJpDQQc\r')


class WebsocketClient(Websocket):
    is_client = True


def connect(uri, password, silent=True):
    """
    Connect a websocket.
    """

    uri = urlparse(uri)
    assert uri

    if __debug__:
        LOGGER.debug("open connection %s:%s", uri.hostname, uri.port)

    sock = socket.socket()
    addr = socket.getaddrinfo(uri.hostname, uri.port)
    sock.connect(addr[0][4])
    if uri.protocol == 'wss':
        sock = ssl.wrap_socket(sock)

    def send_header(header):
        # if __debug__: LOGGER.debug(str(header), *args)
        sock.send(bytes(header, 'utf-8') + b'\r\n')

    # Sec-WebSocket-Key is 16 bytes of random base64 encoded
    key = binascii.b2a_base64(bytes(random.getrandbits(8)
                                    for _ in range(16)))[:-1]

    send_header('GET {} HTTP/1.1'.format(uri.path or '/'))
    send_header('Host: {}:{}'.format(uri.hostname, uri.port))
    send_header('Connection: Upgrade')
    send_header('Upgrade: websocket')
    send_header('Sec-WebSocket-Key: {}'.format(key))
    send_header('Sec-WebSocket-Version: 13')
    send_header('Origin: http://{hostname}:{port}'.format(
        hostname=uri.hostname,
        port=uri.port)
    )
    send_header('')
    # time.sleep(0.1)
    header = sock.recv(2048)
    assert header.startswith(b'HTTP/1.1 101 '), header
    while b'Password: ' not in header:
        header = sock.recv(2048)

    ws = WebsocketClient(sock)
    ws.send(password+'\r')
    ws.send('\r')
    fin, opcode, data = ws.read_frame()
    if not silent:
        print(data.replace(b'\r', b'').replace(b'>>> ', b'').decode())
    ws.sock.settimeout(0.01)
    while True:
        try:
            fin, opcode, data = ws.read_frame()
        except socket.timeout as e:
            break
    return ws
