import csv
import os

from compiler.core.lexicalAnalyzer import LexicalAnalyzer
from compiler.core.syntaxAnalyzer import SyntaxAnalyzer, Symbol
from compiler.grammar import grammar
from compiler.lexerPatterns import tokenizingRules, ignorePatterns
from compiler.preprocessor import Preprocessor
from compiler.symbols import NT_PROG


# Update this variable when you want to analyze a different source file.
SOURCE_FILE_PATH = "samples/simple.cg"
OUTPUT_DIR = "output"


def _read_source(file_path: str) -> str:
    with open(file_path, "r") as source_file:
        return source_file.read()


def _ensure_output_dir(output_dir: str = OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)


def _build_parse_tree(file_path: str) -> Symbol:
    original_code = _read_source(file_path)
    processed_code = Preprocessor(original_code).getProcessedCode()
    lexer = LexicalAnalyzer(processed_code, tokenizingRules, ignorePatterns)
    parser = SyntaxAnalyzer(grammar, NT_PROG, lexer.nextTokenAndLexeme)
    return parser.parse()


def save_language_grammar(output_path: str = None) -> str:
    """Save language grammar in BNF-like format and return output path."""
    grammar_text = grammar.getGrammarString()
    _ensure_output_dir()
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, "grammar.bnf")
    with open(output_path, "w") as grammar_file:
        grammar_file.write(grammar_text)
    return output_path


def print_language_grammar() -> str:
    """Backward-compatible alias for saving grammar to output folder."""
    return save_language_grammar()


def save_tokens_to_csv(file_path: str = SOURCE_FILE_PATH, csv_output_path: str = None, include_eof: bool = False) -> str:
    """
    Tokenize code from file_path and write tokens to a CSV with headers:
    Token, Position, Lexeme
    where Position is in line:column format.
    """
    original_code = _read_source(file_path)
    processed_code = Preprocessor(original_code).getProcessedCode()
    lexer = LexicalAnalyzer(processed_code, tokenizingRules, ignorePatterns, generateEof=include_eof)

    _ensure_output_dir()
    if csv_output_path is None:
        source_name = os.path.splitext(os.path.basename(file_path))[0]
        csv_output_path = os.path.join(OUTPUT_DIR, f"{source_name}.tokens.csv")

    with open(csv_output_path, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Token", "Position", "Lexeme"])
        for token_and_lexeme in lexer.getTokenGenerator():
            if token_and_lexeme is None:
                continue
            position = f"{token_and_lexeme.position.lineNumber}:{token_and_lexeme.position.columnNumber}"
            writer.writerow([token_and_lexeme.token, position, token_and_lexeme.lexeme])

    return csv_output_path


def _format_tree_node_label(node: Symbol) -> str:
    lexeme = node.lexeme
    if lexeme is None:
        return node.token
    return f"{node.token}: {lexeme}"


def _render_tree_lines(node: Symbol, prefix: str, is_last: bool, is_root: bool = False) -> [str]:
    connector = "" if is_root else ("└── " if is_last else "├── ")
    lines = []

    if node.lexeme is None:
        lines.append(f"{prefix}{connector}{node.token}")
    else:
        if node.token == "newline":
            escaped_newline_lexeme = node.lexeme.encode("unicode_escape").decode("utf-8")
            lines.append(f"{prefix}{connector}{node.token}: {escaped_newline_lexeme}")
        else:
            lexeme_lines = node.lexeme.split("\n")
            lines.append(f"{prefix}{connector}{node.token}: {lexeme_lines[0]}")

            lexeme_padding = " " * (len(node.token) + 2)
            continuation_prefix = prefix + ("" if is_root else ("    " if is_last else "│   "))
            for lexeme_line in lexeme_lines[1:]:
                lines.append(f"{continuation_prefix}{lexeme_padding}{lexeme_line}")

    continuation_prefix = prefix + ("" if is_root else ("    " if is_last else "│   "))

    child_prefix = continuation_prefix
    for index, child in enumerate(node.children):
        child_is_last = index == len(node.children) - 1
        lines.extend(_render_tree_lines(child, child_prefix, child_is_last, False))
    return lines


def render_ast_tree(file_path: str = SOURCE_FILE_PATH, output_path: str = None) -> str:
    """Parse source code, render unicode AST, and save to output folder."""
    parse_tree = _build_parse_tree(file_path)
    tree_output = "\n".join(_render_tree_lines(parse_tree, prefix="", is_last=True, is_root=True))
    _ensure_output_dir()
    if output_path is None:
        source_name = os.path.splitext(os.path.basename(file_path))[0]
        output_path = os.path.join(OUTPUT_DIR, f"{source_name}.ast.txt")
    with open(output_path, "w") as ast_file:
        ast_file.write(tree_output)
    return output_path

if __name__ == '__main__':
    save_language_grammar()
    save_tokens_to_csv()
    render_ast_tree()