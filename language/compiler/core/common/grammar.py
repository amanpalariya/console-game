from compiler.core.common.rhsSymbol import RhsSymbol
from compiler.core.common.grammarRuleRhs import GrammarRuleRhs


class Grammar:
    __assignmentOperator = ':='

    def __init__(self):
        self.__rules = {}

    def add(self, lhs: str, *rhs: [GrammarRuleRhs]):
        self.__rules[lhs] = rhs

    def getRhs(self, lhs: str) -> [GrammarRuleRhs]:
        try:
            return self.__rules[lhs]
        except KeyError:
            raise Exception(f"Grammar rule for LHS '{lhs}' does not exist")

    def __repr__(self):
        return f"{self.__class__.__name__}(\n{self.getGrammarString()}\n)"

    def __getStringFromGrammarRule(self, lhs: str, rhs: [GrammarRuleRhs], lhsWidth: int):
        lhsString = lhs.ljust(lhsWidth)
        rhsJoiner = '\n' + ' '*(lhsWidth+len(self.__assignmentOperator)) + '| '
        rhsString = rhsJoiner.join(map(lambda x: x.getRuleString(), rhs))
        return f"{lhsString} {self.__assignmentOperator} {rhsString}"

    def getGrammarString(self):
        maxLhsLength = max(map(len, self.__rules.keys()))
        return '\n'.join(map(lambda lhs: self.__getStringFromGrammarRule(lhs, self.__rules[lhs], maxLhsLength), self.__rules.keys()))

    def __eq__(self, other):
        return self.__rules == other._Grammar__rules
