from machine import Timer
import usocket as socket
from ustruct import pack
from array import array
from micropython import const


class U_STREAMER:
    def __init__(self, p_format='f', n_vars=3, buffer_size=32):
        self.cli_soc = None
        self.buff = array(p_format, (0 for _ in range(n_vars)))
        self.BUFFERSIZE = const(buffer_size)
        self.chunk_buffer = array(p_format, (0 for _ in range(self.BUFFERSIZE)))
        self.tim = Timer(-1)
        self.irq_busy = False
        self.index_put = 0
        self.p_format = p_format
        self.n_vars = n_vars

    def connect_SOC(self, host, port):
        self.irq_busy = True
        self.cli_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cli_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc_addr = socket.getaddrinfo(host, port)[0][-1]
        self.cli_soc.connect(soc_addr)
        self.irq_busy = False

    def disconnect_SOC(self):
        self.irq_busy = True
        self.cli_soc.close()
        self.irq_busy = False


# stream through socket
    def sample_send(self):
        if self.irq_busy:
            return
        try:
            self.irq_busy = True
            self.cli_soc.sendall(pack(self.p_format*self.n_vars,
                                      *self.read_method()))
            self.irq_busy = False
        except Exception as e:
            self.irq_busy = False

    def sample_send_call(self, x):
        if self.irq_busy:
            return
        try:
            self.irq_busy = True
            self.cli_soc.sendall(pack(self.p_format*self.n_vars,
                                      *self.read_method()))
            self.irq_busy = False
        except Exception as e:
            self.irq_busy = False

    def chunk_send_call(self, x):
        if self.irq_busy:
            return
        try:
            self.irq_busy = True
            if self.index_put < self.BUFFERSIZE:
                self.chunk_buffer[self.index_put] = self.read_method()[0]
                self.index_put += 1
            elif self.index_put == self.BUFFERSIZE:
                self.cli_soc.sendall(self.chunk_buffer)
                self.index_put = 0
            self.irq_busy = False
        except Exception as e:
            self.irq_busy = False

    def start_send(self, sampling_callback, timeout=100, on_init=None):
        self.irq_busy = False
        if on_init is not None:
            on_init()
        self.tim.init(period=timeout, mode=Timer.PERIODIC,
                      callback=sampling_callback)

    def stop_send(self):
        self.tim.deinit()
        # self.cli_soc.close()
        self.irq_busy = False
        self.index_put = 0


# class U_CHUNK_STREAMER:  # NO NEED, USE CALLBACK OF SENSOR CLASS, THERE DEFINE BUFFERS
