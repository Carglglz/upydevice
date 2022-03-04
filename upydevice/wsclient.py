#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2020 Carlos Gil Gonzalez
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
import getpass
from upydevice.wsprotocol import Websocket, urlparse, URI


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

#  ws.send('8KJpDQQc\r')


class WebsocketClient(Websocket):
    is_client = True


def load_custom_CA_data(path):
    certificates = [cert for cert in os.listdir(
        path) if 'certificate' in cert and cert.endswith('.pem')]
    cert_datafile = ''
    for cert in certificates:
        with io.open(os.path.join(path, cert), 'r') as certfile:
            cert_datafile += certfile.read()
            cert_datafile += '\n\n'
    return cert_datafile


def load_cert_from_hostname(path, hostname):
    certificates = [cert for cert in os.listdir(
        path) if 'certificate' in cert and cert.endswith('.der')]
    cert_datafile = b''
    for cert in certificates:
        with io.open(os.path.join(path, cert), 'rb') as certfile:
            cert_datafile += certfile.read()
            if hostname.encode() in cert_datafile:
                _key = cert.replace('certificate', 'key').replace('.der', '.pem')
                key = os.path.join(path, _key)
                cert = os.path.join(path, cert.replace('.der', '.pem'))
                return key, cert
            else:
                cert_datafile = b''


def connect(uri, password, silent=True, auth=False, capath=None, passphrase=None):
    """
    Connect a websocket.
    """
    hostname = uri
    uri = urlparse(uri)
    try:
        if '.local' in uri.hostname:

            uri = URI(uri.protocol, socket.gethostbyname(uri.hostname),
                      uri.port, uri.path)

    except Exception as e:
        print(e)
        return
    assert uri

    if __debug__:
        LOGGER.debug("open connection %s:%s", uri.hostname, uri.port)

    sock = socket.socket()
    sock.settimeout(10)
    addr = socket.getaddrinfo(uri.hostname, uri.port)
    if uri.protocol == 'wss':
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # context = ssl._create_unverified_context()
        if auth:
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.load_verify_locations(cadata=load_custom_CA_data(capath))
            # load cert from hostname
            key, cert = load_cert_from_hostname(capath, hostname)
            # if cert:
            if not passphrase:
                while True:
                    try:
                        passphrase = getpass.getpass(f'Enter passphrase for '
                                                     f'{urlparse(hostname).hostname} '
                                                     f'key: ',
                                                     stream=None)
                        context.load_cert_chain(cert, key, password=passphrase)
                        break
                    except (OSError, ssl.SSLError):
                        print('Invalid passhprase, try again...')
                    except KeyboardInterrupt:
                        print('KeyboardInterrupt')
                        break
            else:
                context.load_cert_chain(cert, key, password=passphrase)
            context.set_ciphers('ECDHE-ECDSA-AES128-CCM8')
            sock = context.wrap_socket(sock, server_hostname=hostname)
        else:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            context.set_ciphers('ECDHE-ECDSA-AES128-CCM8')
            # sock = context.wrap_socket(sock, server_hostname=hostname)
            sock = context.wrap_socket(sock)
        try:
            sock.connect(addr[0][-1])
        except socket.timeout as e:
            print(e)
            return
    else:
        try:
            sock.connect(addr[0][4])
        except socket.timeout as e:
            print(e)
            return

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
    try:
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

    except Exception as e:
        print(e)
        return
