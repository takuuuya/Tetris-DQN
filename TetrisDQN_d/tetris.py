
import random, time, pygame, sys
import os
import numpy as np
from pygame.locals import *

FPS = 60
BOXSIZE = 20
BOARDWIDTH = 6
BOARDHEIGHT = 20
WINDOWWIDTH = BOXSIZE*(BOARDWIDTH+2)+80
WINDOWHEIGHT =BOXSIZE*(BOARDHEIGHT+2)
BLANK = '0'
WALL = '9'

PLAYMODE = False
PLAYGAME = 20

MOVESIDEWAYSFREQ = 0.000025
MOVEDOWNFREQ = 0.00001

XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH+2) * BOXSIZE) / 2)
TOPMARGIN = WINDOWHEIGHT - ((BOARDHEIGHT+2) * BOXSIZE) - 5

#               R    G    B
WHITE = (255, 255, 255)
GRAY  = (185, 185, 185)
BLACK = (0, 0, 0)

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 140, 0)

LIGHTRED = (255, 50, 50)
LIGHTGREEN = (50, 255, 50)
LIGHTBLUE = (50, 50, 255)
LIGHTYELLOW = (255, 255, 50)
LIGHTMAGENTA = (255, 50, 255)
LIGHTCYAN = (50, 255, 255)
LIGHTORANGE = (255, 140, 50)

BORDERCOLOR = WHITE
BGCOLOR = BLACK
BLANKCOLOR = (50,50,50)
WALLCOLOR = (200, 200, 200)
TEXTCOLOR = WHITE
TEXTSHADOWCOLOR = GRAY

COLORS = (RED, BLUE, GREEN, YELLOW, MAGENTA, CYAN, ORANGE)

LIGHTCOLORS = (LIGHTRED, LIGHTBLUE, LIGHTGREEN, LIGHTYELLOW, LIGHTMAGENTA, LIGHTCYAN, LIGHTORANGE)

assert len(COLORS) == len(LIGHTCOLORS) # each color must have light color

TEMPLATEWIDTH = 5
TEMPLATEHEIGHT = 5

S_SHAPE_TEMPLATE = [['00000',
                     '00000',
                     '00110',
                     '01100',
                     '00000'],
                    ['00000',
                     '00100',
                     '00110',
                     '00010',
                     '00000']]

Z_SHAPE_TEMPLATE = [['00000',
                     '00000',
                     '01100',
                     '00110',
                     '00000'],
                    ['00000',
                     '00100',
                     '01100',
                     '01000',
                     '00000']]

I_SHAPE_TEMPLATE = [['00100',
                     '00100',
                     '00100',
                     '00100',
                     '00000'],
                    ['00000',
                     '00000',
                     '11110',
                     '00000',
                     '00000']]

O_SHAPE_TEMPLATE = [['00000',
                     '00000',
                     '01100',
                     '01100',
                     '00000']]

J_SHAPE_TEMPLATE = [['00000',
                     '01000',
                     '01110',
                     '00000',
                     '00000'],
                    ['00000',
                     '00110',
                     '00100',
                     '00100',
                     '00000'],
                    ['00000',
                     '00000',
                     '01110',
                     '00010',
                     '00000'],
                    ['00000',
                     '00100',
                     '00100',
                     '01100',
                     '00000']]

L_SHAPE_TEMPLATE = [['00000',
                     '00010',
                     '01110',
                     '00000',
                     '00000'],
                    ['00000',
                     '00100',
                     '00100',
                     '00110',
                     '00000'],
                    ['00000',
                     '00000',
                     '01110',
                     '01000',
                     '00000'],
                    ['00000',
                     '01100',
                     '00100',
                     '00100',
                     '00000']]

T_SHAPE_TEMPLATE = [['00000',
                     '00100',
                     '01110',
                     '00000',
                     '00000'],
                    ['00000',
                     '00100',
                     '00110',
                     '00100',
                     '00000'],
                    ['00000',
                     '00000',
                     '01110',
                     '00100',
                     '00000'],
                    ['00000',
                     '00100',
                     '01100',
                     '00100',
                     '00000']]

