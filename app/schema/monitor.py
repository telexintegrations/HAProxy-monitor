from pydantic import BaseModel
from typing import List


class Setting(BaseModel):
    label: str
    type: str
    required: bool
    default: str
    stats_endpoint: str | None = None
    username: str | None = None
    password: str | None = None


class MonitorPayload(BaseModel):
    channel_id: str
    return_url: str
    settings: List[Setting]
