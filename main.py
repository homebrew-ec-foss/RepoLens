from tree_sitter.build_workspace_tree import *
from tree_sitter.json_utils import JSONUtils
from clone_repo import clone_repo
if __name__ == "__main__":
    url = input("Enter the url of the repo: ")
    branch = input("Enter the name of the branch: ")
    if branch == "main":
        branch = None
    name = clone_repo(url,branch)
    if not name:
        exit(0)
    ignored_files = ['model.py','build_workspace_tree.py','json_utils.py','main.py','os_utils.py']
    build_full_workspace_tree(name)
    obj = JSONUtils(name,ignored_files)
    obj.get_file_and_folders()
    compile_summaries()
    compile_directory_summaries_from_files()
    merge_directory_summary_into_super_dir()