import re


class Preprocessor:
    def __init__(self, code: str):
        self.__code = code
        self.__process()

    def __removeComments(self):
        commentPattern = re.compile(r'//[^\n]*$', re.MULTILINE)
        self.__code = commentPattern.sub('', self.__code)

    def __removeTrailingWhitespaceFromLines(self):
        emptyLinePattern = re.compile(r'[ \t]+$', re.MULTILINE)
        self.__code = emptyLinePattern.sub('', self.__code)

    def __addEmptyLineAtTheEndIfNotPresent(self):
        if self.__code[-1] != '\n':
            self.__code = self.__code + '\n'

    def __process(self):
        self.__removeComments()
        self.__removeTrailingWhitespaceFromLines()
        self.__addEmptyLineAtTheEndIfNotPresent()

    def getProcessedCode(self):
        return self.__code
