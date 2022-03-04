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
Websockets protocol
"""

import logging
import re
import struct
import random
from collections import namedtuple

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

# Opcodes
OP_CONT = 0x0
OP_TEXT = 0x1
OP_BYTES = 0x2
OP_CLOSE = 0x8
OP_PING = 0x9
OP_PONG = 0xa

# Close codes
CLOSE_OK = 1000
CLOSE_GOING_AWAY = 1001
CLOSE_PROTOCOL_ERROR = 1002
CLOSE_DATA_NOT_SUPPORTED = 1003
CLOSE_BAD_DATA = 1007
CLOSE_POLICY_VIOLATION = 1008
CLOSE_TOO_BIG = 1009
CLOSE_MISSING_EXTN = 1010
CLOSE_BAD_CONDITION = 1011

URL_RE = re.compile(r'(wss|ws)://([A-Za-z0-9-\.]+)(?:\:([0-9]+))?(/.+)?')
URI = namedtuple('URI', ('protocol', 'hostname', 'port', 'path'))


class NoDataException(Exception):
    pass


class ConnectionClosed(Exception):
    pass


def urlparse(uri):
    """Parse ws:// URLs"""
    match = URL_RE.match(uri)
    if match:
        protocol = match.group(1)
        host = match.group(2)
        port = match.group(3)
        path = match.group(4)

        if protocol == 'wss':
            if port is None:
                port = 443
        elif protocol == 'ws':
            if port is None:
                port = 80
        else:
            raise ValueError('Scheme {} is invalid'.format(protocol))

        return URI(protocol, host, int(port), path)


