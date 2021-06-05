from collections import defaultdict


class GotoTable:
    def __init__(self):
        self.__gotoTable = defaultdict(dict)

    def addGoto(self, state: int, nonTerminal: str, toState: int):
        self.__gotoTable[state][nonTerminal] = toState

    def __entryPresentAtCell(self, state: int, nonTerminal: str):
        return self.__gotoTable[state].get(nonTerminal, None) is not None

    def getStateToGoTo(self, state: int, nonTerminal: str):
        if self.__entryPresentAtCell(state, nonTerminal):
            return self.__gotoTable[state][nonTerminal]
        else:
            raise Exception(f"No goto specified for state '{state}' and non-terminal '{nonTerminal}'")
