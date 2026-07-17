"""API config / endpoint models stored in CoreDatasource.configuration as JSON."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ApiAuthType(str, Enum):
    NONE = "none"
    API_KEY = "api_key"
    BEARER = "bearer"
    BASIC = "basic"
    COOKIE = "cookie"


class ApiKeyLocation(str, Enum):
    HEADER = "header"
    QUERY = "query"


class ApiAuthConfig(BaseModel):
    """Auth credentials for an API datasource (sensitive; AES-encrypted before storage)."""

    type: ApiAuthType = ApiAuthType.NONE
    api_key: str = ""
    api_key_header: str = "X-API-Key"
    api_key_location: ApiKeyLocation = ApiKeyLocation.HEADER
    bearer_token: str = ""
    basic_username: str = ""
    basic_password: str = ""
    # Cookie auth: name -> value pairs, emitted as ``Cookie: n1=v1; n2=v2``.
    # Intended for temporary browser-session reuse (SSO cookie paste).
    cookies: Dict[str, str] = Field(default_factory=dict)


class ApiParamDef(BaseModel):
    """Single request parameter or response field."""

    name: str
    type: str = "string"
    required: bool = False
    default: Optional[str] = None
    description: str = ""
    location: str = "query"  # query | header | path | body
    example: Optional[str] = None
    enabled: bool = True


class ApiResponseFieldDef(BaseModel):
    """Describes one leaf field in a JSON response (used for schema text generation)."""

    name: str
    type: str = "string"
    description: str = ""
    path: str = ""  # JSONPath expression into the response; defaults to name
    enabled: bool = True


class ApiEndpointDef(BaseModel):
    """One callable API endpoint exposed as a virtual table."""

    name: str
    path: str = ""
    method: str = "GET"
    description: str = ""
    params: List[ApiParamDef] = Field(default_factory=list)
    response_fields: List[ApiResponseFieldDef] = Field(default_factory=list)
    # How body-location params assemble into the HTTP JSON body:
    # - object: JSON object from body params as keys (DTO field expansion / form fields)
    # - raw:    the single body param value *is* the JSON body (array / free-form / primitive)
    # OpenAPI body parameter names are documentation-only; they are never envelope keys.
    body_mode: str = "object"
    # Optional: JSONPath expression to extract the array of records from the response body.
    data_path: str = ""
    # Response extraction config — protocol-agnostic concept, API implements first.
    # Paths are dot-paths (e.g. "data.total"), not full JSONPath expressions.
    code_path: str = ""                         # Dot-path to business status, e.g. "code"
    # None = not configured (do not enforce). Distinct from success value 0 / "0" / "".
    code_success_value: Optional[Any] = None
    total_path: str = ""                        # Dot-path to total count, e.g. "data.total"
    # Static query / header overrides specific to this endpoint.
    extra_headers: Dict[str, str] = Field(default_factory=dict)
    extra_query: Dict[str, Any] = Field(default_factory=dict)
    body_template: Optional[str] = None  # JSON string template with {param} placeholders


class ApiDatasourceConf(BaseModel):
    """Persisted in `CoreDatasource.configuration` (AES-encrypted JSON).

    Mirrors `DatasourceConf` — one flat Pydantic model per protocol.
    """

    base_url: str = ""
    swagger_url: str = ""   # 持久化 swagger 源 URL（便于重新解析）
    timeout: int = 30
    headers: Dict[str, str] = Field(default_factory=dict)
    auth: ApiAuthConfig = Field(default_factory=ApiAuthConfig)
    endpoints: List[ApiEndpointDef] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
