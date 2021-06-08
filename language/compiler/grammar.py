from compiler.core.common.all import Grammar, GrammarRuleRhs, RhsSymbol
from compiler.symbols import *

# Helper methods and variables for commonly used tasks and to keep the grammar definition clean


def nt(name): return RhsSymbol(name)
def t(name): return RhsSymbol.terminal(name)


NL = t(T_NEWLINE)


# Grammar rules
grammar = Grammar()

grammar.add(NT_PROG,
            GrammarRuleRhs(t(T_STATE_NAME), NL, nt(NT_TOP_LEVEL_STMTS), NL, RhsSymbol.eof()),
            )
grammar.add(NT_TOP_LEVEL_STMTS,
            GrammarRuleRhs(nt(NT_TOP_LEVEL_STMTS), NL, nt(NT_TOP_LEVEL_STMT)),
            GrammarRuleRhs(nt(NT_TOP_LEVEL_STMT)),
            )
grammar.add(NT_TOP_LEVEL_STMT,
            GrammarRuleRhs(nt(NT_SHAPE_DEF)),
            GrammarRuleRhs(nt(NT_STATE_DEF)),
            )
grammar.add(NT_SHAPE_DEF,
            GrammarRuleRhs(t(T_SHAPE_NAME), t(T_LEFT_BRACE), NL, t(T_SHAPE), t(T_RIGHT_BRACE)),
            )
grammar.add(NT_STATE_DEF,
            GrammarRuleRhs(t(T_STATE_NAME), t(T_LEFT_BRACE), NL, nt(NT_INSTATE_STMTS), NL, t(T_RIGHT_BRACE)),
            )
grammar.add(NT_INSTATE_STMTS,
            GrammarRuleRhs(nt(NT_INSTATE_STMTS), NL, nt(NT_INSTATE_STMT)),
            GrammarRuleRhs(nt(NT_INSTATE_STMT)),
            )
grammar.add(NT_INSTATE_STMT,
            GrammarRuleRhs(nt(NT_VARIABLE_ASSIGN_STMT)),
            GrammarRuleRhs(nt(NT_SCREEN_UPDATE_STMT)),
            GrammarRuleRhs(nt(NT_GOTO_STMT)),
            GrammarRuleRhs(nt(NT_SELECTION_STMT)),
            GrammarRuleRhs(nt(NT_BTN_HANDLER)),
            )
grammar.add(NT_EXPR,
            GrammarRuleRhs(t(T_SINGLE_EXPR)),
            GrammarRuleRhs(t(T_RAND), t(T_SINGLE_EXPR), t(T_SINGLE_EXPR)),
            )
grammar.add(NT_VARIABLE_ASSIGN_STMT,
            GrammarRuleRhs(t(T_VARIABLE), t(T_ASSIGNMENT_OP), nt(NT_EXPR)),
            )
grammar.add(NT_SCREEN_UPDATE_STMT,
            GrammarRuleRhs(t(T_CLEAR)),
            GrammarRuleRhs(t(T_DISPLAY), t(T_SHAPE_NAME), t(T_COORDINATE_OP), t(T_LEFT_PAREN), nt(NT_EXPR), t(T_COMMA), nt(NT_EXPR), t(T_RIGHT_PAREN)),
            )
grammar.add(NT_GOTO_STMT,
            GrammarRuleRhs(t(T_GOTO), t(T_STATE_NAME)),
            )
grammar.add(NT_SELECTION_STMT,
            GrammarRuleRhs(nt(NT_IF_STMT)),
            GrammarRuleRhs(nt(NT_IF_NOT_STMT)),
            )
grammar.add(NT_IF_STMT,
            GrammarRuleRhs(t(T_IF), nt(NT_EXPR), t(T_LEFT_BRACE), NL, nt(NT_INIF_STMTS), NL, t(T_RIGHT_BRACE)),
            )
grammar.add(NT_IF_NOT_STMT,
            GrammarRuleRhs(t(T_IF), t(T_NOT), nt(NT_EXPR), t(T_LEFT_BRACE), NL, nt(NT_INIF_STMTS), NL, t(T_RIGHT_BRACE)),
            )
grammar.add(NT_INIF_STMTS,
            GrammarRuleRhs(nt(NT_INIF_STMTS), NL, nt(NT_INIF_STMT)),
            GrammarRuleRhs(nt(NT_INIF_STMT)),
            )
grammar.add(NT_INIF_STMT,
            GrammarRuleRhs(nt(NT_VARIABLE_ASSIGN_STMT)),
            GrammarRuleRhs(nt(NT_SCREEN_UPDATE_STMT)),
            GrammarRuleRhs(nt(NT_GOTO_STMT)),
            GrammarRuleRhs(nt(NT_SELECTION_STMT)),
            )
grammar.add(NT_BTN_HANDLER,
            GrammarRuleRhs(t(T_HANDLER_NAME), t(T_LEFT_BRACE), NL, nt(NT_INHANDLER_STMTS), NL, t(T_RIGHT_BRACE)),
            )
grammar.add(NT_INHANDLER_STMTS,
            GrammarRuleRhs(nt(NT_INHANDLER_STMTS), NL, nt(NT_INHANDLER_STMT)),
            GrammarRuleRhs(nt(NT_INHANDLER_STMT)),
            )
grammar.add(NT_INHANDLER_STMT,
            GrammarRuleRhs(nt(NT_VARIABLE_ASSIGN_STMT)),
            GrammarRuleRhs(nt(NT_SCREEN_UPDATE_STMT)),
            GrammarRuleRhs(nt(NT_GOTO_STMT)),
            GrammarRuleRhs(nt(NT_SELECTION_STMT)),
            )
