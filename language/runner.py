from device.main import RetroConsole
from compiler.main import Compiler
import sys

args = sys.argv

DEFAULT_W = 30
DEFAULT_H = 30
DEFAULT_FPS = 30


def showErrorAndTerminate(message):
    print("Error:", message)
    sys.exit()


def processArgs(args):
    if len(args) < 2:
        showErrorAndTerminate('Expected input filename as the first argument')

    W, H, FPS = DEFAULT_W, DEFAULT_H, DEFAULT_FPS
    inputFilename = args[1]

    if len(args) > 2:
        try:
            W, H, FPS = int(args[2]), int(args[3]), int(args[4])
        except IndexError:
            showErrorAndTerminate(f'Expected exactly 3 positive integers (width, height, and fps) after the input filename, got {len(args)-2}')
        except ValueError:
            showErrorAndTerminate(f'Expected exactly 3 positive integers (width, height, and fps) after the input filename, got some non-integer values')
    return inputFilename, W, H, FPS


inputFilename, W, H, FPS = processArgs(sys.argv)

try:
    with open(inputFilename, 'r') as codeFile:
        code = codeFile.read()
except FileNotFoundError:
    showErrorAndTerminate(f"File '{inputFilename}' not found")

compiler = Compiler(code, W, H, FPS, errorHandler=showErrorAndTerminate)
game = compiler.compile()

device = RetroConsole(game, W, H, FPS)
device.show()
