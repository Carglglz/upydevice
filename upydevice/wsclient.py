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
import os
import io

from upydevice.protocol import Websocket, urlparse

LOGGER = logging.getLogger(__name__)

#  ws.send('8KJpDQQc\r')


class WebsocketClient(Websocket):
    is_client = True


def load_custom_CA_data(path):
    certificates = [cert for cert in os.listdir(path) if 'certificate' in cert and cert.endswith('.pem')]
    cert_datafile = ''
    for cert in certificates:
        with io.open(path+'/{}'.format(cert), 'r') as certfile:
            cert_datafile += certfile.read()
            cert_datafile += '\n\n'
    return cert_datafile


def connect(uri, password, silent=True, auth=False, capath=None):
    """
    Connect a websocket.
    """
    hostname = uri
    uri = urlparse(uri)
    assert uri

    if __debug__:
        LOGGER.debug("open connection %s:%s", uri.hostname, uri.port)

    sock = socket.socket()
    addr = socket.getaddrinfo(uri.hostname, uri.port)
    if uri.protocol == 'wss':
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # context = ssl._create_unverified_context()
        if auth:
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.load_verify_locations(cadata=load_custom_CA_data(capath))
            context.set_ciphers('ECDHE-ECDSA-AES128-CCM8')
            sock = context.wrap_socket(sock, server_hostname=hostname)
        else:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            context.set_ciphers('ECDHE-ECDSA-AES128-CCM8')
            # sock = context.wrap_socket(sock, server_hostname=hostname)
            sock = context.wrap_socket(sock)
        sock.connect(addr[0][-1])
    else:
        sock.connect(addr[0][4])

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
