from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class LLMUsage:

    provider: str
    model: str

    request_id: Optional[str]

    timestamp: datetime

    input_tokens: int
    output_tokens: int
    total_tokens: int

    latency_ms: float

    input_cost: float
    output_cost: float
    total_cost: float

    status: str