from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import json

_GLOBAL_STATE_FILE = "state.json"
_REPO_STATE_FILE = "state.json"


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


@dataclass
class AppState:
    _repo_path: Path | None = None
    out_dir: Path = field(default_factory=lambda: Path("out"))
    raw_nodes: list[dict] = field(default_factory=list)
    pipeline_progress: dict = field(default_factory=dict)

    @property
    def _global_state_path(self) -> Path:
        return self.out_dir / _GLOBAL_STATE_FILE

    def _global_state(self) -> dict:
        return _load_json(self._global_state_path)

    def _write_global_state(self, data: dict) -> None:
        _save_json(self._global_state_path, data)

    @property
    def repo_path(self) -> Path | None:
        if self._repo_path is not None:
            return self._repo_path
        data = self._global_state()
        if data.get("repo_path"):
            self._repo_path = Path(data["repo_path"])
        return self._repo_path

    @repo_path.setter
    def repo_path(self, val: Path | None):
        self._repo_path = val
        data = self._global_state()
        data["repo_path"] = str(val) if val else None
        self._write_global_state(data)

    @property
    def repo_dir(self) -> Path:
        """Directory where the active repository's generated artifacts live.

        Every repository (GitHub clone or local folder) gets its own
        `repolens/` directory inside the repository itself, so artifacts from
        different repos never overwrite each other.
        """
        if self.repo_path is not None:
            return (self.repo_path / "repolens").resolve()
        return self.out_dir

    def ensure_repo_dir(self) -> Path:
        repo_dir = self.repo_dir
        repo_dir.mkdir(parents=True, exist_ok=True)
        return repo_dir

    def repo_state(self) -> dict:
        return _load_json(self.repo_dir / _REPO_STATE_FILE)

    def write_repo_state(self, data: dict) -> None:
        repo_dir = self.ensure_repo_dir()
        _save_json(repo_dir / _REPO_STATE_FILE, data)

    @property
    def gemini_api_key(self) -> str | None:
        return self._global_state().get("gemini_api_key")

    @gemini_api_key.setter
    def gemini_api_key(self, val: str | None):
        data = self._global_state()
        data["gemini_api_key"] = val
        self._write_global_state(data)

    @property
    def user_choice(self):
        return self._global_state().get("user_choice")
    @user_choice.setter
    def user_choice(self,val):
        data = self._global_state()
        data['user_choice'] = val
        self._write_global_state(data)
    @property
    def registered_repos(self) -> list[dict]:
        return self._global_state().get("registered_repos") or []

    def register_repo(self, kind: str, owner: str, name: str, path: Path) -> None:
        path_str = str(path.resolve())
        data = self._global_state()
        repos = list(data.get("registered_repos") or [])
        repos = [r for r in repos if r.get("path") != path_str]
        repos.append({
            "kind": kind,
            "owner": owner,
            "name": name,
            "path": path_str,
        })
        data["registered_repos"] = repos
        self._write_global_state(data)

    def save(self) -> None:
        self._global_state()

state = AppState()

if state.gemini_api_key:
    import os
    os.environ["GEMINI_API_KEY"] = state.gemini_api_key