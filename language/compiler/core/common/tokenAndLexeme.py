from dataclasses import dataclass
from collections import namedtuple

CharPosition = namedtuple('CharPosition', ['lineNumber', 'columnNumber'])


@dataclass(frozen=True)
class TokenAndLexeme:
    token: str
    lexeme: str
    position: CharPosition
