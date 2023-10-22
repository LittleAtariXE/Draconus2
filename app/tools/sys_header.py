import os
import string
from random import randint

from ..CONFIG import LEN_HEADER_SYS_MSG, DRACO_OUT_MAIN_DIR

class MrHeader:
    def __init__(self, length=50):
        self.length = length
        self.base_char = string.ascii_letters + string.digits + string.punctuation
        self.headers_path = os.path.join(DRACO_OUT_MAIN_DIR, "sys_headers.txt")
        self.ban_char = ["'", '"', "\\"]
        self.header = self.work()

    def generate(self):
        header = ""
        for _ in range(self.length):
            char = self.base_char[randint(0, len(self.base_char) - 1)]
            if char in self.ban_char:
                continue
            header += char
        return header
    
    def work(self):
        if os.path.exists(self.headers_path):
            with open(self.headers_path, "r") as f:
                head = f.read()
            return head.strip("\n")
        else:
            with open(self.headers_path, "w") as f:
                head = self.generate()
                f.write(head.strip("\n"))
            return head.strip("\n")


