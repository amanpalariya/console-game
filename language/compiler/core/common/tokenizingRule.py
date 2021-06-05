from dataclasses import dataclass
from re import Pattern


@dataclass(frozen=True)
class TokenizingRule:
    token: str
    pattern: Pattern
