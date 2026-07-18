from pathlib import Path
from tree_sitter_language_pack import get_parser
import json
from model import AIModel
from json_utils import JSONUtils
ignored_files = ['model.py','build_workspace_tree.py','json_utils.py','main.py','os_utils.py']
obj = JSONUtils(".",ignored_files)
EXT_TO_LANG = {".py": "python"}
model = AIModel("gemini-3.1-flash-lite")
def extract_code(file_path,start_line,end_line):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    return ''.join(lines[start_line-1:end_line])
def build_full_workspace_tree(root_dir):
    required = ['import_statement','function_definition','class_definition']
    
    root = Path(root_dir).resolve()
    files = [f for f in root.rglob("*") if f.suffix in EXT_TO_LANG and f.name not in ignored_files]

    nodes = []


    for f in files:
        rel = f.relative_to(root)
        file_id = f"file::{rel}"
        

        parser = get_parser(EXT_TO_LANG[f.suffix])
        tree = parser.parse(f.read_bytes())

        stack = [(tree.root_node, file_id)]
        counter = 0
        while stack:
            node, parent_id = stack.pop()
            node_id = f"{rel}::{counter}"
            counter += 1
            
            
            if node.type in required:
                snippet = extract_code(f,node.start_point[0]+1,node.end_point[0]+1)
                # print(snippet)
                name = node.child_by_field_name("name")
                name = name.text.decode("utf-8") if name else None
                summary = model.summarize_code(snippet)
                nodes.append({
                        "id": node_id,
                        "parent_id": parent_id,
                        "type": node.type,
                        "start_line": node.start_point[0] + 1,
                        "end_line": node.end_point[0] + 1,
                        "path": str(f.relative_to(root)),
                        "name": name,
                        "summary": summary
                })
            for child in reversed(node.children):
                stack.append((child, node_id))
        print(f"Processed file: {f}")

    json_output = {"nodes": nodes}
    with open("out/workspace_tree.json", "w") as f:
        json.dump(json_output, f, indent=4)

def add_to_dir_summary(summary, parent_dir,file):
    result, idx = obj.find_key_in_json_file(parent_dir)
    if result != -1:
        if summary:

            result[idx][parent_dir]['summary'] += f"{file}:" + summary
        result[idx][parent_dir]['child_ids'].append(file)
        return result
    else:
        return None
def compile_directory_summaries_from_files():
    list_of_files = obj.find_directories_for_files()

    for path,parent_dir in list_of_files.items():
        if parent_dir == '.':
            continue

        
        result,idx = obj.find_key_in_json_file(path)
        if result != -1:
            summary = result[idx][path]['summary']
            res = add_to_dir_summary(summary, parent_dir,path)
            if res:

                with open("out/files_and_folders.json", "w") as f:
                        json.dump(res, f, indent=4)            
            

def compile_summaries():
    with open("out/workspace_tree.json", "r") as f:
        data = json.load(f)

    for node in data["nodes"]:
        summaries = ''
        if node["summary"]:
            summaries += node["summary"] + '\n'
            path = node["path"]
            result,idx = obj.find_key_in_json_file(path)
            result[idx][path]['summary'] += summaries
            result[idx][path]['child_ids'].append(node['id'])
            with open("out/files_and_folders.json", "w") as f:
                json.dump(result, f, indent=4)

def merge_directory_summary_into_super_dir():
    with open("out/max_level.txt","r") as f:
        max_level = int(f.read())
    data = obj.load_json_data()
    for i in range(max_level,0,-1):
        dirs = obj.find_directories_based_on_level(i)
        
        for dir in dirs:
            _,idx = obj.find_key_in_json_file(dir)
            summary = (data[idx][dir]['summary'])
            parent = data[idx][dir]['parent_dir']
            if parent == '.':
                continue

            _,p_idx = obj.find_key_in_json_file(parent)
            data[p_idx][parent]['summary'] = f'{data[idx][dir]['path']}:' + summary
            data[p_idx][parent]['child_ids'].append(dir)
    
    with open("out/files_and_folders.json", "w") as f:
            json.dump(data, f, indent=4)
if __name__ == "__main__":
    #build_full_workspace_tree(".")
    merge_directory_summary_into_super_dir()