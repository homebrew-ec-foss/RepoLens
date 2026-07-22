from __future__ import annotations

from pydantic import AnyHttpUrl, BaseModel, field_validator

# all pydantic v2 schemas 
class RepoRequest(BaseModel):
    github_url: str

    @field_validator("github_url")
    @classmethod
    def must_be_github(cls, v: str) -> str:
        if "github.com" not in v:
            raise ValueError("URL must be a github.com repository")
        return v.rstrip("/")

class StatusResponse(BaseModel):
    status: str
    detail: str | None = None

class NodeResponse(BaseModel):
    id: str
    path: str
    language: str
    node_type: str
    title: str | None
    start_line: int
    end_line: int
    parent_id: str | None
    children_ids: list[str]
    summary: str
