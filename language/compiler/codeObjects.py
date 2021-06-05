from copy import deepcopy
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from random import randint
import re
from compiler.core.lexicalAnalyzer import LexicalAnalyzer
from compiler.core.common.all import TokenizingRule


class ShapePixel(Enum):
    TRANSPARENT = 0
    WHITE = 1
    BLACK = 2

    @staticmethod
    def fromPixelChar(char: str):
        assert char in ['.', '+', '#'], "Invalid pixel character"
        mapping = {'.': ShapePixel.TRANSPARENT,
                   '+': ShapePixel.WHITE, '#': ShapePixel.BLACK}
        return mapping[char]


class Button:
    X = 'X'
    Y = 'Y'
    A = 'A'
    B = 'B'
    START = 'START'
    POWER = 'POWER'


class Display:
    def __init__(self, pixelArray: [[bool]], W: int, H: int):
        self.__W = W
        self.__H = H
        self.__pixelArray = [[False]*W for _ in range(H)]
        for row in range(H):
            for column in range(W):
                if (row < len(pixelArray) and column < len(pixelArray[row])):
                    self.__pixelArray[row][column] = pixelArray[row][column]
                else:
                    self.__pixelArray[row][column] = False

    @staticmethod
    def cleared(W: int, H: int):
        return Display([[False]*W]*H, W, H)

    def clear(self):
        W = self.__W
        H = self.__H
        self.__pixelArray = [[False]*W for _ in range(H)]

    def overlay(self, pixelArray: [[ShapePixel]], topLeftCoordinate=(0, 0)):
        W = self.__W
        H = self.__H
        tlX, tlY = topLeftCoordinate
        for row in range(H):
            for column in range(W):
                overlayRow, overlayColumn = row - tlY, column - tlX
                if (0 <= overlayRow < len(pixelArray) and 0 <= overlayColumn < len(pixelArray[overlayRow])):
                    shapePixel = pixelArray[overlayRow][overlayColumn]
                    if shapePixel != ShapePixel.TRANSPARENT:
                        pixelIsOn = shapePixel == ShapePixel.BLACK
                        self.__pixelArray[row][column] = pixelIsOn

    def isPixelOn(self, row, column):
        return self.__pixelArray[row][column]

    def getPixelArray(self):
        return self.__pixelArray

    def __repr__(self):
        onPixel = '#'
        offPixel = '.'
        def getPixelChar(pixel): return onPixel if pixel else offPixel
        def rowMapper(row): return ''.join(map(getPixelChar, row))
        allRowsString = '\n'.join(map(rowMapper, self.__pixelArray))
        return f"{self.__class__.__name__}(\n{allRowsString}\n)"


class Game:

    def __init__(self, states, initialStateName, shapes, W, H, fps):
        self.__states = states
        self.__initialStateName = initialStateName
        self.__shapes = shapes
        self.__W = W
        self.__H = H
        self.__fps = fps
        self.__createConstants()
        self.reset()

    def updateConstants(self, W, H, fps):
        self.__W = W
        self.__H = H
        self.__fps = fps
        self.__createConstants()
        self.reset()

    def getWidth(self):
        return self.__W

    def getHeight(self):
        return self.__H

    def getFps(self):
        return self.__fps

    def __createConstants(self):
        self.__constants = {'!W': self.__W, '!H': self.__H, '!FPS': self.__fps}

    def __currentState(self):
        return self.__states[self.__currentStateName]

    def reset(self):
        self.__variables = defaultdict(int)
        self.__currentStateName = self.__initialStateName
        self.__display = Display.cleared(self.__W, self.__H)

    def _getVariables(self):
        return self.__variables

    def _getConstants(self):
        return self.__constants

    def onXPress(self):
        self.__currentState().onXPressed(self)

    def onYPress(self):
        self.__currentState().onYPressed(self)

    def onAPress(self):
        self.__currentState().onAPressed(self)

    def onBPress(self):
        self.__currentState().onBPressed(self)

    def onStartPress(self):
        self.__currentState().onStartPressed(self)

    def tick(self):
        self.__currentState().run(self)

    def setVariable(self, varName, value: int):
        self.__variables[varName] = value

    def getVariable(self, varName) -> int:
        return self.__variables[varName]

    def getConstant(self, constName) -> int:
        return self.__constants[constName]

    def getShape(self, shapeName):
        return self.__shapes[shapeName]

    def overlayShapeOnScreen(self, shape, coordinate):
        self.__display.overlay(shape.getShapePixelArray(), coordinate)

    def clearScreen(self):
        self.__display.clear()

    def getDisplay(self):
        return self.__display

    def jumpToState(self, targetStateName: str):
        self.__currentStateName = targetStateName


class Statement:

    def run(self, game) -> bool:
        raise Exception("`run` method not implemented")


