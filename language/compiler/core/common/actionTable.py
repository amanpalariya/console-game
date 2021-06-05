from collections import defaultdict
from compiler.core.common.action import Action


class ActionTable:
    def __init__(self):
        self.__shiftTable = defaultdict(dict)
        self.__acceptTable = defaultdict(dict)
        self.__reduceTable = {}

    def __shiftEntryPresentAtCell(self, state: int, terminal: str):
        return self.__shiftTable[state].get(terminal, None) is not None

    def __reduceEntryPresentInRow(self, state: int):
        return self.__reduceTable.get(state, None) is not None

    def __acceptEntryPresentAtCell(self, state: int, terminal: str):
        return self.__acceptTable[state].get(terminal, None) is not None

    def __entryPresentAtCell(self, state: int, terminal: str):
        return self.__shiftEntryPresentAtCell(state, terminal) or self.__reduceEntryPresentInRow(state) or self.__acceptEntryPresentAtCell(state, terminal)

    def __getShiftActionAtCell(self, state: int, terminal: str):
        return self.__shiftTable[state].get(terminal, None)

    def __getAcceptActionAtCell(self, state: int, terminal: str):
        return self.__acceptTable[state].get(terminal, None)

    def __getReduceActionInRow(self, state: int):
        return self.__reduceTable.get(state, None)

    def __getActionAtCell(self, state: int, terminal: str):
        shiftAction = self.__getShiftActionAtCell(state, terminal)
        reduceAction = self.__getReduceActionInRow(state)
        acceptAction = self.__getAcceptActionAtCell(state, terminal)

        if acceptAction is not None:
            return acceptAction
        if shiftAction is not None:
            return shiftAction
        return reduceAction

    def getActionAtCell(self, state: int, terminal: str):
        if self.__entryPresentAtCell(state, terminal):
            return self.__getActionAtCell(state, terminal)
        else:
            raise Exception(f"No action specified for state '{state}' and terminal '{terminal}'")

    def addShift(self, state: int, terminal: str, toState: int):
        if self.__shiftEntryPresentAtCell(state, terminal):
            raise Exception(f"Shift-shift conflict at state '{state}' and terminal '{terminal}'")
        elif self.__reduceEntryPresentInRow(state):
            raise Exception(f"Shift-reduce conflict at state '{state}' and terminal '{terminal}'")
        elif self.__acceptEntryPresentAtCell(state, terminal):
            raise Exception(f"Shift-accept conflict at state '{state}' and terminal '{terminal}'")
        else:
            self.__shiftTable[state][terminal] = Action.shift(toState)

    def addReduce(self, state: int, ruleNumber: int):
        if self.__reduceEntryPresentInRow(state):
            raise Exception(f"Reduce-reduce conflict at state '{state}' and all terminals")
        else:
            for terminal in self.__shiftTable[state].keys():
                if self.__shiftEntryPresentAtCell(state, terminal):
                    raise Exception(f"Reduce-shift conflict at state '{state}' and terminal '{terminal}'")
                elif self.__acceptEntryPresentAtCell(state, terminal):
                    raise Exception(f"Reduce-accept conflict at state '{state}' and terminal '{terminal}'")
            self.__reduceTable[state] = Action.reduce(ruleNumber)

    def addAccept(self, state: int, terminal: str):
        if self.__shiftEntryPresentAtCell(state, terminal):
            raise Exception(f"Accept-shift conflict at state '{state}' and terminal '{terminal}'")
        elif self.__reduceEntryPresentInRow(state):
            raise Exception(f"Accept-reduce conflict at state '{state}' and terminal '{terminal}'")
        else:
            self.__acceptTable[state][terminal] = Action.accept()
