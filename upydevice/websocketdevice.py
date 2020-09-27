import ast
import time
import socket
import multiprocessing
import shlex
import subprocess
from array import array
from upydevice import wsclient, protocol
try:
    from upydev import __path__ as CA_PATH
except Exception as e:
    pass


class BASE_WS_DEVICE:
    def __init__(self, target, password, init=False, ssl=False, auth=False,
                 capath=CA_PATH[0]):
        self.ws = None
        self.ip = target
        self.pswd = password
        self.port = 8266
        self.bytes_sent = 0
        self.buff = b''
        self.raw_buff = b''
        self.prompt = b'>>> '
        self.response = ''
        self._kbi = '\x03'
        self._banner = '\x02'
        self._reset = '\x04'
        self._traceback = b'Traceback (most recent call last):'
        self._flush = b''
        self.output = None
        self.platform = None
        self.connected = False
        self.repl_CONN = self.connected
        if init:
            if not ssl:
                self.ws = wsclient.connect('ws://{}:{}'.format(self.ip, self.port), self.pswd)
            else:
                self.port = 8833
                self.ws = wsclient.connect('wss://{}:{}'.format(self.ip, self.port), self.pswd, auth=auth, capath=capath)
            self.connected = True
            self.repl_CONN = self.connected

    def open_wconn(self, ssl=False, auth=False, capath=CA_PATH[0]):
        if not ssl:
            self.ws = wsclient.connect('ws://{}:{}'.format(self.ip, self.port), self.pswd)
        else:
            self.port = 8833
            self.ws = wsclient.connect('wss://{}:{}'.format(self.ip, self.port), self.pswd, auth=auth, capath=capath)
        self.connected = True
        self.repl_CONN = self.connected

    def close_wconn(self):
        self.ws.close()
        self.connected = False
        self.repl_CONN = self.connected

    def connect(self):
        self.open_wconn()

    def disconnect(self):
        self.close_wconn()

    def write(self, cmd):
        n_bytes = len(bytes(cmd, 'utf-8'))
        self.ws.send(cmd)
        return n_bytes

    def read_all(self):
        self.ws.sock.settimeout(None)
        try:
            self.raw_buff = b''
            while self.prompt not in self.raw_buff:
                fin, opcode, data = self.ws.read_frame()
                self.raw_buff += data

            return self.raw_buff
        except socket.timeout as e:
            return self.raw_buff

    def flush(self):
        self.ws.sock.settimeout(0.01)
        self._flush = b''
        while True:
            try:
                fin, opcode, data = self.ws.read_frame()
                self._flush += data
            except socket.timeout as e:
                break
            except protocol.NoDataException as e:
                break

    def wr_cmd(self, cmd, silent=False, rtn=True, rtn_resp=False, long_string=False):
        self.output = None
        self.response = ''
        self.buff = b''
        self.flush()
        self.bytes_sent = self.write(cmd+'\r')
        # time.sleep(0.1)
        # self.buff = self.read_all()[self.bytes_sent:]
        self.buff = self.read_all()
        if self.buff == b'':
            # time.sleep(0.1)
            self.buff = self.read_all()
        # print(self.buff)
        # filter command
        cmd_filt = bytes(cmd + '\r\n', 'utf-8')
        self.buff = self.buff.replace(cmd_filt, b'', 1)
        if self._traceback in self.buff:
            long_string = True
        if long_string:
            self.response = self.buff.replace(b'\r', b'').replace(b'\r\n>>> ', b'').replace(b'>>> ', b'').decode('utf-8', 'ignore')
        else:
            self.response = self.buff.replace(b'\r\n', b'').replace(b'\r\n>>> ', b'').replace(b'>>> ', b'').decode('utf-8', 'ignore')
        if not silent:
            if self.response != '\n' and self.response != '':
                print(self.response)
            else:
                self.response = ''
        if rtn:
            self.get_output()
            if self.output == '\n' and self.output == '':
                self.output = None
            if self.output is None:
                if self.response != '' and self.response != '\n':
                    self.output = self.response
        if rtn_resp:
            return self.output

    def cmd(self, cmd, silent=False, rtn=False, ssl=False, long_string=False):
        if not self.connected:
            self.open_wconn(ssl=ssl, auth=True)
        self.wr_cmd(cmd, silent=True, long_string=long_string)
        if self.connected:
            self.close_wconn()
        self.get_output()
        if not silent:
            print(self.response)
        if rtn:
            return self.output

    def reset(self, silent=False, ssl=False):
        if not silent:
            print('Rebooting device...')
        if self.connected:
            self.bytes_sent = self.write(self._reset)
            self.close_wconn()
            time.sleep(1)
            while True:
                try:
                    self.open_wconn()
                    self.wr_cmd(self._banner, silent=True)
                    break
                except Exception as e:
                    time.sleep(0.5)
            if not silent:
                print('Done!')
        else:
            self.open_wconn(ssl=ssl, auth=True)
            self.bytes_sent = self.write(self._reset)
            self.close_wconn()
            if not silent:
                print('Done!')

    def kbi(self, silent=True, pipe=None):
        if self.connected:
            if pipe is not None:
                self.wr_cmd(self._kbi, silent=silent)
                bf_output = self.response.split('Traceback')[0]
                traceback = 'Traceback' + self.response.split('Traceback')[1]
                if bf_output != '' and bf_output != '\n':
                    pipe(bf_output)
                pipe(traceback, std='stderr')
            else:
                self.wr_cmd(self._kbi, silent=silent)
        else:
            self.cmd(self._kbi, silent=silent)

    def banner(self, pipe=None):
        self.wr_cmd(self._banner, silent=True, long_string=True)
        if pipe is None:
            print(self.response.replace('\n\n', '\n'))
        else:
            pipe(self.response.replace('\n\n', '\n'))

    def get_output(self):
        try:
            self.output = ast.literal_eval(self.response)
        except Exception as e:
            if 'bytearray' in self.response:
                try:
                    self.output = bytearray(ast.literal_eval(
                        self.response.strip().split('bytearray')[1]))
                except Exception as e:
                    pass
            else:
                if 'array' in self.response:
                    try:
                        arr = ast.literal_eval(
                            self.response.strip().split('array')[1])
                        self.output = array(arr[0], arr[1])
                    except Exception as e:
                        pass
            pass


