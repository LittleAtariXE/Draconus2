from time import sleep
from shell import build_draco_shell

if __name__ == "__main__":
    MasterShell = build_draco_shell()
    sleep(1)
    MasterShell()
