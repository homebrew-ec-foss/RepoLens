from pathlib import Path
import json
from .os_utils import *
class JSONUtils:
    def __init__(self,dir,ignored_files):
        self.dir = dir
        self.json_file = "out/files_and_folders.json"
        self.ignored_files = ignored_files
    
    def load_json_data(self):
        with open(self.json_file, 'r') as f:
            data = json.load(f)
        return data
    def get_file_and_folders(self):
        res = []
        max_level = None
        for p in Path(self.dir).rglob("*"):
            if p not in self.ignored_files:

                parent_dir = str(p.parent.relative_to(self.dir))
                if p.is_file():
                    
                    res.append({str(p.relative_to(self.dir)): {"path": str(p.relative_to(self.dir)), "child_ids": [], "summary": "","parent_dir": parent_dir,"type": "file"}})
                elif p.is_dir():
                    level,max_level = get_level(str(p.relative_to(self.dir)),max_level=max_level)
                    res.append({str(p.relative_to(self.dir)): {"path": str(p.relative_to(self.dir)), "child_ids": [], "summary": "","parent_dir": parent_dir,"type": "directory","level":level}})
        with open(self.json_file, "w") as f:
            json.dump(res, f, indent=4)
            f.close()
        with open("out/max_level.txt","w") as f:
            f.write(str(max_level))
    def find_key_in_json_file(self,key):
        data = self.load_json_data()
        for i in range(len(data)):
            ele = data[i]
            val = (str(list(ele.keys())[0]))
            if val == key:
                return data,i
        print(f"Key not found: {key}")
        return -1,-1
    def find_directories_for_files(self):
        data = self.load_json_data()
        file_to_directory = {}
        for ele in data:
            for key, value in ele.items():
                if value['type'] == 'file':
                    file_to_directory[key] = value['parent_dir']
        return file_to_directory
    
    def find_directories_based_on_level(self,level):
        res = []
        data = self.load_json_data()
        for ele in data:
            for key,value in ele.items():
                if value['type'] == 'directory' and value['level'] == level:
                    res.append(key)
        return res

    
if __name__ == "__main__":
    obj = JSONUtils(".")
    print(obj.find_directories_for_files())
    #result, idx = obj.find_key_in_json_file("out/file_and_folders.json", "test.py")
    #print(f"Index of 'test.py': {idx}")