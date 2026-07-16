from pathlib import Path
from tree_sitter_language_pack import get_parser
import json
from model import AIModel
from json_utils import JSONUtils
obj = JSONUtils(".")
EXT_TO_LANG = {".py": "python"}
model = AIModel("gemini-3.1-flash-lite")
def extract_code(file_path,start_line,end_line):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    return ''.join(lines[start_line-1:end_line])
def build_full_workspace_tree(root_dir):
    required = ['import_statement','function_definition','class_definition']
    ignored_files = ['model.py','modified_tree.py','json_utils.py','model.py']
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



def compile_summaries():
    with open("out/workspace_tree.json", "r") as f:
        data = json.load(f)

    for node in data["nodes"]:
        summaries = ''
        if node["summary"]:
            summaries += node["summary"] + '\n'
            path = node["path"]
            result,idx = obj.find_key_in_json_file("out/file_and_folders.json", path)
            result[idx][path]['summary'] += summaries
            result[idx][path]['child_ids'].append(node['id'])
            with open("out/file_and_folders.json", "w") as f:
                json.dump(result, f, indent=4)

if __name__ == "__main__":
    #build_full_workspace_tree(".")
    compile_summaries()