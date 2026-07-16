from build_workspace_tree import build_full_workspace_tree, compile_summaries
from json_utils import JSONUtils

if __name__ == "__main__":
    build_full_workspace_tree(".")
    obj = JSONUtils(".")
    obj.get_file_and_folders()
    compile_summaries()