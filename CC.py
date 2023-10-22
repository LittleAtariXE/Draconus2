import os
import socket
import sys
import json

from time import sleep
from threading import Thread


from app.CONFIG import SOCKETS_DIR, UNIX_SOCKET_FORMAT_CODE, UNIX_SOCKET_RAW_LEN


class SocketHandler(Thread):
    def __init__(self, name, serv_sock, cc_callback):
        super().__init__(daemon=True)
        self.name = name
        self.CC = cc_callback
        self.serv_sock = serv_sock
        self.format = UNIX_SOCKET_FORMAT_CODE
        self.raw_len = UNIX_SOCKET_RAW_LEN
    
    def recv_msg(self):
        msg = b""
        while True:
            recv = self.serv_sock.recv(self.raw_len)
            if not recv or recv == b"":
                return None
            else:
                if len(recv) < self.raw_len:
                    msg += recv
                    break
                else:
                    msg += recv
        return msg.decode(self.format)
    
    def waiting4msg(self):
        while True:
            msg = self.recv_msg()
            if not msg:
                break
            else:
                print(msg)
    
    def close(self):
        try:
            self.serv_sock.shutdown(socket.SHUT_RDWR)
            self.serv_sock.close()
        except:
            pass
    
    def __del__(self):
        self.close()

    def run(self):
        self.waiting4msg()


    

class ApiHandler:
    def __init__(self, socket_path):
        self.path = socket_path
        self.format = UNIX_SOCKET_FORMAT_CODE
        self.raw_len = UNIX_SOCKET_RAW_LEN
        self.api = None
    
    def connect(self):
        self.api = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self.api.connect(self.path)
            return True
        except OSError as e:
            # print(f"\n[CC] [!!] ERROR connection API Server [!!] : {e}")
            return None

    def send_data(self, data):
        data = json.dumps(data)
        try:
            self.api.sendall(data.encode(self.format))
        except OSError as e:
            print(f"[CC] [!!] ERROR send data to API Server [!!] : {e}")
    
    def recive_data(self):
        data = b""
        while True:
            recv = self.api.recv(self.raw_len)
            if not recv or recv == b"":
                return None
            else:
                if len(recv) < self.raw_len:
                    data += recv
                    break
                else:
                    data += recv
        try:
            data = json.loads(data)
            return data
        except json.JSONDecodeError as e:
            print(f"[CC] [!!] ERROR decode JSON data [!!] : {e}")
            return None




class CommandCenter:
    def __init__(self):
        self.sockets_dir = SOCKETS_DIR
        self.raw_len = UNIX_SOCKET_RAW_LEN
        self.format = UNIX_SOCKET_FORMAT_CODE
        self.draco_socket_path = os.path.join(self.sockets_dir, "_draco_sock")
        self.draco_socket_out_path = os.path.join(self.sockets_dir, "_draco_msg")
        self.SERVERS = {}
        self.Api = {}
    
    def find_draco(self):
        if not os.path.exists(self.draco_socket_path) or not os.path.exists(self.draco_socket_out_path):
            print("[SYSTEM] ERROR: Cant find Draconus")
        _ds = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            _ds.connect(self.draco_socket_path)
            print("[SYSTEM] Connected to DRACONUS")
            return _ds
        except Exception as e:
            print("[SYSTEM] ERROR: ", e)
            print("[SYSTEM] Probably Draconus was not started. Run first Draconus")
            print("[!!] EXIT PROGRAM [!!]")
            return None
    
    def conn_serv(self, name):
        sock_path = os.path.join(self.sockets_dir, name)
        try:
            lsocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            lsocket.connect(sock_path)
            self.SERVERS[name] = SocketHandler(name, lsocket, self)
            self.SERVERS[name].start()
            return True
        except:
            return None
    
    def conn_api(self, name):
        sock_path = os.path.join(self.sockets_dir, name)
        api = ApiHandler(sock_path)
        if api.connect():
            self.Api[name[:-4]] = api
            # print("CONN TO API")
            return True
        else:
            return None



    
    def find_servers(self):
        count = 0
        for sock in os.listdir(self.sockets_dir):
            if sock == "_draco_sock" or sock in self.SERVERS or sock in self.Api:
                continue
            elif sock.endswith("_api"):
                self.conn_api(sock)
                continue
            lsock = self.conn_serv(sock)
            if lsock:
                count += 1
        return count - 1
    
    def send_msg(self, msg):
        self.draco_socket.sendall(msg.encode(self.format))
    
    def send_json(self, data):
        try:
            jdata = json.dumps(data)
            self.send_msg(jdata)
        except json.JSONDecodeError as e:
            print("ERROR JSON data dump: ", e)
            return False
    
    def recv_msg(self):
        msg = b""
        while True:
            recv = self.draco_socket.recv(self.raw_len)
            if not recv or recv == b"":
                return None
            else:
                if len(recv) < self.raw_len:
                    msg += recv
                    break
                else:
                    msg += recv
        return msg.decode(self.format)
    
    def api_response(self, api_name, msg, recive=False):
        api = self.Api.get(api_name)
        api.send_data(msg)
        if recive:
            sleep(0.2)
            resp = api.recive_data()
            return resp
    
    def kill_server(self, name):
        if not name in self.SERVERS.keys():
            print("[DRACONUS] [!!] ERROR: Server does not exists [!!]")
            return False
        del self.SERVERS[name]
        del self.Api[name]
        print("[DRACONUS] Wait moment")
        sleep(1)
        self.find_servers()
        
    
    def simple_shell(self):
        conf = {"NAME": "qqq", "PORT": 1234, "DEV": True, "TYPE": "Basic"}
        while True:
            print("\n[SHELL]>>", end="")
            cmd = input()
            if cmd == "exit":
                break
            if cmd == "make":
                self.send_json(["make", conf])
                sleep(1)
                self.find_servers()
                continue
            if cmd == "api":
                self.api_response("qqq_api", ["next", "start"])
                continue
            cmd = cmd.split(",")
            self.send_json(cmd)


    
    def START(self):
        self.draco_socket = self.find_draco()
        if not self.draco_socket:
            return False
        numbers = self.find_servers()
        if numbers > 0:
            print(f"[CommandCenter] I found {numbers} servers")
        return True

if __name__ == "__main__":
    conf = {"NAME": "MEINE", "PORT": 1234, "DEV": True, "TYPE": "Basic"}
    CC = CommandCenter()
    if not CC.START():
        print("NOT WORK")
        sys.exit()
    # CC.find_servers()
    CC.simple_shell()


    



