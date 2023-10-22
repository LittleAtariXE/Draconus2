import os
from pathlib import Path


DEFAULT_IP = "192.168.100.21"
FORMAT_CODE = "utf-8"
RAW_LEN = 1024
LISTENING_STEP = 3

# Format code for internal communication between Draconus, Command Center and Servers
UNIX_SOCKET_FORMAT_CODE = "utf-8"
UNIX_SOCKET_RAW_LEN = 2048

MESSENGER_NO_PRINTS = False

LEN_HEADER_SYS_MSG = 50

CLIENT_PAUSE_CONN = 5
CLIENT_CHECK_CONN = 30


APP_DIRECTORY = str(Path(os.path.dirname(__file__)).parent)
DRACO_OUT_MAIN_DIR = os.path.join(APP_DIRECTORY, "DRACONUS")
SOCKETS_DIR = os.path.join(APP_DIRECTORY, "app", "_sockets")
OUTPUT_DIR = os.path.join(DRACO_OUT_MAIN_DIR, "OUTPUT")
EXTRAS_DIR = os.path.join(APP_DIRECTORY, "extras")
PAYLOAD_DIR = os.path.join(DRACO_OUT_MAIN_DIR, "PAYLOAD")

print(APP_DIRECTORY)
print(DRACO_OUT_MAIN_DIR)

if not os.path.exists(DRACO_OUT_MAIN_DIR):
    os.mkdir(DRACO_OUT_MAIN_DIR)



