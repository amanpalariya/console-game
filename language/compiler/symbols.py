# Terminals/tokens
# Prefixed with `T`
T_SHAPE_NAME = 'shape-name'
T_SHAPE = 'shape'

T_VARIABLE = 'variable'
T_ASSIGNMENT_OP = 'assignment-op'
T_RAND = 'rand'
T_SINGLE_EXPR = 'single-expression'

T_HANDLER_NAME = 'handler-name'

T_CLEAR = 'clear-screen'
T_DISPLAY = 'display-shape'

T_COORDINATE_OP = 'coordinate-op'
T_COMMA = 'comma'

T_LEFT_PAREN = 'left-paren'
T_RIGHT_PAREN = 'right-paren'

T_LEFT_BRACE = 'left-brace'
T_RIGHT_BRACE = 'right-brace'

T_STATE_NAME = 'state-name'
T_GOTO = 'goto'

T_IF = 'if'
T_NOT = 'not'

T_NEWLINE = 'newline'

# Non-terminals
# Prefixed with `NT`
NT_PROG = 'prog'
NT_TOP_LEVEL_STMTS = 'top-level-stmts'
NT_TOP_LEVEL_STMT = 'top-level-stmt'

NT_SHAPE_DEF = 'shape-def'

NT_STATE_DEF = 'state-def'
NT_INSTATE_STMTS = 'instate-stmts'
NT_INSTATE_STMT = 'instate-stmt'

NT_VARIABLE_ASSIGN_STMT = 'variable-update-stmt'
NT_SCREEN_UPDATE_STMT = 'screen-update-stmt'
NT_GOTO_STMT = 'goto-stmt'
NT_EXPR = 'expression'

NT_IF_STMTS = 'if-stmts'
NT_IF_STMT = 'if-stmt'
NT_IF_NOT_STMT = 'if-not-stmt'
NT_INIF_STMTS = 'inif-stmts'
NT_INIF_STMT = 'inif-stmt'

NT_BTN_HANDLER = 'btn-handler'
NT_INHANDLER_STMTS = 'inhandler-stmts'
NT_INHANDLER_STMT = 'inhandler-stmt'
