from build_workspace_tree import *
from json_utils import JSONUtils

if __name__ == "__main__":
    build_full_workspace_tree(".")
    obj = JSONUtils(".")
    obj.get_file_and_folders()
    compile_summaries()
    compile_directory_summaries_from_files()