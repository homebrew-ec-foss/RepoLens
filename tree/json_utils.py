from pathlib import Path
import json
class JSONUtils:
    def __init__(self,dir):
        self.dir = dir

    
    def get_file_and_folders(self):
        res = []
        for p in Path(self.dir).rglob("*"):
            parent_dir = str(p.parent.relative_to(self.dir))
            if p.is_file():
                
                res.append({str(p.relative_to(self.dir)): {"path": str(p.relative_to(self.dir)), "child_ids": [], "summary": "","parent_dir": parent_dir,"type": "file"}})
            elif p.is_dir():
                res.append({str(p.relative_to(self.dir)): {"path": str(p.relative_to(self.dir)), "child_ids": [], "summary": "","parent_dir": parent_dir,"type": "directory"}})
        with open("out/file_and_folders.json", "w") as f:
            json.dump(res, f, indent=4)
    def find_key_in_json_file(self, json_file, key):
        with open(json_file, 'r') as f:
            data = json.load(f)
        for i in range(len(data)):
            ele = data[i]
            val = (str(list(ele.keys())[0]))
            if val == key:
                print(f"Found key: {key} at index {i}")
                print(f"Value: {ele[val]['summary']}")
                return data,i
        print(f"Key not found: {key}")
        return -1,-1

    
if __name__ == "__main__":
    obj = JSONUtils(".")
    obj.get_file_and_folders()
    #result, idx = obj.find_key_in_json_file("out/file_and_folders.json", "test.py")
    #print(f"Index of 'test.py': {idx}")