class Websocket:
    """
    Basis of the Websocket protocol.

    This can probably be replaced with the C-based websocket module, but
    this one currently supports more options.
    """
    is_client = False

    def __init__(self, sock):
        self.sock = sock
        self.open = True
        self.debug = False
        self.buff = b''
        self.tmp_buff = b''
        self.global_len = 0
        self.frame_debug = []
        self.last_len = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def settimeout(self, timeout):
        self.sock.settimeout(timeout)

    def read_frame(self, max_size=None):
        """
        Read a frame from the socket.
        See https://tools.ietf.org/html/rfc6455#section-5.2 for the details.
        """
        # try:
        #     assert self.last_len == len(self.tmp_buff)
        # except Exception:
        #     # print(f'MAGICAL APPEARING BYTES :^O!{self.tmp_buff}:{self.last_len}')
        if len(self.tmp_buff) != self.last_len:
            two_bytes = self.tmp_buff
        else:
            self.tmp_buff = b''
            two_bytes = b''
        mask_bits = None
        # try:
        #     assert self.global_len == len(self.buff)
        # except Exception:
        #     # Missing byte
        #     print(f"Missmatch at start gl:{self.global_len}, bl:{len(self.buff)}")
        # prevent frame header shifting
        # Frame header
        while len(two_bytes) < 2:
            two_bytes += self.sock.recv(1)
        self.buff += two_bytes
        if not self.tmp_buff:
            self.tmp_buff += two_bytes
        if not two_bytes:
            raise NoDataException

        byte1, byte2 = struct.unpack('!BB', two_bytes)

        # Byte 1: FIN(1) _(1) _(1) _(1) OPCODE(4)
        fin = bool(byte1 & 0x80)
        opcode = byte1 & 0x0f

        # Byte 2: MASK(1) LENGTH(7)
        mask = bool(byte2 & (1 << 7))
        length = byte2 & 0x7f

        if length == 126:  # Magic number, length header is 2 bytes
            lh = self.sock.recv(2)
            assert len(lh) == 2
            self.buff += lh
            self.tmp_buff += lh
            length, = struct.unpack('!H', lh)
        elif length == 127:  # Magic number, length header is 8 bytes
            lh = self.sock.recv(8)
            assert len(lh) == 8
            self.buff += lh
            self.tmp_buff += lh
            length, = struct.unpack('!Q', lh)

        if mask:  # Mask is 4 bytes
            mask_bits = self.sock.recv(4)
            while len(mask_bits) < 4:
                mask_bits += self.sock.recv(1)
            assert len(mask_bits) == 4
            self.buff += mask_bits
            self.tmp_buff += mask_bits

        try:
            data = self.sock.recv(length)
            while len(data) < length:
                data += self.sock.recv(1)
            self.buff += data
            self.tmp_buff += data
            assert len(data) == length
            if self.debug:
                try:
                    assert self.buff[-len(self.tmp_buff):] == self.tmp_buff
                    self.global_len += len(self.tmp_buff)
                    assert self.global_len == len(self.buff), "Missmatch at end"
                except Exception:
                    if self.debug:
                        print(f"Missmatch at end gl:{self.global_len}, "
                              f"bl:{len(self.buff)}")
            self.last_len = len(self.tmp_buff)
        except MemoryError:
            # We can't receive this many bytes, close the socket
            if __debug__:
                LOGGER.debug("Frame of length %s too big. Closing",
                             length)
            self.close(code=CLOSE_TOO_BIG)
            return True, OP_CLOSE, None

        if mask:
            data = bytes(b ^ mask_bits[i % 4]
                         for i, b in enumerate(data))

        if self.debug:
            idx = self.buff.index(two_bytes)
            self.frame_debug.append(dict(tb=two_bytes, b1=byte1, b2=byte2,
                                         fin=fin, opcode=opcode,
                                         mask=mask, ln=length, data=data,
                                         pf=self.buff[idx-200:idx],
                                         tmp=self.tmp_buff,
                                         btmp=self.buff[-len(self.tmp_buff):]))

        return fin, opcode, data

    def write_frame(self, opcode, data=b''):
        """
        Write a frame to the socket.
        See https://tools.ietf.org/html/rfc6455#section-5.2 for the details.
        """
        fin = True
        mask = self.is_client  # messages sent by client are masked

        length = len(data)

        # Frame header
        # Byte 1: FIN(1) _(1) _(1) _(1) OPCODE(4)
        byte1 = 0x80 if fin else 0
        byte1 |= opcode

        # Byte 2: MASK(1) LENGTH(7)
        byte2 = 0x80 if mask else 0

        if length < 126:  # 126 is magic value to use 2-byte length header
            byte2 |= length
            self.sock.send(struct.pack('!BB', byte1, byte2))

        elif length < (1 << 16):  # Length fits in 2-bytes
            byte2 |= 126  # Magic code
            self.sock.send(struct.pack('!BBH', byte1, byte2, length))

        elif length < (1 << 64):
            byte2 |= 127  # Magic code
            self.sock.send(struct.pack('!BBQ', byte1, byte2, length))

        else:
            raise ValueError()

        if mask:  # Mask is 4 bytes
            mask_bits = struct.pack('!I', random.getrandbits(32))
            self.sock.send(mask_bits)

            data = bytes(b ^ mask_bits[i % 4]
                         for i, b in enumerate(data))

        self.sock.send(data)

    def reset_buffers(self):
        # Redo frame reading to prevent misterious frame header shifting missing
        # first two bytes
        self.buff = b''
        self.tmp_buff = b''
        self.global_len = 0

    def recv(self):
        """
        Receive data from the websocket.

        This is slightly different from 'websockets' in that it doesn't
        fire off a routine to process frames and put the data in a queue.
        If you don't call recv() sufficiently often you won't process control
        frames.
        """
        assert self.open

        while self.open:
            try:
                fin, opcode, data = self.read_frame()
            except NoDataException:
                return ''
            except ValueError:
                LOGGER.debug("Failed to read frame. Socket dead.")
                self._close()
                raise ConnectionClosed()

            if not fin:
                raise NotImplementedError()

            if opcode == OP_TEXT:
                return data.decode('utf-8')
            elif opcode == OP_BYTES:
                return data
            elif opcode == OP_CLOSE:
                self._close()
                return
            elif opcode == OP_PONG:
                # Ignore this frame, keep waiting for a data frame
                continue
            elif opcode == OP_PING:
                # We need to send a pong frame
                if __debug__:
                    LOGGER.debug("Sending PONG")
                self.write_frame(OP_PONG, data)
                # And then wait to receive
                continue
            elif opcode == OP_CONT:
                # This is a continuation of a previous frame
                raise NotImplementedError(opcode)
            else:
                raise ValueError(opcode)

    def send(self, buf):
        """Send data to the websocket."""

        assert self.open

        if isinstance(buf, str):
            opcode = OP_TEXT
            buf = buf.encode('utf-8')
        elif isinstance(buf, bytes):
            opcode = OP_BYTES
        else:
            raise TypeError()

        self.write_frame(opcode, buf)

    def close(self, code=CLOSE_OK, reason=''):
        """Close the websocket."""
        if not self.open:
            return

        buf = struct.pack('!H', code) + reason.encode('utf-8')

        self.write_frame(OP_CLOSE, buf)
        self._close()

    def _close(self):
        if __debug__:
            LOGGER.debug("Connection closed")
        self.open = False
        self.sock.close()
