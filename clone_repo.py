import re
import subprocess
from urllib.parse import urlparse


def get_repo_name(url):

    url = url.strip()

    if url.startswith("git@"):
        match = re.match(r"git@[^:]+:(.+/.+?)(?:\.git)?/?$", url)
        if match:
            return match.group(1).split("/")[-1]

    parsed = urlparse(url)
    path = parsed.path.strip("/")

    if not path:
        return ""

    parts = [part for part in path.split("/") if part]
    if len(parts) < 2:
        return ""

    repo_name = parts[-1]
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]

    return repo_name


def clone_repo(url, branch=None):
    name = get_repo_name(url)
    if not name:
        return None
    if not branch:
        subprocess.run(["git", "clone", f"{url}"])
    else:
        subprocess.run(["git", "clone", f"{url}", "-b", f"{branch}"])

    print("Repo cloning process completed")
    return name

if __name__ == "__main__":
    print(clone_repo(""))