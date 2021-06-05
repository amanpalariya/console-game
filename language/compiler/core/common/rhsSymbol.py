from dataclasses import dataclass


@dataclass(frozen=True)
class RhsSymbol:
    value: str
    __isTerminal: bool = False

    @staticmethod
    def terminal(token: str):
        return RhsSymbol(token, True)

    def isTerminal(self):
        return self.__isTerminal

    @staticmethod
    def eof():
        return RhsSymbol('__eof__', True)
