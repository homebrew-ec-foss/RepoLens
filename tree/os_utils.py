from pathlib import Path
import os
def get_level(path, root=".",max_level=None):
    if os.path.exists(path):

        rel = Path(path).resolve().relative_to(Path(root).resolve())
        level =  len(rel.parts) if str(rel) != "." else 0
        if not max_level:
            max_level = level
        else:
            max_level = max(max_level,level)
        return level,max_level
    return '',max_level

if __name__ == "__main__":

    print(get_level("./folder/sub"))   