PIECES = {'Z' : Z_SHAPE_TEMPLATE,   # Red
          'J' : J_SHAPE_TEMPLATE,   # Blue
          'S' : S_SHAPE_TEMPLATE,   # Green
          'O' : O_SHAPE_TEMPLATE,   # Yellow
          'T' : T_SHAPE_TEMPLATE,   # Magenta
          'I' : I_SHAPE_TEMPLATE,   # Cyan
          'L' : L_SHAPE_TEMPLATE}   # Orange


class Tetris:
    def __init__(self):
        pygame.init()
        global FPSCLOCK, BASICFONT, BIGFONT
        self.name = os.path.splitext(os.path.basename(__file__))[0]
        self.FPSCLOCK = pygame.time.Clock()
        self.DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        self.BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
        self.BIGFONT = pygame.font.Font('freesansbold.ttf', 100)
        self.enable_actions = (0, 1, 2, 3, 4, 5)
        # setup variables for the start of the game
        #self.board = getBlankBoard()
        self.lastMoveDownTime = time.time()
        self.lastMoveSidewaysTime = time.time()
        self.lastFallTime = time.time()
        self.movingDown = False # note: there is no movingUp variable
        self.movingLeft = False
        self.movingRight = False
        self.score = 0
        self.get_score = 0
        self.removed_line = 0
        self.episode = 0
        self.calculateLevelAndFallFreq()

        self.fallingPiece = self.getNewPiece()
        self.nextPiece = self.getNewPiece()

        # variables
        self.reset()


    def update(self, action):
        """
        action:
            0: move left
            1: move right
            2: move down
            3: Right rotation
            4: Left rotation
            5: none
        """
        self.reward = 0
        self.terminal = False

        if self.fallingPiece == None:
            # No falling piece in play, so start a new piece at the top
            self.fallingPiece = self.nextPiece
            self.nextPiece = self.getNewPiece()
            self.lastFallTime = time.time() # reset lastFallTime

            if not self.isValidPosition():
                self.terminal = True
                self.reward = -1
                return # can't fit a new piece on the board, so game over


        # move left
        if action == self.enable_actions[0] and self.isValidPosition(adjX=-1):
            self.fallingPiece['x'] -= 1
            self.movingLeft = True
            self.movingRight = False
            self.lastMoveSidewaysTime = time.time()

        # move right
        elif action == self.enable_actions[1] and self.isValidPosition(adjX=1):
            self.fallingPiece['x'] += 1
            self.movingRight = True
            self.movingLeft = False
            self.lastMoveSidewaysTime = time.time()

        # rotating the piece (if there is room to rotate)
        elif (action == self.enable_actions[3]):
            self.fallingPiece['rotation'] = (self.fallingPiece['rotation'] + 1) % len(PIECES[self.fallingPiece['shape']])
            if not self.isValidPosition():
                self.fallingPiece['rotation'] = (self.fallingPiece['rotation'] - 1) % len(PIECES[self.fallingPiece['shape']])
        # rotate the other direction
        elif (action == self.enable_actions[4]):
            self.fallingPiece['rotation'] = (self.fallingPiece['rotation'] - 1) % len(PIECES[self.fallingPiece['shape']])
            if not self.isValidPosition():
                self.fallingPiece['rotation'] = (self.fallingPiece['rotation'] + 1) % len(PIECES[self.fallingPiece['shape']])

        # making the piece fall faster with the down key
        elif (action == self.enable_actions[2]):
            self.movingDown = True
            if self.isValidPosition(adjY=1):
                self.fallingPiece['y'] += 1
            self.lastMoveDownTime = time.time()

        # move the current piece all the way down
        elif action == self.enable_actions[5]:
            self.movingDown = False
            self.movingLeft = False
            self.movingRight = False
            """
            for i in range(1, BOARDHEIGHT):
                if not self.isValidPosition(adjY=i):
                    break
            self.fallingPiece['y'] += i - 1
        """


        # handle moving the piece because of user input
        if (self.movingLeft or self.movingRight) and time.time() - self.lastMoveSidewaysTime > MOVESIDEWAYSFREQ:
            if self.movingLeft and self.isValidPosition(adjX=-1):
                self.fallingPiece['x'] -= 1
            elif self.movingRight and self.isValidPosition(adjX=1):
                self.fallingPiece['x'] += 1
            self.lastMoveSidewaysTime = time.time()

        if self.movingDown and time.time() - self.lastMoveDownTime > MOVEDOWNFREQ and self.isValidPosition(adjY=1):
            self.fallingPiece['y'] += 1
            self.lastMoveDownTime = time.time()

        # let the piece fall if it is time to fall
        if time.time() - self.lastFallTime > self.fallFreq:
            # see if the piece has landed
            if not self.isValidPosition(adjY=1):
                # falling piece has landed, set it on the board
                self.addToBoard()
                self.get_score, self.reward, self.terminal, removeLine = self.removeCompleteLines()
                self.removed_line += removeLine
                self.score += self.get_score
                self.calculateLevelAndFallFreq()
                self.fallingPiece = None
                if not self.upper_board():
                    self.terminal = True
                    self.reward = -1
                    return

            else:
                # piece did not land, just move the piece down
                self.fallingPiece['y'] += 1
                self.lastFallTime = time.time()

        self.draw()
        self.FPSCLOCK.tick(FPS)

    def draw(self):
        self.DISPLAYSURF
        # drawing everything on the screen
        self.DISPLAYSURF.fill(BGCOLOR)
        self.drawBoard()
        self.drawStatus()
        self.drawNextPiece()
        if self.fallingPiece != None:
            self.drawPiece(self.fallingPiece)
        pygame.display.update()


    def get_image(self):
        self.draw()
        #image = pygame.display.get_surface()
        image = pygame.surfarray.array3d(pygame.display.get_surface())
        return image

    def observe(self):
        # screen render mode
        #if SCREEN_MODE:

        self.draw()

        """
        board_int = self.board_str2int()
        return board_int, self.reward, self.terminal
        """

        image = self.get_image()
        return image, self.reward, self.terminal


    def execute_action(self, action, e):
        self.get_episode(e)
        self.update(action)

    def reset(self):
        pygame.init()
        self.FPSCLOCK = pygame.time.Clock()
        self.DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        self.enable_actions = (0, 1, 2, 3, 4, 5)
        # setup variables for the start of the game
        self.getBlankBoard()
        self.lastMoveDownTime = time.time()
        self.lastMoveSidewaysTime = time.time()
        self.lastFallTime = time.time()
        self.movingDown = False # note: there is no movingUp variable
        self.movingLeft = False
        self.movingRight = False
        self.score = 0
        self.get_score = 0
        self.removed_line = 0
        self.episode = 0
        self.calculateLevelAndFallFreq()
        
        self.fallingPiece = self.getNewPiece()
        self.nextPiece = self.getNewPiece()

        #reset other variables
        self.reward = 0
        self.terminal = False


    def board_str2int(self):
        board_int = []
        board_int = [list(map(int, x)) for x in self.board]
        return board_int


    def get_episode(self, e):
        self.episode = e

    def makeTextObjs(text, font, color):
        surf = font.render(text, True, color)
        return surf, surf.get_rect()


    def terminate(self):
        pygame.quit()
        sys.exit()


    def upper_board(self):
        for i in range(int(BOARDWIDTH/2)-1, int(BOARDWIDTH/2)+2+1):
            if self.board[i][0] != BLANK:
                return False
        return True

    def calculateLevelAndFallFreq(self):
        # Based on the score, return the level the player is on and
        # how many seconds pass until a falling piece falls one space.

        # play mode
        if PLAYMODE:
            if self.episode >= 0 and self.episode < PLAYGAME:
                self.level = int(self.removed_line / 10) + 1
                self.fallFreq = 0.27 - (self.level * 0.02)

            else:
                self.level = int(self.removed_line / 10) + 1
                self.fallFreq = 0.0027 - (self.level * 0.0002)

        # all agent play mode
        else :
            self.level = int(self.removed_line / 10) + 1
            self.fallFreq = 0.000027 - (self.level * 0.000002)
        
    def getColor(self, shape):
        if shape == 'Z':
            color = 0

        elif shape == 'J':
            color = 1

        elif shape == 'S':
            color = 2

        elif shape == 'O':
            color = 3

        elif shape == 'T':
            color = 4

        elif shape == 'I':
            color = 5

        elif shape == 'L':
            color = 6

        return color


    def getNewPiece(self):
        # return a random new piece in a random rotation and color
        shape = random.choice(list(PIECES.keys()))
        newPiece = {'shape': shape,
                    'rotation': random.randint(0, len(PIECES[shape]) - 1),
                    'x': int(BOARDWIDTH / 2) - int(TEMPLATEWIDTH / 2),
                    'y': -1, # start it above the board (i.e. less than 0)
                    'color': self.getColor(shape)}
                    #'color': random.randint(0, len(COLORS)-1)}
        return newPiece


    def addToBoard(self):
        # fill in the board based on piece's location, shape, and rotation
        for x in range(TEMPLATEWIDTH):
            for y in range(TEMPLATEHEIGHT):
                if PIECES[self.fallingPiece['shape']][self.fallingPiece['rotation']][y][x] != BLANK:
                    self.board[x + self.fallingPiece['x']][y + self.fallingPiece['y']] = self.fallingPiece['color']


    def getBlankBoard(self):
        # create and return a new blank board data structure
        self.board = []
        for i in range(BOARDWIDTH+2):
            arr = []
            if i == 0 or i == BOARDWIDTH + 1:
                self.board.append([WALL] * (BOARDHEIGHT+2))

            elif i < (BOARDWIDTH/2)-1 or i > (BOARDWIDTH/2)+2:
                arr.append(WALL)
                for j in range(BOARDHEIGHT):
                    arr.append(BLANK)
                arr.append(WALL)
                self.board.append(arr)

            else:
                for j in range(BOARDHEIGHT+1):
                    arr.append(BLANK)
                arr.append(WALL)
                self.board.append(arr)
        return self.board





    def isOnBoard(self, x, y):
        return x >= 1 and x < BOARDWIDTH+1 and y < BOARDHEIGHT+1


    def isValidPosition(self, adjX=0, adjY=0):
        # Return True if the piece is within the board and not colliding
        for x in range(TEMPLATEWIDTH):
            for y in range(TEMPLATEHEIGHT):
                isAboveBoard = y + self.fallingPiece['y'] + adjY < 0
                if isAboveBoard or PIECES[self.fallingPiece['shape']][self.fallingPiece['rotation']][y][x] == BLANK:
                    continue
                if not self.isOnBoard(x + self.fallingPiece['x'] + adjX, y + self.fallingPiece['y'] + adjY):
                    return False
                if self.board[x + self.fallingPiece['x'] + adjX][y + self.fallingPiece['y'] + adjY] != BLANK:
                    return False
        return True

    def isCompleteLine(self, y):
        # Return True if the line filled with boxes with no gaps.
        for x in range(1, BOARDWIDTH+1):
            if self.board[x][y] == BLANK:
                return False
        return True


    def removeCompleteLines(self):
        # Remove any completed lines on the board, move everything above them down, and return the number of complete lines.
        self.numLinesRemoved = 0
        self.get_score = 0
        y = BOARDHEIGHT # start y at the bottom of the board
        while y >= 0:
            if self.isCompleteLine(y):
                # Remove the line and pull boxes down by one line.
                for pullDownY in range(y, 1, -1):
                    for x in range(1, BOARDWIDTH+1):
                        self.board[x][pullDownY] = self.board[x][pullDownY-1]
                # Set very top line to blank.
                for x in range(1, BOARDWIDTH+1):
                    self.board[x][1] = BLANK
                self.numLinesRemoved += 1
                # self.removed_line += 1
                # Note on the next iteration of the loop, y is the same.
                # This is so that if the line that was pulled down is also
                # complete, it will be removed.
                self.terminal = False
                self.reward = self.numLinesRemoved
            else:
                y -= 1 # move on to check next row up


        if self.numLinesRemoved == 1:
            self.get_score = 40 * self.level
        elif self.numLinesRemoved == 2:
            self.get_score = 100 * self.level
        elif self.numLinesRemoved == 3:
            self.get_score = 300 * self.level
        elif self.numLinesRemoved == 4:
            self.get_score = 1200 * self.level

        score = self.get_score
            
        if self.reward > 0:
            print('Complete %d Line' % self.numLinesRemoved)
            self.reward = self.get_score
            
        self.get_score = 0
        #return self.get_score, self.get_socore, self.terminal
        return score , self.reward, self.terminal, self.numLinesRemoved


    def convertToPixelCoords(self, boxx, boxy):
        # Convert the given xy coordinates of the board to xy
        # coordinates of the location on the screen.
        return ((boxx * BOXSIZE)), ((boxy * BOXSIZE))


    def drawBox(self, boxx, boxy, color, pixelx=None, pixely=None):
        # draw a single box (each tetromino piece has four boxes)
        # at xy coordinates on the board. Or, if pixelx & pixely
        # are specified, draw to the pixel coordinates stored in
        # pixelx & pixely (this is used for the "Next" piece).
        if color == BLANK:
            return
        if pixelx == None and pixely == None:
            pixelx, pixely = self.convertToPixelCoords(boxx, boxy)
        if color == BLANKCOLOR:
            pygame.draw.rect(self.DISPLAYSURF, COLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
        if color == WALLCOLOR:
            pygame.draw.rect(self.DISPLAYSURF, COLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))

        else:
            pygame.draw.rect(self.DISPLAYSURF, COLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
            pygame.draw.rect(self.DISPLAYSURF, LIGHTCOLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 4, BOXSIZE - 4))

    def drawBoard(self):
        # draw the border around the board
        # pygame.draw.rect(self.DISPLAYSURF, BORDERCOLOR, (0, TOPMARGIN - 7, ((BOARDWIDTH+2) * BOXSIZE), ((BOARDHEIGHT+2) * BOXSIZE)), 5)

        # fill the background of the board:
        pygame.draw.rect(self.DISPLAYSURF, BGCOLOR, (0, 0, BOXSIZE * (BOARDWIDTH+2), BOXSIZE * (BOARDHEIGHT+2)))
        # draw the individual boxes on the board
        for x in range(BOARDWIDTH+2):
            for y in range(BOARDHEIGHT+2):
                if self.board[x][y] == BLANK:
                    pixelx , pixely = self.convertToPixelCoords(x, y)
                    pygame.draw.rect(self.DISPLAYSURF, BLANKCOLOR, (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
                if self.board[x][y] == WALL:
                    pixelx , pixely = self.convertToPixelCoords(x, y)
                    pygame.draw.rect(self.DISPLAYSURF, WALLCOLOR, (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
                else:
                    self.drawBox(x, y, self.board[x][y])

    def drawStatus(self):
        # draw the score text
        scoreSurf = self.BASICFONT.render('Score:', True, TEXTCOLOR)
        scoreRect = scoreSurf.get_rect()
        scoreRect.topleft = (WINDOWWIDTH - 95, 10)
        self.DISPLAYSURF.blit(scoreSurf, scoreRect)
        
        scoreSurf = self.BASICFONT.render('%s' % self.score, True, TEXTCOLOR)
        scoreRect = scoreSurf.get_rect()
        scoreRect.topleft = (WINDOWWIDTH - 80, 30)
        self.DISPLAYSURF.blit(scoreSurf, scoreRect)

        # draw the level text
        levelSurf = self.BASICFONT.render('Level: %s' % self.level, True, TEXTCOLOR)
        levelRect = levelSurf.get_rect()
        levelRect.topleft = (WINDOWWIDTH - 95, 70)
        self.DISPLAYSURF.blit(levelSurf, levelRect)


    def drawPiece(self, piece, pixelx=None, pixely=None):
        shapeToDraw = PIECES[piece['shape']][piece['rotation']]
        if pixelx == None and pixely == None:
            # if pixelx & pixely hasn't been specified, use the location stored in the piece data structure
            pixelx, pixely = self.convertToPixelCoords(piece['x'], piece['y'])

        # draw each of the boxes that make up the piece
        for x in range(TEMPLATEWIDTH):
            for y in range(TEMPLATEHEIGHT):
                if shapeToDraw[y][x] != BLANK:
                    self.drawBox(None, None, piece['color'], pixelx + (x * BOXSIZE), pixely + (y * BOXSIZE))


    def drawNextPiece(self):
        # draw the "next" text
        nextSurf = self.BASICFONT.render('Next:', True, TEXTCOLOR)
        nextRect = nextSurf.get_rect()
        nextRect.topleft = (WINDOWWIDTH - 95, 110)
        self.DISPLAYSURF.blit(nextSurf, nextRect)
        # draw the "next" piece
        self.drawPiece(self.nextPiece, pixelx=WINDOWWIDTH-100, pixely=140)
