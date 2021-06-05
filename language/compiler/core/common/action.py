from enum import Enum


class ActionType(Enum):
    Shift = 0
    Reduce = 1
    Accept = 2


class Action:

    def __init__(self, actionType: ActionType, value: int = -1):
        self.__actionType = actionType
        if actionType == ActionType.Shift:
            self.toState = value
        elif actionType == ActionType.Reduce:
            self.ruleNumber = value

    @staticmethod
    def shift(toState: int):
        return Action(ActionType.Shift, toState)

    @staticmethod
    def reduce(ruleNumber: int):
        return Action(ActionType.Reduce, ruleNumber)

    @staticmethod
    def accept():
        return Action(ActionType.Accept)

    def isShift(self):
        return self.__actionType == ActionType.Shift

    def isReduce(self):
        return self.__actionType == ActionType.Reduce

    def isAccept(self):
        return self.__actionType == ActionType.Accept

    def getActionString(self):
        if self.__actionType == ActionType.Shift:
            return f"s{self.toState}"
        elif self.__actionType == ActionType.Reduce:
            return f"r{self.ruleNumber}"
        elif self.__actionType == ActionType.Accept:
            return "acc"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.getActionString()})"
