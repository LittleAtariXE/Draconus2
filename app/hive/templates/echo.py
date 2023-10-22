

class EchoClient(BasicWorm):
    def __init__(self):
        super().__init__()
        self.name = "echo_client"
    
    def RUN(self):
        self.check_conn()
        sleep(1)
        msg = self.make_sysmsg("echo", "Hello World")
        self.send_msg(msg)
        sleep(0.5)
        resp = self.recive_msg()
        print("RESPONSE: ", resp)
        sleep(1)
        return False