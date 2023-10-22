import socket
import os

from threading import Thread
from random import randint
from ..CONFIG import DEFAULT_IP, OUTPUT_DIR


class ExtraSocket(Thread):
    def __init__(self, file_len, file_name,  server_callback, ip=DEFAULT_IP, work="download"):
        super().__init__(daemon=True)
        self.fname = file_name
        self.flen = int(file_len)
        self.ip = ip
        self.Server = server_callback
        self.attemps = 100
        self.out_dir = os.path.join(OUTPUT_DIR, self.Server.name)
        self.work = work
        self.fpath = os.path.join(self.Server.payload_dir, file_name)
    
    def build(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c = 0
        while c < self.attemps:
            self.port = randint(6999, 99999)
            try:
                self.addr = (self.ip, self.port)
                self.server.bind(self.addr)
                return True
            except:
                c += 1
                continue
        self.Server.Msg(f"[{self.Server.name}] [!!] ERROR: Cant make extra socket [!!]")
        return None

    def download_file(self):
        self.Server.Msg(f"[{self.Server.name}] Start download file")
        self.server.listen()
        self.conn, self.addr = self.server.accept()
        file = b""
        while len(file) < self.flen:
            recv = self.conn.recv(self.flen - len(file))
            if not recv:
                return None
            else:
                file += recv
        
        self.save_file(file)
    
    def send_file(self, path):
        self.server.listen()
        self.Server.Msg(f"\n[{self.Server.name}] Waiting for client ...")
        self.conn, self.addr = self.server.accept()
        self.Server.Msg(f"\n[{self.Server.name}] Start sending file")
        with open(path, "rb") as f:
            self.conn.sendfile(f, 0)
        self.conn.close()
    
    def save_file(self, data):
        if not data:
            return None
        else:
            with open(os.path.join(self.out_dir, self.fname), "wb") as f:
                f.write(data)
            self.Server.Msg(f"[{self.Server.name}] Recive file <{self.fname}> successfull")
            return True
      
    def run(self):
        if self.work == "download":
            self.download_file()
        elif self.work == "upload":
            self.send_file(self.fpath)
    

        