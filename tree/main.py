from build_workspace_tree import *
from json_utils import JSONUtils

if __name__ == "__main__":
    ignored_files = ['model.py','build_workspace_tree.py','json_utils.py','main.py','os_utils.py']
    build_full_workspace_tree(".")
    obj = JSONUtils(".",ignored_files)
    obj.get_file_and_folders()
    compile_summaries()
    compile_directory_summaries_from_files()
    merge_directory_summary_into_super_dir()