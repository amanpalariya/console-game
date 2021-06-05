import pygame
import random
import sys
from pygame import gfxdraw
from collections import namedtuple
from pygame.locals import *
from . import colors
from enum import Enum

Size = namedtuple('Size', ['width', 'height'])
Position = namedtuple('Position', ['x', 'y'])


class PixelState(Enum):
    Off = -1
    On0 = 0
    On1 = 1


class RetroConsole:
    def __init__(self, game, W, H, fps):
        assert W >= 1 and H >= 1 and fps >= 1, "Width, height and FPS must be positive integers"
        W = int(W)
        H = int(H)
        fps = int(fps)
        if not (game.getWidth() == W and game.getHeight() == H and game.getFps() == fps):
            raise Exception(f"Game ({game.getWidth()}×{game.getHeight()} @ {game.getFps()}Hz) does not support this device ({W}×{H} @ {fps}Hz)")
        self.__clockFrequencyInHertz = fps
        self.__displaySizeInPixels = Size(W, H)

        width = 640
        height = int(13/9*width)
        self.__pygameSurfaceSize = Size(width, height)
        self.__margin = int(self.__pygameSurfaceSize.width*0.1)
        self.__buttonAreaSize = Size(self.__pygameSurfaceSize.width - 2*self.__margin, int((self.__pygameSurfaceSize.height - 2*self.__margin)*0.3))
        self.__screenAreaSize = Size(self.__pygameSurfaceSize.width - 2*self.__margin, int((self.__pygameSurfaceSize.height - 2*self.__margin)*0.7))
        self.__pixelSize = min(self.__screenAreaSize.width//W, self.__screenAreaSize.height//H)

        self.__bodyColor = colors.blue700
        self.__bodyTextureColor = colors.blue800
        self.__bodySideColor = colors.blue900
        self.__buttonHoleColor = colors.blue900
        self.__pixelColor = {PixelState.Off: colors.gray800,
                             PixelState.On0: colors.gray600, PixelState.On1: colors.gray900}
        self.__pixelSeparatorColor = {0: colors.gray800, 1: colors.gray700}
        self.__buttonColor = {0: colors.gray200, 1: colors.gray600}
        self.__buttonSideColor = colors.indigo100
        self.__buttonTextColor = {0: colors.gray700, 1: colors.gray900}

        self.__screenDepthFromBody = 10
        self.__buttonHeight = 10
        self.__buttonHoleGap = 4

        self.__displaySurface = None
        self.__isRunning = None

        self.__isPoweredOn = False
        self.aValueForTesting = 0
        self.__game = game

    def show(self):
        pygame.init()
        fpsClock = pygame.time.Clock()

        self.__isRunning = True
        self.__displaySurface = pygame.display.set_mode(
            self.__pygameSurfaceSize)
        sizeString = f"{self.__displaySizeInPixels.width}×{self.__displaySizeInPixels.height}"
        freqString = f"{self.__clockFrequencyInHertz}Hz"
        pygame.display.set_caption(f"Retro Console - {sizeString} @ {freqString}")
        while self.__isRunning:
            self.__checkQuitEvent()
            self.__checkButtonPress()
            self.__draw()
            self.__update()
            fpsClock.tick(self.__clockFrequencyInHertz)

    def __checkQuitEvent(self):
        for event in pygame.event.get(QUIT):
            if event.type == QUIT:
                self.__isRunning = False
                pygame.quit()
                sys.exit()

    def __checkButtonPress(self):
        pressedKeys = pygame.key.get_pressed()
        self.__xHeldDown = pressedKeys[K_LEFT] | pressedKeys[K_x]
        self.__yHeldDown = pressedKeys[K_UP] | pressedKeys[K_y]
        self.__aHeldDown = pressedKeys[K_DOWN] | pressedKeys[K_a]
        self.__bHeldDown = pressedKeys[K_RIGHT] | pressedKeys[K_b]
        self.__powerHeldDown = pressedKeys[K_RETURN]
        self.__startHeldDown = pressedKeys[K_SPACE]
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key in [K_LEFT, K_x]:
                    self.__handleXPress()
                if event.key in [K_UP, K_y]:
                    self.__handleYPress()
                if event.key in [K_DOWN, K_a]:
                    self.__handleAPress()
                if event.key in [K_RIGHT, K_b]:
                    self.__handleBPress()
                if event.key in [K_RETURN]:
                    self.__handlePowerPress()
                if event.key in [K_SPACE]:
                    self.__handleStartPress()

    def __handleXPress(self):
        if self.__isPoweredOn:
            self.__game.onXPress()

    def __handleYPress(self):
        if self.__isPoweredOn:
            self.__game.onYPress()

    def __handleAPress(self):
        if self.__isPoweredOn:
            self.__game.onAPress()

    def __handleBPress(self):
        if self.__isPoweredOn:
            self.__game.onBPress()

    def __handlePowerPress(self):
        self.__isPoweredOn = not self.__isPoweredOn
        if self.__isPoweredOn:
            self.__onPowerOn()
        else:
            self.__onPowerOff()

    def __handleStartPress(self):
        if self.__isPoweredOn:
            self.__game.onStartPress()

    def __onPowerOn(self):
        ...

    def __onPowerOff(self):
        self.__game.reset()

    def __getRandomScreen(self):
        return [[(i-j) < self.aValueForTesting for i in range(self.__displaySizeInPixels.width)]
                for j in range(self.__displaySizeInPixels.height)]

    def __getScreenPixels(self):
        if self.__isPoweredOn:
            return self.__game.getDisplay().getPixelArray()
        else:
            return None

    def __draw(self):
        self.__drawBody()
        self.__drawScreen(self.__getScreenPixels())
        self.__drawButtons()

    def __drawBody(self):
        self.__displaySurface.fill(self.__bodyColor)
        strokeSize = 10
        strokeWidth = 2
        strokeColor = self.__bodyTextureColor
        def getStroke1End(position): return Position(position.x + strokeSize, position.y + strokeSize)
        def getStroke2End(position): return Position(position.x - strokeSize, position.y + strokeSize)
        for x in range(0, self.__pygameSurfaceSize.width, 2*strokeSize):
            for y in range(0, self.__pygameSurfaceSize.height, 2*strokeSize):
                start = Position(x, y)
                end = getStroke1End(start)
                self.__drawLine(start, end, strokeWidth, strokeColor)
        for x in range(-strokeSize//2, self.__pygameSurfaceSize.width, 2*strokeSize):
            for y in range(-strokeSize//2, self.__pygameSurfaceSize.height, 2*strokeSize):
                start = Position(x, y)
                end = getStroke2End(start)
                self.__drawLine(start, end, strokeWidth, strokeColor)

    def __drawScreen(self, pixels):
        W, H = self.__displaySizeInPixels
        w = W * self.__pixelSize
        h = H * self.__pixelSize
        horizontalMargin = (self.__pygameSurfaceSize.width - w)//2
        topMargin = self.__margin

        pygame.draw.line(self.__displaySurface, self.__bodySideColor,
                         (horizontalMargin, topMargin), (horizontalMargin+w, topMargin), width=self.__screenDepthFromBody*2)
        for _y in range(H):
            for _x in range(W):
                x = horizontalMargin + _x*self.__pixelSize
                y = topMargin + _y*self.__pixelSize
                self.__drawPixel(
                    Position(x, y), (PixelState.On1 if pixels[_y][_x] else PixelState.On0) if self.__isPoweredOn else PixelState.Off)

        lineColor = self.__pixelSeparatorColor[int(self.__isPoweredOn)]

        for _x in range(W+1):
            x = horizontalMargin + _x*self.__pixelSize
            x1 = x
            x2 = x
            y1 = topMargin
            y2 = topMargin + h
            pygame.draw.line(self.__displaySurface,
                             lineColor, (x1, y1), (x2, y2))
        for _y in range(H+1):
            y = topMargin + _y*self.__pixelSize
            x1 = horizontalMargin
            x2 = horizontalMargin + w
            y1 = y
            y2 = y
            pygame.draw.line(self.__displaySurface,
                             lineColor, (x1, y1), (x2, y2))

    def __drawPixel(self, position: Position, state: PixelState):
        pixelRect = Rect(*position, self.__pixelSize, self.__pixelSize)
        color = self.__pixelColor[state]
        pygame.draw.rect(self.__displaySurface, color, pixelRect)

    def __drawButtons(self):
        W, H = self.__displaySizeInPixels
        w = W * self.__pixelSize
        h = H * self.__pixelSize
        horizontalMargin = self.__margin
        bottomMargin = self.__margin
        buttonAreaSize = self.__buttonAreaSize
        controlButtonsAreaCenter = Position(self.__pygameSurfaceSize.width-horizontalMargin-buttonAreaSize.width *
                                            1/4, self.__pygameSurfaceSize.height - bottomMargin - buttonAreaSize.height*1/2)
        buttonRadius = min(buttonAreaSize.height/5, 35)
        buttonOffsetFromCenter = min(
            buttonRadius*2, buttonAreaSize.height/2 - buttonRadius)

        x_position = Position(controlButtonsAreaCenter.x -
                              buttonOffsetFromCenter, controlButtonsAreaCenter.y)
        y_position = Position(controlButtonsAreaCenter.x,
                              controlButtonsAreaCenter.y - buttonOffsetFromCenter)
        a_position = Position(controlButtonsAreaCenter.x,
                              controlButtonsAreaCenter.y + buttonOffsetFromCenter)
        b_position = Position(controlButtonsAreaCenter.x +
                              buttonOffsetFromCenter, controlButtonsAreaCenter.y)
        self.__drawRoundButton(x_position, 'X', buttonRadius, self.__xHeldDown)
        self.__drawRoundButton(y_position, 'Y', buttonRadius, self.__yHeldDown)
        self.__drawRoundButton(a_position, 'A', buttonRadius, self.__aHeldDown)
        self.__drawRoundButton(b_position, 'B', buttonRadius, self.__bHeldDown)

        powerButtonsCenter = Position(horizontalMargin+buttonAreaSize.width *
                                      1/4, self.__pygameSurfaceSize.height - bottomMargin - buttonAreaSize.height*1/2)
        lengthOfPowerButton = min(
            buttonRadius*2.5, buttonAreaSize.width/2 - 2*buttonRadius)
        buttonOffsetFromCenter = min(buttonRadius*1.5, buttonAreaSize.height/2 - buttonRadius)
        buttonRadius = min(buttonAreaSize.height/8, 25)
        buttonRadius = 30
        self.__drawCapsuleButton(
            Position(powerButtonsCenter.x, powerButtonsCenter.y - buttonOffsetFromCenter), "Power", lengthOfPowerButton, buttonRadius, self.__powerHeldDown)
        self.__drawCapsuleButton(
            Position(powerButtonsCenter.x, powerButtonsCenter.y + buttonOffsetFromCenter), "Start", lengthOfPowerButton, buttonRadius, self.__startHeldDown)
        pass

    def __drawCircle(self, position: Position, radius: float, color):
        # gfxdraw is used to created anti-aliased circle
        # gfxdraw may be removed in future versions of PyGame
        # The code in the next line is the legacy code for creating non-anti-aliased circles
        # pygame.draw.circle(self.__displaySurface, color, position, radius)
        gfxdraw.aacircle(self.__displaySurface, int(position.x), int(position.y), int(radius), Color((color << 8) + 0xff))
        gfxdraw.filled_circle(self.__displaySurface, int(position.x), int(position.y), int(radius), Color((color << 8) + 0xff))

    def __drawRect(self, position: Position, size: Size, color):
        pygame.draw.rect(self.__displaySurface, color, (*position, *size))

    def __drawLine(self, start: Position, end: Position, width: float, color):
        pygame.draw.line(self.__displaySurface, color, start, end, width)

    def __drawCapsuleButton(self, position: Position, label: str, length: float, radius: float, pressed: bool):
        buttonColor = self.__buttonColor[int(pressed)]
        buttonSideColor = self.__buttonSideColor
        buttonHoleColor = self.__buttonHoleColor
        labelColor = self.__buttonTextColor[int(pressed)]
        basePosition = Position(position.x,
                                position.y + self.__buttonHeight)
        finalPosition = position if not pressed else basePosition

        w = length
        h = 2*radius
        offset = self.__buttonHoleGap

        self.__drawRect(Position(basePosition.x - w/2 - offset, basePosition.y - h/2 - offset), Size(w+offset*2, h+offset*2), buttonHoleColor)
        self.__drawCircle(Position(basePosition.x - w/2, basePosition.y), radius + offset, buttonHoleColor)
        self.__drawCircle(Position(basePosition.x + w/2, basePosition.y), radius + offset, buttonHoleColor)

        self.__drawRect(Position(basePosition.x - w/2, basePosition.y - h/2), Size(w, h), buttonSideColor)
        self.__drawCircle(Position(basePosition.x - w/2, basePosition.y), radius, buttonSideColor)
        self.__drawCircle(Position(basePosition.x + w/2, basePosition.y), radius, buttonSideColor)

        self.__drawRect(Position(finalPosition.x - w/2, finalPosition.y - h/2), Size(w, h), buttonColor)
        self.__drawCircle(Position(finalPosition.x - w/2, finalPosition.y), radius, buttonColor)
        self.__drawCircle(Position(finalPosition.x + w/2, finalPosition.y), radius, buttonColor)

        self.__drawText(label, finalPosition, int(radius), labelColor)

    def __drawRoundButton(self, position: Position, label: str, radius: float, pressed: bool):
        buttonColor = self.__buttonColor[int(pressed)]
        buttonSideColor = self.__buttonSideColor
        buttonHoleColor = self.__buttonHoleColor
        labelColor = self.__buttonTextColor[int(pressed)]
        basePosition = Position(position.x,
                                position.y + self.__buttonHeight)
        finalPosition = position if not pressed else basePosition
        holeRadius = radius+self.__buttonHoleGap

        self.__drawCircle(basePosition, holeRadius, buttonHoleColor)

        self.__drawCircle(basePosition, radius, buttonSideColor)

        self.__drawCircle(finalPosition, radius, buttonColor)

        self.__drawText(label, finalPosition, int(radius), labelColor)

    def __drawText(self, text: str, position: Position, size: int, color, rotation: float = 0):
        font = pygame.sysfont.SysFont("Arial", size)
        renderedText = font.render(text, True, color << 8)
        rotatedRenderedText = pygame.transform.rotate(renderedText, rotation)
        rect = rotatedRenderedText.get_rect()
        rect.center = position
        self.__displaySurface.blit(rotatedRenderedText, rect)

    def __update(self):
        pygame.display.update()
        if self.__isPoweredOn:
            self.__game.tick()
