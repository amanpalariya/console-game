from dataclasses import dataclass
from collections import defaultdict, deque, OrderedDict
from enum import Enum
from compiler.core.common.all import GrammarRuleRhs, RhsSymbol, Grammar, TokenAndLexeme, Action, ActionTable, GotoTable, Item, ItemSet


@dataclass(frozen=True)
class Symbol:
    token: str
    children: [] = ()
    lexeme: str = None

    @staticmethod
    def terminal(token, lexeme):
        return Symbol(token, (), lexeme)

    def isTerminal(self):
        return len(self.children) == 0


@dataclass(frozen=True)
class ProductionRule:
    lhs: str
    rhs: GrammarRuleRhs
    __assingmentOperator = ':='

    def getRuleString(self):
        return f"{self.lhs} {self.__assingmentOperator} {self.rhs.getRuleString()}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.getRuleString()})"

    @staticmethod
    def fromItem(item: Item):
        return ProductionRule(item.getLhs(), item.getRhs())


class SyntaxAnalyzer:
    __eofSymbol = RhsSymbol.eof()

    def __init__(self, grammar: Grammar, startSymbol: str, getNextTokenAndLexeme, errorHandler=None):
        self.__startSymbol = startSymbol
        self.__grammar = grammar
        self.__getNextTokenAndLexeme = getNextTokenAndLexeme
        self.__itemSets = OrderedDict()
        self.__errorHandler = errorHandler

    def __error(self, message):
        if self.__errorHandler is not None:
            self.__errorHandler(message)
        else:
            raise Exception(message)

    def __getNormalizedProductionRules(self, grammar: Grammar) -> [ProductionRule]:
        normalizedProductionRules: [ProductionRule] = []
        bfsQueue = deque([self.__startSymbol])
        visited = defaultdict(lambda: False)
        while len(bfsQueue) > 0:
            currentSymbol = bfsQueue.popleft()
            if not visited[currentSymbol]:
                rhsRules = grammar.getRhs(currentSymbol)
                for rhsRule in rhsRules:
                    for symbol in rhsRule.getAllSymbols():
                        if not symbol.isTerminal() and not visited[symbol.value]:
                            bfsQueue.append(symbol.value)
                    normalizedProductionRules.append(ProductionRule(currentSymbol, rhsRule))
                visited[currentSymbol] = True
        return normalizedProductionRules

    def __createRuleIndices(self):
        self.__ruleIndices = defaultdict(lambda: [])
        for index, productionRule in enumerate(self.__productionRules):
            self.__ruleIndices[productionRule.lhs].append(index)

    def __createProductionRules(self):
        self.__productionRules = self.__getNormalizedProductionRules(self.__grammar)
        self.__createRuleIndices()

    def __getItemsFromNonTerminal(self, nonTerminal: str):
        items = []
        bfsQueue = deque([nonTerminal])
        visited = defaultdict(lambda: False)
        while len(bfsQueue) > 0:
            currentSymbol = bfsQueue.popleft()
            if not visited[currentSymbol]:
                for ruleIndex in self.__ruleIndices[currentSymbol]:
                    rule = self.__productionRules[ruleIndex]
                    item = Item(rule.lhs, rule.rhs)
                    items.append(item)
                    if not item.isFinished():
                        nextSymbol = item.getNextSymbol()
                        if not nextSymbol.isTerminal():
                            bfsQueue.append(nextSymbol.value)
                visited[currentSymbol] = True
        return items

    def __getFullItemSetFromKernel(self, kernel: Item):
        items = [kernel]
        if not kernel.isFinished():
            nextSymbol = kernel.getNextSymbol()
            if not nextSymbol.isTerminal():
                items += self.__getItemsFromNonTerminal(nextSymbol.value)
        return ItemSet(*items)

    def __assignStateToItemSet(self, itemSet: ItemSet):
        state = self.__itemSets.get(itemSet, None)
        if state is None:
            self.__itemSets[itemSet] = len(self.__itemSets)

    def __getStateFromItemSet(self, itemSet: ItemSet):
        self.__assignStateToItemSet(itemSet)
        return self.__itemSets[itemSet]

    def __getItemSetFromState(self, state: int):
        try:
            return list(self.__itemSets.keys())[state]
        except KeyError:
            raise Exception(f"No item set present for the given state '{state}'")

    def __getTransitionsFromItemSet(self, itemSet: ItemSet):
        transitions = defaultdict(lambda: ItemSet())
        for item in itemSet.getItems():
            if not item.isFinished():
                symbol = item.getNextSymbol()
                newItem = item.getFutureItem()
                partialItemSet = self.__getFullItemSetFromKernel(newItem)
                transitions[symbol] = ItemSet.union(transitions[symbol], partialItemSet)
        return transitions

    def __generateActionAndGotoTables(self):
        self.__createProductionRules()
        rootProductionRule = self.__productionRules[0]
        rootKernel = Item(rootProductionRule.lhs, rootProductionRule.rhs)
        rootState = self.__getStateFromItemSet(self.__getFullItemSetFromKernel(rootKernel))
        visited = defaultdict(lambda: False)
        bfsQueue = deque([rootState])
        self.__actionTable = ActionTable()
        self.__gotoTable = GotoTable()
        while(len(bfsQueue) > 0):
            currentState = bfsQueue.popleft()
            if visited[currentState]:
                continue
            currentItemSet = self.__getItemSetFromState(currentState)
            transitions = self.__getTransitionsFromItemSet(currentItemSet)
            for symbol in transitions:
                try:
                    if symbol == self.__eofSymbol:
                        self.__actionTable.addAccept(currentState, symbol.value)
                    else:
                        newItemSet = transitions[symbol]
                        newState = self.__getStateFromItemSet(newItemSet)
                        if not visited[newState]:
                            bfsQueue.append(newState)
                        if symbol.isTerminal():
                            self.__actionTable.addShift(currentState, symbol.value, newState)
                        else:
                            self.__gotoTable.addGoto(currentState, symbol.value, newState)
                    visited[currentState] = True
                except:
                    self.__error(f"Ill-formed grammar, please report the issue to the developer")

        productionRuleMap = {rule: i for i, rule in enumerate(self.__productionRules)}

        def getProductionRuleNumber(rule: ProductionRule):
            return productionRuleMap.get(rule, None)

        for itemSet in self.__itemSets:
            state = self.__getStateFromItemSet(itemSet)
            for item in itemSet.getItems():
                if item.isFinished():
                    productionRuleNumber = getProductionRuleNumber(ProductionRule.fromItem(item))
                    if productionRuleNumber is not None:
                        self.__actionTable.addReduce(state, productionRuleNumber)

    def __currentState(self):
        return self.__stateStack[-1]

    def __shift(self, toState: int, tokenAndLexeme: TokenAndLexeme):
        self.__parseStack.append(Symbol.terminal(tokenAndLexeme.token, tokenAndLexeme.lexeme))
        self.__stateStack.append(toState)

    def __reduce(self, ruleNumber: int):
        rule = self.__productionRules[ruleNumber]
        numberOfSymbols = rule.rhs.getNumberOfSymbols()
        self.__stateStack = self.__stateStack[:-numberOfSymbols]
        children = self.__parseStack[-numberOfSymbols:]
        self.__parseStack = self.__parseStack[:-numberOfSymbols]
        self.__parseStack.append(Symbol(rule.lhs, children))
        self.__stateStack.append(self.__gotoTable.getStateToGoTo(self.__currentState(), rule.lhs))

    def parse(self):
        self.__generateActionAndGotoTables()
        self.__parseStack: [Symbol] = []
        self.__stateStack: [int] = [0]
        tokenAndLexeme: TokenAndLexeme = self.__getNextTokenAndLexeme()
        while True:
            try:
                action: Action = self.__actionTable.getActionAtCell(self.__currentState(), tokenAndLexeme.token)
                if action.isShift():
                    self.__shift(action.toState, tokenAndLexeme)
                    tokenAndLexeme: TokenAndLexeme = self.__getNextTokenAndLexeme()
                elif action.isReduce():
                    self.__reduce(action.ruleNumber)
                elif action.isAccept():
                    return Symbol(self.__startSymbol, self.__parseStack)
            except:
                lineNumber, columnNumber = tokenAndLexeme.position
                self.__error(f"Syntax error at {lineNumber}:{columnNumber}")
