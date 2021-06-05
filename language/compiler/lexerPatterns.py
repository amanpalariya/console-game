import re
from compiler.core.common.all import TokenizingRule
from compiler.symbols import *

tokenizingRules = [
    # Keywords
    TokenizingRule(T_GOTO, re.compile(r"goto")),
    TokenizingRule(T_CLEAR, re.compile(r"clear")),
    TokenizingRule(T_DISPLAY, re.compile(r"display")),
    TokenizingRule(T_IF, re.compile(r"if")),
    TokenizingRule(T_NOT, re.compile(r"not")),
    TokenizingRule(T_RAND, re.compile(r"r")),

    # Identifiers
    TokenizingRule(T_STATE_NAME, re.compile(r"~[\w\d_]+")),
    TokenizingRule(T_SHAPE_NAME, re.compile(r"#[\w\d_]+")),
    TokenizingRule(T_HANDLER_NAME, re.compile(r"@(X|Y|A|B|START)")),
    TokenizingRule(T_VARIABLE, re.compile(r"\$[\w\d_]+")),

    # Operators
    TokenizingRule(T_ASSIGNMENT_OP, re.compile(r"=")),
    TokenizingRule(T_COORDINATE_OP, re.compile(r"@")),
    TokenizingRule(T_COMMA, re.compile(r",")),

    TokenizingRule(T_LEFT_BRACE, re.compile(r"{")),
    TokenizingRule(T_RIGHT_BRACE, re.compile(r"}")),

    TokenizingRule(T_LEFT_PAREN, re.compile(r"\(")),
    TokenizingRule(T_RIGHT_PAREN, re.compile(r"\)")),

    # Literals
    TokenizingRule(T_SHAPE, re.compile(r"[.#+][.#+\n]+")),
    TokenizingRule(T_SINGLE_EXPR, re.compile(r"\[[-+*/%><=|&~$()!\d\w_ ]+\]")),

    TokenizingRule(T_NEWLINE, re.compile(r"\n+")),
]

ignorePatterns = [
    re.compile(r"[ \t]+")
]
