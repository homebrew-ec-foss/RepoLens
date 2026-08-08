from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import json

@dataclass
class AppState:
    _repo_path: Path | None = None
    out_dir: Path = field(default_factory=lambda: Path("out"))
    raw_nodes: list[dict] = field(default_factory=list)
    pipeline_progress: dict = field(default_factory=dict)

    @property
    def repo_path(self) -> Path | None:
        if self._repo_path is not None:
            return self._repo_path
        state_file = self.out_dir / "state.json"
        if state_file.exists():
            try:
                data = json.loads(state_file.read_text())
                if data.get("repo_path"):
                    self._repo_path = Path(data["repo_path"])
            except Exception:
                pass
        return self._repo_path

    @repo_path.setter
    def repo_path(self, val: Path | None):
        self._repo_path = val
        self.out_dir.mkdir(exist_ok=True, parents=True)
        state_file = self.out_dir / "state.json"
        data = {}
        if state_file.exists():
            try:
                data = json.loads(state_file.read_text())
            except Exception:
                pass
        data["repo_path"] = str(val) if val else None
        state_file.write_text(json.dumps(data))

    @property
    def gemini_api_key(self) -> str | None:
        state_file = self.out_dir / "state.json"
        if state_file.exists():
            try:
                data = json.loads(state_file.read_text())
                return data.get("gemini_api_key")
            except Exception:
                pass
        return None

    @gemini_api_key.setter
    def gemini_api_key(self, val: str | None):
        self.out_dir.mkdir(exist_ok=True, parents=True)
        state_file = self.out_dir / "state.json"
        data = {}
        if state_file.exists():
            try:
                data = json.loads(state_file.read_text())
            except Exception:
                pass
        data["gemini_api_key"] = val
        state_file.write_text(json.dumps(data))

state = AppState()

if state.gemini_api_key:
    import os
    os.environ["GEMINI_API_KEY"] = state.gemini_api_key