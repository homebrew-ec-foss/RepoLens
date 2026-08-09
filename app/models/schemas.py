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

class LocalRepoRequest(BaseModel):
    folder_path: str

class OpenRepoRequest(BaseModel):
    path: str
    owner: str | None = None
    name: str | None = None

class ConfigRequest(BaseModel):
    gemini_api_key: str | None = None
    provider: str | None = None

class ConfigResponse(BaseModel):
    api_key_set: bool
    api_key_preview: str | None = None
    provider: str | None = None
    model: str | None = None
    embedding_model: str | None = None
    vector_db: str | None = None

class HealthResponse(BaseModel):
    status: str
    gemini_key_set: bool
    ollama_running: bool

class StatusResponse(BaseModel):
    status: str
    detail: str | None = None

class QueryRequest(BaseModel):
    query: str
    repo_owner: str | None = None
    repo_name: str | None = None
    deep: bool = False

class Citation(BaseModel):
    id: str | None = None
    kind: str | None = None
    title: str | None = None
    node_type: str | None = None
    language: str | None = None
    path: str | None = None
    start_line: int | None = None
    end_line: int | None = None
    chain: list[str] = []
    summary: str | None = None
    score: float | None = None

class RAGAnswer(BaseModel):
    query: str
    mode: str
    answer: str
    citations: list[Citation] = []
    retrieved: list[Citation] = []
