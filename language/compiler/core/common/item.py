from compiler.core.common.grammarRuleRhs import GrammarRuleRhs
from compiler.core.common.rhsSymbol import RhsSymbol


class Item:
    __assignmentOperator = ':='

    def __init__(self, lhs: str, rhs: GrammarRuleRhs, cursorIndex: int = 0):
        self.__lhs = lhs
        self.__rhs = rhs
        self.__cursor = cursorIndex

    def __getCursorIndex(self):
        if 0 <= self.__cursor < self.__rhs.getNumberOfSymbols():
            return self.__cursor
        else:
            return self.__rhs.getNumberOfSymbols()

    def isFinished(self) -> bool:
        return self.__getCursorIndex() == self.__rhs.getNumberOfSymbols()

    def getLhs(self) -> str:
        return self.__lhs

    def getRhs(self) -> GrammarRuleRhs:
        return self.__rhs

    def getNextSymbol(self) -> RhsSymbol:
        if not self.isFinished():
            return self.__rhs.getSymbol(self.__getCursorIndex())
        else:
            raise Exception("No next token present in item")

    def getFutureItem(self):
        return Item(self.__lhs, self.__rhs, cursorIndex=self.__cursor + (0 if self.isFinished() else 1))

    def __getEscapedSymbolString(self, symbol: RhsSymbol):
        return f"'{symbol.value}'" if symbol.isTerminal() else symbol.value

    def __getJoinedSymbols(self):
        symbolsBeforeCursor = self.__rhs.getAllSymbols()[:self.__getCursorIndex()]
        symbolsAfterCursor = self.__rhs.getAllSymbols()[self.__getCursorIndex():]
        return ' '.join(list(map(self.__getEscapedSymbolString, symbolsBeforeCursor)) + ['•'] + list(map(self.__getEscapedSymbolString, symbolsAfterCursor)))

    def getItemString(self):
        return f"{self.__lhs} {self.__assignmentOperator} {self.__getJoinedSymbols()}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.getItemString()})"

    def __hash__(self):
        return hash((self.__getCursorIndex(), self.__lhs, self.__rhs))

    def __eq__(self, other):
        lhsEqual = self.__lhs == other._Item__lhs
        rhsEqual = self.__rhs == other._Item__rhs
        cursorIndexEqual = self.__getCursorIndex() == other._Item__getCursorIndex()
        return lhsEqual and rhsEqual and cursorIndexEqual