class GameState:

    def __init__(self, statements: [Statement], buttonHandler):
        self.__statements = statements
        self.__buttonHandlers = buttonHandler

    def __onButtonPressed(self, game, button: Button):
        for stmt in self.__buttonHandlers.get(button, []):
            shouldMoveToNextStatement = stmt.run(game)
            if not shouldMoveToNextStatement:
                return

    def onXPressed(self, game):
        self.__onButtonPressed(game, Button.X)

    def onYPressed(self, game):
        self.__onButtonPressed(game, Button.Y)

    def onAPressed(self, game):
        self.__onButtonPressed(game, Button.A)

    def onBPressed(self, game):
        self.__onButtonPressed(game, Button.B)

    def onStartPressed(self, game):
        self.__onButtonPressed(game, Button.START)

    def run(self, game):
        for stmt in self.__statements:
            shouldMoveToNextStatement = stmt.run(game)
            if not shouldMoveToNextStatement:
                return


class BinaryOperator:

    __precedence = defaultdict(lambda: 0, {
        '|': 1,
        '&': 1,
        '~=': 2,
        '=': 2,
        '<': 2,
        '>': 2,
        '>=': 2,
        '<=': 2,
        '-': 3,
        '+': 3,
        '*': 4,
        '/': 4,
        '%': 4,
    })

    __binaryOperationMap = {
        '>=': lambda a, b: 1 if a >= b else 0,
        '<=': lambda a, b: 1 if a <= b else 0,
        '>': lambda a, b: 1 if a > b else 0,
        '<': lambda a, b: 1 if a < b else 0,
        '&': lambda a, b: 1 if a and b else 0,
        '|': lambda a, b: 1 if a or b else 0,
        '~=': lambda a, b: 1 if a != b else 0,
        '=': lambda a, b: 1 if a == b else 0,
        '+': lambda a, b: a + b,
        '-': lambda a, b: a - b,
        '*': lambda a, b: a * b,
        '/': lambda a, b: a // b,
        '%': lambda a, b: a % b,
    }

    def __init__(self, opStr):
        assert opStr in self.__binaryOperationMap.keys(
        ), f"Invalid operator {opStr}"
        self.__opStr = opStr

    def getPrecedence(self):
        return self.__precedence[self.__opStr]

    def eval(self, operand1: int, operand2: int):
        assert type(operand1) == int and type(
            operand2) == int, f"Operators should be integer, got {operand1} ({type(operand1)}) and {operand2} ({type(operand2)})"
        return self.__binaryOperationMap[self.__opStr](operand1, operand2)


class UnaryOperator:

    __unaryOperationMap = {
        '+': lambda x: +x,
        '-': lambda x: -x,
        '~': lambda x: 0 if x else 1,
    }

    def __init__(self, opStr):
        self.__opStr = opStr

    def eval(self, operand: int):
        assert type(operand) == int, f"Operator should be integer, got {operand} ({type(operand)})"
        return self.__unaryOperationMap[self.__opStr](operand)


class Expression:
    __T_LEFT_PAREN = 'left-paren'
    __T_RIGHT_PAREN = 'right-paren'
    __T_VARIABLE = 'variable'
    __T_CONSTANT = 'constant'
    __T_LITERAL = 'literal'
    __T_OPERATOR = 'operator'

    __tokenizingRules = [
        TokenizingRule(__T_LEFT_PAREN, re.compile(r"\(")),
        TokenizingRule(__T_RIGHT_PAREN, re.compile(r"\)")),
        TokenizingRule(__T_VARIABLE, re.compile(r"\$[\w\d_]+")),
        TokenizingRule(__T_CONSTANT, re.compile(r"![\w\d_]+")),
        TokenizingRule(__T_OPERATOR, re.compile(
            r"(>=|<=|>|<|~=|=|&|\||~|\+|-|\*|/|%)")),
        TokenizingRule(__T_LITERAL, re.compile(r"\d+")),
    ]

    __ignorePatterns = [
        re.compile(r'[ ]+')
    ]

    def __init__(self, exprString, errorHandler=None):
        self.__exprString = exprString
        tokenizer = LexicalAnalyzer(
            self.__exprString[1:-1], self.__tokenizingRules, self.__ignorePatterns, generateEof=False)
        self.__tokens = list(filter(bool, tokenizer.getTokenGenerator()))
        self.__errorHandler = errorHandler

    def __error(self, message):
        if self.__errorHandler is not None:
            self.__errorHandler(message)
        else:
            raise Exception(message)

    def __getValue(self, game):
        prevWasNumber = False
        numStack = []
        opStack = []

        def pushNumber(num):
            while len(opStack) > 0 and type(opStack[-1]) == UnaryOperator:
                prevOp: UnaryOperator = opStack.pop()
                num = prevOp.eval(num)
            numStack.append(num)

        def evalLast():
            prevOp: BinaryOperator = opStack.pop()
            b = numStack.pop()
            a = numStack.pop()
            c = prevOp.eval(a, b)
            pushNumber(c)

        for tokenAndLexeme in self.__tokens:
            token = tokenAndLexeme.token
            lexeme = tokenAndLexeme.lexeme
            if token == self.__T_LEFT_PAREN:
                opStack.append(token)
                prevWasNumber = False
            elif token == self.__T_RIGHT_PAREN:
                while len(opStack) > 0 and opStack[-1] != self.__T_LEFT_PAREN:
                    evalLast()
                opStack.pop()
                pushNumber(numStack.pop())
                prevWasNumber = True
            elif token == self.__T_OPERATOR:
                if prevWasNumber:
                    currentOp = BinaryOperator(lexeme)
                    while len(opStack) > 0 and type(opStack[-1]) == BinaryOperator and opStack[-1].getPrecedence()>=currentOp.getPrecedence():
                        evalLast()
                    opStack.append(currentOp)
                else:
                    currentOp = UnaryOperator(lexeme)
                    opStack.append(currentOp)
                prevWasNumber = False
            elif token == self.__T_LITERAL:
                number = int(lexeme)
                pushNumber(number)
                prevWasNumber = True
            elif token == self.__T_VARIABLE:
                number = game.getVariable(lexeme)
                pushNumber(number)
                prevWasNumber = True
            elif token == self.__T_CONSTANT:
                number = game.getConstant(lexeme)
                pushNumber(number)
                prevWasNumber = True
        while len(numStack) > 1:
            evalLast()
        return numStack[0]

    def getValue(self, game):
        try:
            return self.__getValue(game)
        except ZeroDivisionError:
            self.__error(f"Cannot divide by zero, problem in expression {self.__exprString}")
        except:
            self.__error(f"Invalid expression {self.__exprString}, please refer to language documentation")


