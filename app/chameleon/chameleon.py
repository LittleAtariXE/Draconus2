import base64



class Chameleon:
    def __init__(self, format_code):
        self.format = format_code

    
    def _encrypt(self, msg):
        msg = str(msg).encode(self.format)
        emsg = base64.b64encode(msg)
        return emsg
    
    def _decrypt(self, msg):
        dmsg = base64.b64decode(msg)
        return dmsg.decode(self.format)
    
    def encrypt(self, msg):
        return self._encrypt(msg)

    def decrypt(self, msg):
        return self._decrypt(msg)
    

    
