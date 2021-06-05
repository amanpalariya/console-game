import re
from re import Pattern
from compiler.core.common.all import TokenizingRule, TokenAndLexeme, CharPosition, RhsSymbol


class LexicalAnalyzer:
    __newLineChar = '\n'

    def __init__(self, data: str, rules: [TokenizingRule], ignorePatterns: [Pattern] = [], generateEof=True, errorHandler=None):
        self.__rules = rules
        self.__ignorePatterns = ignorePatterns
        self.__originalData = data
        self.__remainingData = data
        self.__generateEof = generateEof
        self.__errorHandler = errorHandler
        self.__eofTokenAndLexeme = TokenAndLexeme(RhsSymbol.eof().value, '', self.__getCharPositionFromCharIndex(len(self.__originalData)))

    def reachedEndOfData(self):
        return len(self.__remainingData) == 0

    def isDataFinished(self):
        return self.__remainingData is None

    def __error(self, message):
        if self.__errorHandler is not None:
            self.__errorHandler(message)
        else:
            raise Exception(message)

    def __getCharPositionFromCharIndex(self, charIndex: int):
        lineNumber = 1
        columnNumber = 1
        totalCharsCounted = 0
        while(totalCharsCounted < charIndex):
            currentChar = self.__originalData[totalCharsCounted]
            if currentChar == self.__newLineChar:
                lineNumber += 1
                columnNumber = 1
            else:
                columnNumber += 1
            totalCharsCounted += 1
        return CharPosition(lineNumber, columnNumber)

    def __unexpectedTokenError(self, charIndex: int):
        lineNumber, columnNumber = self.__getCharPositionFromCharIndex(charIndex)
        self.__error(f"Unexpected token {self.__originalData[charIndex: charIndex+3]}... at {lineNumber}:{columnNumber}")

    def __getLexemeFromRule(self, rule: TokenizingRule) -> str:
        return self.__getPrefixMatchFromPattern(rule.pattern)

    def __getPrefixMatchFromPattern(self, pattern: Pattern) -> str:
        prefixMatch = pattern.match(self.__remainingData)
        if prefixMatch is not None:
            return prefixMatch.group()

    def __skipIgnorablePrefix(self):
        ignorablePrefixExists = True
        while(ignorablePrefixExists):
            ignorablePrefixExists = False
            for pattern in self.__ignorePatterns:
                ignoreString = self.__getPrefixMatchFromPattern(pattern)
                if ignoreString is not None:
                    self.__remainingData = self.__remainingData[len(ignoreString):]
                    ignorablePrefixExists = True

    def __getPrefixTokenAndLexeme(self) -> TokenAndLexeme:
        if not self.isDataFinished():
            if not self.reachedEndOfData():
                for rule in self.__rules:
                    lexeme = self.__getLexemeFromRule(rule)
                    if lexeme is not None:
                        position = self.__getCharPositionFromCharIndex(len(self.__originalData) - len(self.__remainingData))
                        self.__remainingData = self.__remainingData[len(lexeme):]
                        return TokenAndLexeme(rule.token, lexeme, position)
                self.__unexpectedTokenError(len(self.__originalData) - len(self.__remainingData))
            else:
                self.__remainingData = None
                if self.__generateEof:
                    return self.__eofTokenAndLexeme

    def nextTokenAndLexeme(self) -> TokenAndLexeme:
        if not self.isDataFinished():
            self.__skipIgnorablePrefix()
            return self.__getPrefixTokenAndLexeme()

    def getTokenGenerator(self):
        while not self.isDataFinished():
            yield self.nextTokenAndLexeme()
