import os
import socket

from datetime import datetime
from time import sleep
from threading import Thread

from ..CONFIG import DRACO_OUT_MAIN_DIR, SOCKETS_DIR, UNIX_SOCKET_FORMAT_CODE, MESSENGER_NO_PRINTS


class Messenger:
    def __init__(self, name, conf={}):
        self.name = name
        self._dev = conf.get("DEV", False)
        self.format = UNIX_SOCKET_FORMAT_CODE
        self.socket_name = conf.get("MSG-SOCKET", self.name)
        self._s_dir = SOCKETS_DIR
        self.sock_file = os.path.join(self._s_dir, self.socket_name)
        self._logs_dir = os.path.join(DRACO_OUT_MAIN_DIR, "OUTPUT")
        self.log_file = os.path.join(self._logs_dir, f"{self.name}.txt")
        self.no_prints = conf.get("MSG_NO_PRINTS", False)
        self.make_file()
        self.server = None
        self.conn = None
        self.addr = None
        self.buff = []
        self.tmp_msg = ""
        self.char_end = "\n\n" + "-" * 90 + "\n\n"
        self.start_server()

    def make_file(self):
        if not os.path.exists(self._s_dir):
            os.mkdir(self._s_dir)
        if os.path.exists(self.sock_file):
            try:
                os.unlink(self.sock_file)
            except Exception as e:
                print("ERROR: ", e)
                return False
        if not os.path.exists(self._logs_dir):
            os.mkdir(self._logs_dir)
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write("") 
        return True
    
    def _add_log(self, logs):
        with open(self.log_file, "a+") as f:
            f.write(logs)
    
    def build_socket(self):
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(self.sock_file)
        self.server.listen(1)

    def accept_conn(self):
        while True:
            self.conn, self.addr = self.server.accept()
            self.empty_buff()
    
    def start_server(self):
        self.build_socket()
        acc_conn = Thread(target=self.accept_conn, daemon=True)
        acc_conn.start()
    
    def _send_msg(self, msg):
        self.conn.send(msg.encode(self.format))
    
    def send_msg(self, msg):
        if not self.conn:
            self.buff.append(f"{msg}")
            return False
        try:
            self._send_msg(msg)
        except (BrokenPipeError, ConnectionAbortedError, OSError):
            self.buff.append(msg)
    
    def empty_buff(self):
        if len(self.buff) > 0:
            old = "\n".join(self.buff)
            self._send_msg(old)
            self.buff = []
    
    def _send_dev_msg(self, msg):
        if not self.conn:
            return False
        try:
            self._send_msg(msg)
        except (BrokenPipeError, ConnectionAbortedError, OSError):
            pass


    def _log2file_dev(self, msg):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._add_log(f"\n*****{date}*****\n*****DEV MESSAGE******\n{str(msg)}\n")
        
    
    def _log2file(self, msg, end=True):
        if isinstance(msg, bytes):
            msg = msg.decode(self.format)
    
        if self.tmp_msg == "":
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.tmp_msg = f"\n[{self.name}] ---------- {date} ------------------------\n"
        self.tmp_msg += "\n" + str(msg)
        if end:
            self.tmp_msg += self.char_end
            self._add_log(self.tmp_msg)
            self.tmp_msg = ""
    
    def unpack_dict(self, data, name=""):
        max_len = max(len(str(k)) for k in data.keys())
        buff = f"-------------------------------{name}-----------------------------\n"
        for k, i in data.items():
            buff += f"--- {str(k).ljust(max_len)}\t -- {i}\n"
        buff += "---------------------------------------------------------------------------------"
        return buff
    
    
    def __call__(self, msg, end=True, unpack=False, unpack_name="", dev=False, level=False):
        if unpack:
            msg = self.unpack_dict(msg, unpack_name)
        if dev:
            if self._dev:
                self._send_dev_msg(msg)
                self._log2file_dev(msg)
                print(f"[{self.name}-DEV]{msg}")
            return True
        self.send_msg(msg)
        self._log2file(msg, end=end)