class WS_DEVICE(BASE_WS_DEVICE):
    def __init__(self, target, password, init=False, ssl=False, auth=False,
                 capath=CA_PATH[0], name=None, dev_platf=None,
                 autodetect=False):
        super().__init__(target=target, password=password, init=init, ssl=ssl,
                         auth=auth, capath=capath)
        self.dev_class = 'WIRELESS'
        self.dev_platform = dev_platf
        self.name = name
        self.raw_buff = b''
        self.message = b''
        self.output_queue = multiprocessing.Queue(maxsize=1)
        self.data_buff = ''
        self.datalog = []
        self.paste_cmd = ''
        self.flush_conn = self.flush
        self._is_traceback = False
        self.stream_kw = ['print', 'ls', 'cat', 'help', 'from', 'import',
                          'tree', 'du']
        if name is None and self.dev_platform:
            self.name = '{}_{}'.format(self.dev_platform, self.ip.split('.')[-1])
        if autodetect:
            if not self.connected:
                self.cmd("import sys; sys.platform", silent=True)
            else:
                self.wr_cmd("import sys; sys.platform", silent=True)
            self.dev_platform = self.output
            self.name = '{}_{}'.format(self.dev_platform, self.ip.split('.')[-1])

    def readline(self):
        self.ws.sock.settimeout(None)
        try:
            self.raw_buff = b''
            while b'\r\n' not in self.raw_buff:
                fin, opcode, data = self.ws.read_frame()
                self.raw_buff += data
                if self.prompt in self.raw_buff:
                    break

            return self.raw_buff
        except socket.timeout as e:
            return self.raw_buff
        except KeyboardInterrupt:
            raise KeyboardInterrupt

    def wr_cmd(self, cmd, silent=False, rtn=True, long_string=False,
               rtn_resp=False, follow=False, pipe=None, multiline=False,
               dlog=False, nb_queue=None):
        self.output = None
        self._is_traceback = False
        self.response = ''
        self.buff = b''
        self.flush()
        self.bytes_sent = self.write(cmd+'\r')
        # time.sleep(0.1)
        # self.buff = self.read_all()[self.bytes_sent:]
        if not follow:
            self.buff = self.read_all()
        if self.buff == b'':
            # time.sleep(0.1)
            if not follow:
                self.buff = self.read_all()
            else:
                silent_pipe = silent
                silent = True
                rtn = False
                rtn_resp = False
                try:
                    self.follow_output(cmd, pipe=pipe, multiline=multiline,
                                       silent=silent_pipe)
                except KeyboardInterrupt:
                    # time.sleep(0.2)
                    self.paste_cmd = ''
                    if pipe is None:
                        print('')
                    self.kbi(pipe=pipe)  # KBI
                    time.sleep(0.2)
                    for i in range(1):
                        self.write('\r')
                        self.flush_conn()
        # print(self.buff)
        # filter command
        cmd_filt = bytes(cmd + '\r\n', 'utf-8')
        self.buff = self.buff.replace(cmd_filt, b'', 1)
        if dlog:
            self.data_buff = self.buff.replace(b'\r', b'').replace(b'\r\n>>> ', b'').replace(b'>>> ', b'').decode('utf-8', 'ignore')
        if self._traceback in self.buff:
            long_string = True
        if long_string:
            self.response = self.buff.replace(b'\r', b'').replace(b'\r\n>>> ', b'').replace(b'>>> ', b'').decode('utf-8', 'ignore')
        else:
            self.response = self.buff.replace(b'\r\n', b'').replace(b'\r\n>>> ', b'').replace(b'>>> ', b'').decode('utf-8', 'ignore')
        if not silent:
            if self.response != '\n' and self.response != '':
                if pipe is None:
                    print(self.response)
            else:
                self.response = ''
        if rtn:
            self.get_output()
            if self.output == '\n' and self.output == '':
                self.output = None
            if self.output is None:
                if self.response != '' and self.response != '\n':
                    self.output = self.response
            if nb_queue is not None:
                nb_queue.put((self.output), block=False)
        if rtn_resp:
            return self.output

    def follow_output(self, inp, pipe=None, multiline=False, silent=False):
        self.raw_buff += self.readline()
        if pipe is not None:
            self._is_first_line = True
            if any(_kw in inp for _kw in self.stream_kw):
                self._is_first_line = False
            if self.paste_cmd != '':
                while self.paste_cmd.split('\n')[-1] not in self.raw_buff.decode('utf-8', 'ignore'):
                    self.raw_buff += self.readline()
        while True:

            self.message = self.readline()
            self.buff += self.message
            self.raw_buff += self.message
            if self.message == b'':
                pass
            else:
                if self.message.startswith(b'\n'):
                    self.message = self.message[1:]
                if pipe:
                    cmd_filt = bytes(inp + '\r\n', 'utf-8')
                    self.message = self.message.replace(cmd_filt, b'', 1)
                msg = self.message.replace(b'\r', b'').decode('utf-8', 'ignore')
                if 'cat' in inp:
                    if msg.endswith('>>> '):
                        msg = msg.replace('>>> ', '')
                        if not msg.endswith('\n'):
                            msg = msg+'\n'

                if pipe is not None:
                    if msg == '>>> ':
                        pass
                    else:
                        pipe_out = msg.replace('>>> ', '')
                        if pipe_out != '':
                            # if '...' in pipe_out:
                            #     pipe(pipe_out.split('...')[-1])
                            # else:
                            if 'Traceback (most' in pipe_out:
                                self._is_traceback = True
                                # catch before traceback:
                                pipe_stdout = pipe_out.split('Traceback (most')[0]
                                if pipe_stdout != '' and pipe_stdout != '\n':
                                    pipe(pipe_stdout)
                                pipe_out = 'Traceback (most' + pipe_out.split('Traceback (most')[1]
                            if self._is_traceback:
                                pipe(pipe_out, std='stderr')
                            else:
                                if self._is_first_line:
                                    self._is_first_line = False
                                    if not multiline:
                                        pipe(pipe_out, execute_prompt=True)
                                    else:
                                        pipe(pipe_out)
                                else:
                                    pipe(pipe_out)
                if pipe is None:
                    if not silent:
                        print(msg.replace('>>> ', ''), end='')
            if self.buff.endswith(b'>>> '):
                break
        self.paste_cmd = ''

    def is_reachable(self, n_tries=2, max_loss=1, debug=False, timeout=2):
        ping_cmd_str = 'ping -c {} {} -t {}'.format(n_tries, self.ip, timeout)
        ping_cmd = shlex.split(ping_cmd_str)
        timeouts = 0
        down_kw = ['Unreachable', 'down', 'timeout']
        try:
            proc = subprocess.Popen(
                ping_cmd, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            while proc.poll() is None:
                resp = proc.stdout.readline()[:-1].decode()
                if debug:
                    print(resp)
                if any([kw in resp for kw in down_kw]):
                    timeouts += 1

            time.sleep(1)
            result = proc.stdout.readlines()
            for message in result:
                if debug:
                    print(message[:-1].decode())

        except KeyboardInterrupt:
            time.sleep(1)
            result = proc.stdout.readlines()
            for message in result:
                if debug:
                    print(message[:-1].decode())

        if timeouts >= max_loss:
            if debug:
                print('DEVICE IS DOWN OR SIGNAL RSSI IS TOO LOW')
            return False
        else:
            return True

    def paste_buff(self, long_command):
        self.paste_cmd = long_command
        self.write('\x05')
        lines = long_command.split('\n')
        for line in lines:
            time.sleep(0.1)
            self.write(line+'\n')
        self.flush_conn()

    def get_datalog(self, dvars=None, fs=None, time_out=None, units=None):
        self.datalog = []
        self.output = None
        for line in self.data_buff.splitlines():
            self.output = None
            self.response = line
            self.get_output()
            if self.output is not None and self.output != '':
                self.datalog.append(self.output)
        if dvars is not None and self.datalog != []:
            temp_dict = {var: [] for var in dvars}
            temp_dict['vars'] = dvars
            for data in self.datalog:
                if len(data) == len(dvars):
                    for i in range(len(data)):
                        temp_dict[dvars[i]].append(data[i])
            if time_out is not None:
                fs = int((1/time_out)*1000)
            if fs is not None:
                temp_dict['fs'] = fs
                temp_dict['ts'] = [i/temp_dict['fs'] for i in range(len(temp_dict[dvars[0]]))]
            if units is not None:
                temp_dict['u'] = units
            self.datalog = temp_dict

    def cmd(self, cmd, silent=False, rtn=False, ssl=False, nb_queue=None,
            long_string=False):
        if not self.connected:
            self.open_wconn(ssl=ssl, auth=True)
        self.wr_cmd(cmd, silent=True, long_string=long_string)
        if self.connected:
            self.close_wconn()
        self.get_output()
        if not silent:
            print(self.response)
        if rtn:
            return self.output
        if nb_queue is not None:
            nb_queue.put((self.output), block=False)

    def cmd_nb(self, command, silent=False, rtn=True, long_string=False,
               rtn_resp=False, follow=False, pipe=None, multiline=False,
               dlog=False):
        # do a
        if self.connected:
            self.dev_process_raw = multiprocessing.Process(
                target=self.wr_cmd, args=(command, silent, rtn, long_string, rtn_resp,
                                          follow, pipe, multiline, dlog,
                                          self.output_queue))
            self.dev_process_raw.start()
        else:
            self.dev_process_raw = multiprocessing.Process(
                target=self.cmd, args=(command, silent, False, False,
                                          self.output_queue, long_string))
            self.dev_process_raw.start()

    def get_opt(self):
        try:
            self.output = self.output_queue.get(block=False)
        except Exception:
            pass
