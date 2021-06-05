from compiler.core.lexicalAnalyzer import LexicalAnalyzer
from compiler.core.syntaxAnalyzer import SyntaxAnalyzer
from compiler.preprocessor import Preprocessor
from compiler.grammar import grammar
from compiler.lexerPatterns import tokenizingRules, ignorePatterns
from compiler.semanticAnalyzer import SemanticAnalyzer
from compiler.symbols import NT_PROG


class Compiler:

    def __init__(self, code: str, W, H, fps, errorHandler=None):
        assert W >= 1 and H >= 1 and fps >= 1, "Width, height and FPS must be positive integers"
        self.__W = int(W)
        self.__H = int(H)
        self.__fps = int(fps)
        self.__originalCode = code
        self.__errorHandler = errorHandler

    def __runPreprocessor(self, code: str):
        preprocessor = Preprocessor(code)
        processedCode = preprocessor.getProcessedCode()
        return processedCode

    def __runLexicalAndSyntaxAnalysis(self, code: str):
        lexer = LexicalAnalyzer(code, tokenizingRules, ignorePatterns, errorHandler=self.__errorHandler)
        parser = SyntaxAnalyzer(grammar, NT_PROG, lexer.nextTokenAndLexeme, errorHandler=self.__errorHandler)
        parseTree = parser.parse()
        return parseTree

    def __runSemanticAnalyzer(self, parseTree):
        semanticAnalyzer = SemanticAnalyzer(parseTree, self.__W, self.__H, self.__fps, errorHandler=self.__errorHandler)
        game = semanticAnalyzer.getOutput()
        return game

    def compile(self):
        processedCode = self.__runPreprocessor(self.__originalCode)
        parseTree = self.__runLexicalAndSyntaxAnalysis(processedCode)
        game = self.__runSemanticAnalyzer(parseTree)
        return game
