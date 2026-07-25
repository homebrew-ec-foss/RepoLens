from __future__ import annotations

import asyncio
import logging
import re
import shutil
from pathlib import Path
import os
from app.storage.state import state
import stat
import platform
logger = logging.getLogger(__name__)

# prehand regex for parsing GitHub URLs
_GITHUB_RE = re.compile(r"^https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$")


def _parse_github_url(url: str) -> tuple[str, str]:
    m = _GITHUB_RE.match(url.rstrip("/"))
    if not m:
        raise ValueError(f"Not a valid GitHub repository URL: {url!r}")
    return m.group("owner"), m.group("repo")


def remove_readonly(func,path,exc):
    os.chmod(path,stat.S_IWRITE)
    func(path)
async def clone_repo(github_url: str) -> Path:
    owner, repo_name = _parse_github_url(github_url)

    clone_url = f"https://github.com/{owner}/{repo_name}.git"
    # for now , this is fine, later after networkx graph, we can think
    # about a different storage system
    target = (state.out_dir / "repo" / owner / repo_name).resolve()

    if target.exists():
        logger.info("Removing existing clone at %s", target)
        if platform.system() == "Windows":

            shutil.rmtree(target,onexc=remove_readonly)
        else:
            shutil.rmtree(target)

    target.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Cloning %s :%s", clone_url, target)

    proc = await asyncio.create_subprocess_exec(
        "git", "clone", "--depth=1", clone_url, str(target),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        err = stderr.decode(errors="replace").strip()
        raise RuntimeError(f"git clone failed (exit {proc.returncode}): {err}")

    logger.info("Clone complete: %s", target)
    state.repo_path = target
    return target
