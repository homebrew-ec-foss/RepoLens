from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class AppState:
    repo_path: Path | None = None
    out_dir: Path = field(default_factory=lambda: Path("out"))
    # Holds the path of the currently active repository so that every endpoint 
    # after POST /repo can operate without requiring parameters.
    # for now, ig this will do
        raw_nodes: list[dict] = field(default_factory=list)

state = AppState()