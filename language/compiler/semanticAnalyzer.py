from compiler.symbols import *
from compiler.codeObjects import *


class SemanticAnalyzer:

    def __init__(self, parseTreeRoot, W, H, fps, errorHandler=None):
        assert W >= 1 and H >= 1 and fps >= 1, "Width, height and FPS must be positive integers"
        self.__W = int(W)
        self.__H = int(H)
        self.__fps = int(fps)
        self.__root = parseTreeRoot
        self.__errorHandler = errorHandler

    def __error(self, message):
        if self.__errorHandler is not None:
            self.__errorHandler(message)
        else:
            raise Exception(message)

    def getOutput(self):
        return self.__prog(self.__root.children)

    def __singleExpr(self, exprString):
        return Expression(exprString, errorHandler=self.__errorHandler)

    def __randomExpr(self, expr1String, expr2String):
        expr1 = self.__singleExpr(expr1String)
        expr2 = self.__singleExpr(expr2String)
        return RandomExpression(expr1, expr2)

    def __expr(self, children):
        if children[0].token == T_SINGLE_EXPR:
            expr, = children
            return self.__singleExpr(expr.lexeme)
        elif children[0].token == T_RAND:
            _, expr1, expr2 = children
            return self.__randomExpr(expr1.lexeme, expr2.lexeme)

    def __shape(self, shapeString):
        return Shape.fromShapeString(shapeString)

    def __prog(self, children):
        initialStateName, _, topLevelStmts, _ = children
        shapes, states = self.__topLevelStmts(topLevelStmts.children)
        return Game(states, initialStateName.lexeme, shapes, self.__W, self.__H, self.__fps)

    def __topLevelStmts(self, children):
        if children[0].token == NT_TOP_LEVEL_STMTS:
            topLevelStmts, _, topLevelStmt = children
            shapes1, states1 = self.__topLevelStmts(topLevelStmts.children)
            shapes2, states2 = self.__topLevelStmt(topLevelStmt.children)
            return {**shapes1, **shapes2}, {**states1, **states2}
        elif children[0].token == NT_TOP_LEVEL_STMT:
            topLevelStmt, = children
            shapes, states = self.__topLevelStmt(topLevelStmt.children)
            return shapes, states

    def __topLevelStmt(self, children):
        if children[0].token == NT_SHAPE_DEF:
            shapeDef, = children
            shapeName, shape = self.__shapeDef(shapeDef.children)
            return {shapeName: shape}, {}
        elif children[0].token == NT_STATE_DEF:
            stateDef, = children
            stateName, state = self.__stateDef(stateDef.children)
            return {}, {stateName: state}

    def __shapeDef(self, children):
        shapeName, _, _, shape, _ = children
        shape = self.__shape(shape.lexeme)
        return shapeName.lexeme, shape

    def __stateDef(self, children):
        stateName, _, _, instateStmts, _, _ = children
        statements, handlers = self.__instateStmts(instateStmts.children)
        return stateName.lexeme, GameState(StatementsBlock(statements), handlers)

    def __instateStmts(self, children):
        if children[0].token == NT_INSTATE_STMTS:
            instateStmts, _, instateStmt = children
            statements1, handlers1 = self.__instateStmts(instateStmts.children)
            statements2, handlers2 = self.__instateStmt(instateStmt.children)
            return [*statements1, *statements2], {**handlers1, **handlers2}
        elif children[0].token == NT_INSTATE_STMT:
            instateStmt, = children
            statements, handlers = self.__instateStmt(instateStmt.children)
            return statements, handlers

    def __instateStmt(self, children):
        if children[0].token == NT_VARIABLE_ASSIGN_STMT:
            variableAssignStmt, = children
            statement = self.__variableAssignStmt(variableAssignStmt.children)
            return [statement], {}
        elif children[0].token == NT_SCREEN_UPDATE_STMT:
            screenUpdateStmt, = children
            statement = self.__screenUpdateStmt(screenUpdateStmt.children)
            return [statement], {}
        elif children[0].token == NT_GOTO_STMT:
            gotoStmt, = children
            statement = self.__gotoStmt(gotoStmt.children)
            return [statement], {}
        elif children[0].token == NT_SELECTION_STMT:
            selectionStmt, = children
            statement = self.__selectionStmt(selectionStmt.children)
            return [statement], {}
        elif children[0].token == NT_ITERATION_STMT:
            iterationStmt, = children
            statement = self.__iterationStmt(iterationStmt.children)
            return [statement], {}
        elif children[0].token == NT_BTN_HANDLER:
            btnHandler, = children
            handler = self.__btnHandler(btnHandler.children)
            return [], {**handler}

    def __variableAssignStmt(self, children):
        variableName, _, expr = children
        expr = self.__expr(expr.children)
        return VariableUpdateStatement(variableName.lexeme, expr)

    def __screenUpdateStmt(self, children):
        if children[0].token == T_CLEAR:
            return self.__clear()
        elif children[0].token == T_DISPLAY:
            _, shapeName, _, _, xExpr, _, yExpr, _ = children
            xExpr = self.__expr(xExpr.children)
            yExpr = self.__expr(yExpr.children)
            return self.__display(shapeName.lexeme, xExpr, yExpr)

    def __clear(self):
        return ClearScreenStatement()

    def __display(self, shapeName, xExpr, yExpr):
        return DisplayShapeStatement(shapeName, xExpr, yExpr)

    def __gotoStmt(self, children):
        _, stateName = children
        return GotoStatement(stateName.lexeme)

    def __selectionStmt(self, children):
        if children[0].token == NT_IF_STMT:
            ifStmt, = children
            return self.__ifStmt(ifStmt.children)
        elif children[0].token == NT_IF_NOT_STMT:
            ifNotStmt, = children
            return self.__ifNotStmt(ifNotStmt.children)

    def __ifStmt(self, children):
        _, conditionExpr, _, _, inifStmts, _, _ = children
        statements = self.__inifStmts(inifStmts.children)
        conditionExpr = self.__expr(conditionExpr.children)
        return IfStatement(conditionExpr, StatementsBlock(statements))

    def __ifNotStmt(self, children):
        _, _, conditionExpr, _, _, inifStmts, _, _ = children
        statements = self.__inifStmts(inifStmts.children)
        conditionExpr = self.__expr(conditionExpr.children)
        return IfNotStatement(conditionExpr, StatementsBlock(statements))

    def __inifStmts(self, children):
        if children[0].token == NT_INIF_STMTS:
            inifStmts, _, inifStmt = children
            statements = self.__inifStmts(inifStmts.children)
            statement = self.__inifStmt(inifStmt.children)
            return [*statements, statement]
        elif children[0].token == NT_INIF_STMT:
            inifStmt, = children
            statement = self.__inifStmt(inifStmt.children)
            return [statement]

    def __inifStmt(self, children):
        if children[0].token == NT_VARIABLE_ASSIGN_STMT:
            variableAssignStmt, = children
            return self.__variableAssignStmt(variableAssignStmt.children)
        elif children[0].token == NT_SCREEN_UPDATE_STMT:
            screenUpdateStmt, = children
            return self.__screenUpdateStmt(screenUpdateStmt.children)
        elif children[0].token == NT_GOTO_STMT:
            gotoStmt, = children
            return self.__gotoStmt(gotoStmt.children)
        elif children[0].token == NT_SELECTION_STMT:
            selectionStmt, = children
            return self.__selectionStmt(selectionStmt.children)
        elif children[0].token == NT_ITERATION_STMT:
            iterationStmt, = children
            return self.__iterationStmt(iterationStmt.children)

    def __iterationStmt(self, children):
        if children[0].token == NT_WHILE_STMT:
            whileStmt, = children
            return self.__whileStmt(whileStmt.children)
        elif children[0].token == NT_WHILE_NOT_STMT:
            whileNotStmt, = children
            return self.__whileNotStmt(whileNotStmt.children)

    def __whileStmt(self, children):
        _, conditionExpr, _, _, inwhileStmts, _, _ = children
        statements = self.__inwhileStmts(inwhileStmts.children)
        conditionExpr = self.__expr(conditionExpr.children)
        return WhileStatement(conditionExpr, StatementsBlock(statements))

    def __whileNotStmt(self, children):
        _, _, conditionExpr, _, _, inwhileStmts, _, _ = children
        statements = self.__inwhileStmts(inwhileStmts.children)
        conditionExpr = self.__expr(conditionExpr.children)
        return WhileNotStatement(conditionExpr, StatementsBlock(statements))

    def __inwhileStmts(self, children):
        if children[0].token == NT_INWHILE_STMTS:
            inwhileStmts, _, inwhileStmt = children
            statements = self.__inwhileStmts(inwhileStmts.children)
            statement = self.__inwhileStmt(inwhileStmt.children)
            return [*statements, statement]
        elif children[0].token == NT_INWHILE_STMT:
            inwhileStmt, = children
            statement = self.__inwhileStmt(inwhileStmt.children)
            return [statement]

    def __inwhileStmt(self, children):
        if children[0].token == NT_VARIABLE_ASSIGN_STMT:
            variableAssignStmt, = children
            return self.__variableAssignStmt(variableAssignStmt.children)
        elif children[0].token == NT_SCREEN_UPDATE_STMT:
            screenUpdateStmt, = children
            return self.__screenUpdateStmt(screenUpdateStmt.children)
        elif children[0].token == NT_GOTO_STMT:
            gotoStmt, = children
            return self.__gotoStmt(gotoStmt.children)
        elif children[0].token == NT_SELECTION_STMT:
            selectionStmt, = children
            return self.__selectionStmt(selectionStmt.children)
        elif children[0].token == NT_ITERATION_STMT:
            iterationStmt, = children
            return self.__iterationStmt(iterationStmt.children)

    def __btnHandler(self, children):
        handlerName, _, _, inhandlerStmts, _, _ = children
        statements = self.__inhandlerStmts(inhandlerStmts.children)
        def getButtonFromName(name): return {'@X': Button.X, '@Y': Button.Y, '@A': Button.A, '@B': Button.B, '@START': Button.START}.get(name)
        return {getButtonFromName(handlerName.lexeme): statements}

    def __inhandlerStmts(self, children):
        if children[0].token == NT_INHANDLER_STMTS:
            inhandlerStmts, _, inhandlerStmt = children
            statements = self.__inhandlerStmts(inhandlerStmts.children)
            statement = self.__inhandlerStmt(inhandlerStmt.children)
            return [*statements, statement]
        elif children[0].token == NT_INHANDLER_STMT:
            inhandlerStmt, = children
            statement = self.__inhandlerStmt(inhandlerStmt.children)
            return [statement]

    def __inhandlerStmt(self, children):
        if children[0].token == NT_VARIABLE_ASSIGN_STMT:
            variableAssignStmt, = children
            return self.__variableAssignStmt(variableAssignStmt.children)
        elif children[0].token == NT_SCREEN_UPDATE_STMT:
            screenUpdateStmt, = children
            return self.__screenUpdateStmt(screenUpdateStmt.children)
        elif children[0].token == NT_GOTO_STMT:
            gotoStmt, = children
            return self.__gotoStmt(gotoStmt.children)
        elif children[0].token == NT_SELECTION_STMT:
            selectionStmt, = children
            return self.__selectionStmt(selectionStmt.children)
        elif children[0].token == NT_ITERATION_STMT:
            iterationStmt, = children
            return self.__iterationStmt(iterationStmt.children)
