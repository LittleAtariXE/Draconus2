import os
import json

from ..CONFIG import OUTPUT_DIR, DRACO_OUT_MAIN_DIR


class Importer:
    def __init__(self):
        self.draco_dir = DRACO_OUT_MAIN_DIR
        self.out_dir = os.path.join(self.draco_dir, "Config")
        self.make_dirs()

    
    def make_dirs(self):
        if not os.path.exists(self.draco_dir):
            os.mkdir(self.draco_dir)
        if not os.path.exists(self.out_dir):
            os.mkdir(self.out_dir)
    
    def save_config(self, name, conf):
        config = json.dumps(conf, indent=3)
        with open(os.path.join(self.out_dir, f"{name}.json"), "w") as f:
            f.write(config)
        print(f"\n[DRACONUS] Save <{name}> config successfull")
    
    def load_config(self, name):
        path = os.path.join(self.out_dir, f"{name}.json")
        if not os.path.exists(path):
            print("\n[DRACONUS] [!!] ERROR: Config file does not exists [!!]")
            return None
        with open(path, "r") as f:
            try:
                data = json.loads(f.read())
                return data
            except json.JSONDecodeError as e:
                print(f"[DRACONUS] [!!] ERROR Load JSON config [!!] : {e}")
                return None
    