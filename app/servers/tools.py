import socket
import os
import json


from ..CONFIG import UNIX_SOCKET_FORMAT_CODE, UNIX_SOCKET_RAW_LEN, SOCKETS_DIR

from threading import Thread
from time import sleep



class MrHandler(Thread):
    def __init__(self, cli_ID, conn, addr, crypter, serv_callback):
        super().__init__(daemon=True)
        self.ID = cli_ID
        self.conn = conn
        self.addr = addr
        self.Server = serv_callback
        self.Addr = f"{self.addr[0]}:{self.addr[1]}"
        self.crypter = crypter
        self.sys_op = "Unknown"
        self.sys_env = "Unknown"
        self.types = "Unknown"
    
    def recive_msg(self):
        msg = b""
        while True:
            recv = self.conn.recv(self.Server.raw_len)
            if not recv:
                return None
            if recv == b"":
                return None

            else:
                if len(recv) < self.Server.raw_len:
                    msg += recv
                    break
                else:
                    msg += recv
        rmsg = self.crypter.decrypt(msg)
        return rmsg
    
    def send_msg(self, msg):
        smsg = self.crypter.encrypt(msg)
        self.conn.sendall(smsg)
    
    def waiting_4msg(self):
        while self.Server.is_listening:
            try:
                msg = self.recive_msg()
            except OSError:
                self.Server.Msg(f"[{self.Server.name}] [!!] Recive from: <{self.Addr}> Abort [!!]", dev=True)
                break
            if not msg:
                break
            else:
                if msg.startswith(self.Server.sys_msg):
                    self.Server.exec_sys(msg, self)
                else:
                    self.Server.Msg(f"[{self.Addr}] {msg}")
        
        self.Server.Msg(f"[{self.Addr}] Close CONN")
        self.Server._close_traget_conn(self.ID)
    
    def close(self):
        try:
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()
        except Exception as e:
            self.Server.Msg(f"\n[{self.name}-DEV] [!!] ERROR Close conn [!!] : {e}", dev=True)
    
    def __del__(self):
        self.close()
        self.Server.Msg("DELETE CONN", dev=True)

    def run(self):
        self.waiting_4msg()


class LocalAPI(Thread):
    def __init__(self, name, server_callback):
        super().__init__(daemon=True)
        self.name = f"{name}_api"
        self.path = os.path.join(SOCKETS_DIR, self.name)
        self.Server = server_callback
        self.format = UNIX_SOCKET_FORMAT_CODE
        self.raw_len = UNIX_SOCKET_RAW_LEN
        self._status = None
    
    def build_server(self):
        if os.path.exists(self.path):
            try:
                os.unlink(self.path)
            except OSError as e:
                self.Server.Msg(f"\n[{self.name}] [!!] ERROR local API socket file [!!] : {e}", level=True)
                return False
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self.server.bind(self.path)
            self.server.listen()
            return True
        except Exception as e:
            self.Server.Msg(f"\n[{self.name}] [!!] ERROR build local API [!!] : {e}", level=True)
            return None

    def accept_conn(self):
        self.conn, self.addr = self.server.accept()
    
    def recive_msg(self):
        msg = b""
        while True:
            recv = self.conn.recv(self.raw_len)
            if not recv or recv == b"":
                return None
            else:
                if len(recv) < self.raw_len:
                    msg += recv
                    break
                else:
                    msg += recv
        return msg.decode(self.format)
    
    def recive_json(self):
        msg = self.recive_msg()
        if not msg:
            return None
        try:
            jmsg = json.loads(msg)
            return jmsg
        except json.JSONDecodeError as e:
            self.Server.Msg(f"\n[{self.name}] [!!] ERROR LocalAPI JSON decode [!!] : {e}", level=True)
            return None
    
    def send_data(self, data):
        try:
            data = json.dumps(data)
        except json.JSONDecodeError as e:
            self.Server.Msg(f"\n[{self.name}] [!!] ERROR LocalAPI JSON encode [!!] : {e}", level=True)
            return False
        try:
            self.conn.sendall(data.encode(self.format))
        except OSError as e:
            self.Server.Msg(f"\n[{self.name}] [!!] ERROR LocalAPI send data to Comand Center [!!] : {e}", level=True)
    

    def exec_command(self, cmd):
        if cmd[0] == "conf":
            self.send_data(self.Server.conf)
        elif cmd[0] == "next":
            self.Server.ctrl.base_cmd(cmd[1:])
        elif cmd[0] == "check":
            self.send_data(["OK"])
        elif cmd[0] == "help":
            self.send_data([str(self.Server.ctrl.help())])

    
    def run(self):
        if self.build_server():
            self._status = True
            while True:
                self.accept_conn()
                while True:
                    cmd = self.recive_json()
                    if not cmd:
                        break
                    self.exec_command(cmd)

    
        