class RandomExpression(Expression):
    def __init__(self, expr1, expr2):
        self.__expr1 = expr1
        self.__expr2 = expr2

    def getValue(self, game):
        m, M = sorted([self.__expr1.getValue(game),
                      self.__expr2.getValue(game)])
        return randint(m, M)


class VariableUpdateStatement(Statement):

    def __init__(self, name: str, expr: Expression):
        self.__name = name
        self.__expr = expr

    def run(self, game):
        game.setVariable(self.__name, self.__expr.getValue(game))
        return True


class SelectionStatement(Statement):

    def __init__(self, conditionExpr: Expression, statements: [Statement]):
        self._conditionExpr = conditionExpr
        self._statements = statements

    def _conditionIsTrue(self, game):
        raise Exception("_conditionIsTrue method not implemented")

    def run(self, game):
        if self._conditionIsTrue(game):
            for stmt in self._statements:
                moveToNextStatement = stmt.run(game)
                if not moveToNextStatement:
                    return False
        return True


class IfStatement(SelectionStatement):
    def _conditionIsTrue(self, game):
        return self._conditionExpr.getValue(game) != 0


class IfNotStatement(SelectionStatement):
    def _conditionIsTrue(self, game):
        return self._conditionExpr.getValue(game) == 0


class ScreenUpdateStatement(Statement):

    def _clear(self, game):
        game.clearScreen()

    def _overlay(self, game, shapeName, coordinate):
        shape = game.getShape(shapeName)
        game.overlayShapeOnScreen(shape, coordinate)


class ClearScreenStatement(ScreenUpdateStatement):
    def __init__(self):
        pass

    def run(self, game):
        self._clear(game)
        return True


class DisplayShapeStatement(ScreenUpdateStatement):
    def __init__(self, shapeName: str, xPosExpr: Expression, yPosExpr: Expression):
        self.__shapeName = shapeName
        self.__xPosExpr = xPosExpr
        self.__yPosExpr = yPosExpr

    def run(self, game):
        coordinate = (self.__xPosExpr.getValue(game),
                      self.__yPosExpr.getValue(game))
        self._overlay(game, self.__shapeName, coordinate)
        return True


class GotoStatement(Statement):
    def __init__(self, targetStateName: str):
        self.__targetStateName = targetStateName

    def run(self, game):
        game.jumpToState(self.__targetStateName)
        return False


class Shape:
    def __init__(self, pixelArray: [[ShapePixel]]):
        self.__pixelArray = deepcopy(pixelArray)

    @staticmethod
    def fromShapeString(shapeString: str):
        rows = shapeString.strip().split('\n')
        def rowMapper(row): return [ShapePixel.fromPixelChar(c) for c in row]
        return Shape(list(map(rowMapper, rows)))

    def getShapePixelArray(self):
        return self.__pixelArray

    def __repr__(self):
        def getPixelChar(pixel): {ShapePixel.TRANSPARENT: ' ',
                                  ShapePixel.WHITE: '.', ShapePixel.BLACK: '#'}[pixel]

        def rowMapper(row): return ''.join(map(getPixelChar, row))
        allRowsString = '\n'.join(map(rowMapper, self.__pixelArray))
        return f"{self.__class__.__name__}(\n{allRowsString}\n)"
