from compiler.core.common.rhsSymbol import RhsSymbol


class GrammarRuleRhs:
    def __init__(self, *symbols: [RhsSymbol]):
        self.__symbols = symbols

    def __getEscapedSymbolString(self, symbol: RhsSymbol):
        return f"'{symbol.value}'" if symbol.isTerminal() else symbol.value

    def getRuleString(self):
        return ' '.join(map(self.__getEscapedSymbolString, self.__symbols))

    def __repr__(self):
        return f"{self.__class__.__name__}({self.getRuleString()})"

    def getNumberOfSymbols(self):
        return len(self.__symbols)

    def getSymbol(self, index: int):
        return self.__symbols[index]

    def getAllSymbols(self):
        return list(self.__symbols)

    def __eq__(self, other):
        return self.getAllSymbols() == other.getAllSymbols()

    def __hash__(self):
        return hash(self.__symbols)
