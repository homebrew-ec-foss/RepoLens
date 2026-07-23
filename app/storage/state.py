from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class AppState:
    repo_path: Path | None = None
    out_dir: Path = field(default_factory=lambda: Path("out"))
    raw_nodes: list[dict] = field(default_factory=list)

state = AppState()