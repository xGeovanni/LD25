# Invasion!
# Created for Ludum Dare 25
# Theme: "You are the villian"
# GNU Genral Public Licsense
# Bobby Clarke

#To do:
# improve upgrades GUI
# More / unique upgrades
# win condition
# better background image
# improve Startup menu
# new units: missile

#Imports
import pygame
import sys
import os
import random
import math
import pickle
from pygame.locals import *
pygame.init()

clock = pygame.time.Clock()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
gamename = "Invasion!"
pygame.display.set_caption(gamename)
pygame.mouse.set_visible(False)

red = (255, 0, 0)
green = (0, 255, 0)
black = (0, 0, 0)

def isNegative(num):
    try:
        math.sqrt(num)
        return False
    except:
        return True

def deNegate(num):
    if isNegative(num):
        return -num
    else:
        return num

class Cursor():
    def __init__(self, img = "Images/cursor.png"):
        self.img = pygame.image.load(img).convert_alpha()
    def draw(self):
        pos = [pygame.mouse.get_pos()[i] - self.img.get_size()[i] / 2
               for i in range(2)]
        
        screen.blit(self.img, pos)

class menuOption():
    def __init__(self, img, pos, clickedImg = None, startState = False):
        if isinstance(img, pygame.Surface):
            self.img = img
        else:
            self.img = pygame.image.load(img).convert_alpha()

        self.pos = pos
        self.rect = pygame.Rect(self.pos, self.img.get_size())
        self.clickedImg = clickedImg

        if startState:
            self.img, self.clickedImg = self.clickedImg, self.img

    def draw(self):
        screen.blit(self.img, self.pos)
    def checkClick(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if self.clickedImg:
                self.img, self.clickedImg = self.clickedImg, self.img # Swap

            return True
        else:
            return False

class playerInputBox():
    def __init__(self, font, colour, pos = None, maxlen = None):
        self.text = ""
        self.font = font
        if pos is None:
            self.pos = (WIDTH / 2, HEIGHT / 2)
            self.central = True
        else:
            self.pos = pos
            self.central = False
        self.colour = colour
        self.maxlen = maxlen
        self.textImg = self.font.render(self.text, True, self.colour).convert_alpha()
        
        alphabet = "abcdefghigklmnopqrstuvwxyz"
        self.key2char = {eval("K_" + char) : char for char in alphabet}
        self.key2upperchar = {eval("K_" + char) : char.upper() for char in alphabet}
        self.upperCase = False
        self.shift = False

    def draw(self):
        screen.blit(self.textImg, self.pos)

    def recentralise(self):
        self.pos = (WIDTH / 2 - self.textImg.get_width() / 2,
                    HEIGHT / 2 - self.textImg.get_height() / 2)
    
    def key_input(self, key, boolean):
        if boolean:
            if key in self.key2char and (self.maxlen is None or len(self.text) < self.maxlen):
                if (self.upperCase and not self.shift) or (self.shift and not self.upperCase):
                    self.text += self.key2upperchar[key]
                else:
                    self.text += self.key2char[key]

                self.textImg = self.font.render(self.text, True, self.colour).convert_alpha()
                if self.central:
                    self.recentralise()

            elif key == K_BACKSPACE:
                self.text = self.text[:len(self.text) - 1]
                self.textImg = self.font.render(self.text, True, self.colour).convert_alpha()
                if self.central:
                    self.recentralise()
            elif key == K_CAPSLOCK:
                if self.upperCase:
                    self.upperCase = False
                else:
                    self.upperCase = True

        if key == K_LSHIFT or key == K_RSHIFT:
            self.shift = boolean

class GUIManager():
    def __init__(self, font = "Lucida Console, Trebuchet MS, Verdana", size = 24,
                 largeSize = 72, menuColour = (0, 50, 255)):
        self.font = pygame.font.SysFont(font, size)
        self.largeFont = pygame.font.SysFont(font, largeSize)
        self.menuColour = menuColour

    def drawGUI(self, ship):
        texts = (self.font.render("Score:           " + str(ship.score),
                                True, black).convert_alpha(),
                 self.font.render("", True, black).convert(),
                 self.font.render("Scrap:           " + str(ship.scrap),
                                True, black).convert_alpha(),
                 self.font.render("Laser Power (i): " + str(ship.laserPower),
                                  True, black).convert_alpha(),
                 self.font.render("Armour (o):      " + str(ship.armour),
                                  True, black).convert_alpha(),
                 self.font.render("Speed (p):       " + str(ship.speed),
                                  True, black).convert_alpha())

        

        cumulativeHeight = 0
        for text in texts:
            screen.blit(text, (0, cumulativeHeight))
            cumulativeHeight += text.get_height()

    def menu(self, cursor, sm, hsm):
        title = self.largeFont.render(gamename, True, self.menuColour).convert_alpha()
        text = self.font.render("Press any key to begin!", True, self.menuColour).convert_alpha()
        audioButtonText = self.largeFont.render("♫", True, green).convert_alpha()
        audioButtonClickedText = self.largeFont.render("♫", True, red).convert_alpha()
        audioButton = menuOption(audioButtonText,
                                 (WIDTH - audioButtonText.get_width(), 0),
                                  audioButtonClickedText)
        highScoreButtonText = self.font.render("High Scores", True, green).convert_alpha()
        highScoreButton = menuOption(highScoreButtonText, (0, highScoreButtonText.get_height()))
        
        instructions = ("Instructions:", 
                        "WASD: Movement",
                        "Click: Fire the laser",
                        "I: Upgrade laser power with scrap",
                        "O: Upgrade ship armour with scrap",
                        "P: Upgrade ship speed with scrap",
                        "H: hold to use scrap to repair the ship",
                        "",
                        "While the laser is firing",
                        "the ship cannot be repaired as the crew is busy",
                        "",
                        "Scrap is accumulated by killing enemies",
                        "Each upgrade costs 100 scrap * your current level")

        strGoat = ("          / /    \ \                               ",
                   "         / /     / /                               ",
                   "         \ \    / /                                ",
                   "          \ \__/_/        Hey look, a goat!        ",
                   "         /    /  \                                 ",
                   "        / @   \  / \,                              ",
                   "       /       \/    \___          _______         ",
                   "       \____/         \  `--------'       `-,___   ",
                   "         ;;|                                 `_ \  ",
                   "           |                                 | \ \ ",
                   "           |                                 | /,/ ",
                   "            \                               /      ",
                   "           / \.                  |         |       ",
                   "          /  / \     /            \       /        ",
                   "         /  /   |   / `~~~~~~~~~~~'\     /         ",
                   "        /  /    |  |               |\   |          ",
                   "        \  \    |  |               | |  |          ",
                   "         \  \   |  |               | |  |          ",
                   "          \  \  |  |               | |  (          ",
                   "           \-L  |  |               | |  |          ",
                   "            \Z  |  |               | |  |          ",
                   "                |  |               | |  |          ",
                   "                |__|               |_|__|          ",   
                   "                |/\/               |/|/\/          ")

        txtInstructions = []
        for line in instructions:
            txtInstructions.append(self.font.render(line, True, self.menuColour).convert_alpha())

        txtGoat = []
        for line in strGoat:
            txtGoat.append(self.font.render(line, True, red).convert_alpha())

        goat = False
                        
        while True:
            screen.fill(black)
            if not goat:
                screen.blit(title, (WIDTH / 2 - title.get_width() / 2, 0))
                screen.blit(text, (WIDTH / 2 - text.get_width() / 2,
                                   HEIGHT - text.get_height()))
                audioButton.draw()
                highScoreButton.draw()
            
                y = sum(line.get_height() for line in txtInstructions) / 2
                for line in txtInstructions:
                    screen.blit(line, (WIDTH / 2 - line.get_width() / 2, HEIGHT / 2 + line.get_height() / 2 - y))
                    y -= line.get_height()

            else:
                y = sum(line.get_height() for line in txtGoat) / 2
                for line in txtGoat:
                    screen.blit(line, (WIDTH / 2 - line.get_width() / 2, HEIGHT / 2 + line.get_height() / 2 - y))
                    y -= line.get_height()
            
            cursor.draw()

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                elif event.type == MOUSEBUTTONDOWN:
                    if audioButton.checkClick():
                        sm.mute()
                    elif highScoreButton.checkClick():
                        self.highScoreBoard(hsm)
                elif event.type == KEYDOWN:
                    if event.key == K_TAB:
                        goat = True
                    else:
                        return True
                elif event.type == KEYUP:
                    if event.key == K_TAB:
                        goat = False

    def lose(self): # Maybe defunct
        youLose = self.largeFont.render("You Lose!", True, self.menuColour).convert_alpha()
        text = self.font.render("Press any key to return to the main menu", True, self.menuColour).convert_alpha()

        screen.fill(black)

        screen.blit(youLose, (WIDTH / 2 - youLose.get_width() / 2,
                              HEIGHT / 2 - youLose.get_height() / 2))
        screen.blit(text, (WIDTH / 2 - text.get_width() / 2,
                           HEIGHT - text.get_height()))

        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                elif event.type == KEYDOWN:
                    return True

    def highScoreBoard(self, hsm):
        title = self.largeFont.render("High Scores", True, self.menuColour).convert_alpha()
        text = self.font.render("Press any key to return to the main menu", True, self.menuColour).convert_alpha()
        
        highScores = []
        for highscore in hsm.highscores:
            highScores.append(self.largeFont.render(highscore[0] + ": " + str(highscore[1]), True, self.menuColour).convert_alpha())

        screen.fill(black)

        screen.blit(title, (WIDTH / 2 - title.get_width() / 2, 0))
        screen.blit(text, (WIDTH / 2 - text.get_width() / 2, HEIGHT - text.get_height()))

        y = sum(line.get_height() for line in highScores) / 2
        for line in highScores:
            screen.blit(line, (WIDTH / 2 - line.get_width() / 2, HEIGHT / 2 + line.get_height() / 2 - y))
            y -= line.get_height()

        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                elif event.type == KEYDOWN:
                    return True

    def newHighScore(self):
        title = self.largeFont.render("New High Score!", True, self.menuColour).convert_alpha()
        text = self.font.render("Enter your name", True, self.menuColour).convert_alpha()

        inputBox = playerInputBox(self.largeFont, self.menuColour, maxlen = 10)

        while True:
            clock.tick(10)
            screen.fill(black)

            screen.blit(title, (WIDTH / 2 - title.get_width() / 2, 0))
            screen.blit(text, (WIDTH / 2 - text.get_width() / 2, HEIGHT - text.get_height()))
            inputBox.draw()

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                elif event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        return inputBox.text
                    else:
                        inputBox.key_input(event.key, True)
                elif event.type == KEYUP:
                    inputBox.key_input(event.key, False)
            
class SoundManager():
    def __init__(self):
        self.sounds = {"bullet" : pygame.mixer.Sound("Sounds/bullet.wav"),
                       "laserstart" : pygame.mixer.Sound("Sounds/laserstart.wav"),
                       "laserstop" : pygame.mixer.Sound("Sounds/laserstop.wav")}

        self.music = {"menu" : "Sounds/Music/menu.wav",
                      "battle" : "Sounds/Music/invasion.wav"}
        self.isMuted = False

    def play(self, sound, loops = 0, fadems = 0):
        self.sounds[sound].play(loops, 0, fadems)

    def loadSong(self, song):
        pygame.mixer.music.load(self.music[song])
        if not self.isMuted:
            pygame.mixer.music.play(-1)

    def stop(self, sound):
        self.sounds[sound].stop()
    def stopSong(self, fadeout = 0):
        if not self.isMuted:
            if fadeout == 0:
                pygame.mixer.music.stop()
            else:
                pygame.mixer.music.fadeout(fadeout)

    def mute(self):
        if self.isMuted:
            for sound in self.sounds:
                self.sounds[sound].set_volume(1)
            self.isMuted = False

            pygame.mixer.music.unpause()
        else:
            for sound in self.sounds:
                 self.sounds[sound].set_volume(0)
            self.isMuted = True

            pygame.mixer.music.pause()

class HighScoreManager():
    def __init__(self):
        self.filename = "highscores.dat"
        self.numScores = 5
        
        if not os.path.isfile(self.filename):
            self.file = open(self.filename, "wb")
            self.scores = [100 for i in range(self.numScores)]
            self.names = ["A", "B", "C", "D", "E"]
            self.highscores = [(self.names[i], self.scores[i]) for i in range(self.numScores)]
            self.updateFile()
        else:
            file = open(self.filename, "rb")
            self.highscores = pickle.load(file)
            file.close()
            self.file = open(self.filename, "wb")

            self.names = [highscore[0] for highscore in self.highscores]
            self.scores = [highscore[1] for highscore in self.highscores]
            self.updateFile()

    def __del__(self):
        self.file.close()

    def checkScore(self, score):
        tempScores = self.scores[:] # Copy
        tempScores.append(score)
        tempScores.sort(reverse = True)
        tempScores = tempScores[:self.numScores]

        return (score in tempScores) # True if score is in tempScores

    def addScore(self, name, score):
        self.scores.append(score) #Add new score 
        self.scores.sort(reverse = True) #Sort
        self.names.insert(self.scores.index(score), name)
        self.names = self.names[:self.numScores] # Top 5
        self.scores = self.scores[:self.numScores]
        self.highscores = [(self.names[i], self.scores[i]) for i in range(self.numScores)]
        self.updateFile()

    def updateFile(self):
        self.file.close()
        self.file = open(self.filename, "wb")
        pickle.dump(self.highscores, self.file)

class HPBar():
    def __init__(self, maxHP, anchor):
        self.maxHP = maxHP
        self.currentHP = maxHP
        self.anchor = anchor

        self.greenbar = pygame.image.load("Images/HPbars/greenbar.png").convert() 
        self.redbar = pygame.image.load("Images/HPbars/redbar.png").convert() 

        if maxHP >= 100:
            self.greenbar = pygame.transform.scale(self.greenbar, (self.greenbar.get_width() * math.floor(maxHP / 100), self.redbar.get_height()))
            self.redbar = pygame.transform.scale(self.redbar, (self.redbar.get_width() * math.floor(maxHP / 100), self.redbar.get_height()))
        
        self.maxwidth = self.greenbar.get_width()
        self.x = self.anchor.x + self.anchor.img.get_width() / 2 - self.redbar.get_width() / 2
        self.y = self.anchor.y - self.redbar.get_height()
    def updateHP(self, currentHP):
        self.currentHP = currentHP
        if currentHP > 0:
            newwidth = math.floor(self.maxwidth * (self.currentHP / self.maxHP))
            self.greenbar = pygame.transform.scale(self.greenbar, (newwidth, self.greenbar.get_height()))
        else:
            self.greenbar.set_alpha(255)

    def draw(self):
        screen.blit(self.redbar, (self.x, self.y))
        screen.blit(self.greenbar, (self.x, self.y))

    def move(self):
        self.x = self.anchor.x + self.anchor.img.get_width() / 2 - self.redbar.get_width() / 2 
        self.y = self.anchor.y - self.redbar.get_height()

class Ship():
    def __init__(self, img = "Images/ship.png", HP = 400):
        self.img = pygame.image.load(img).convert_alpha()
        self.x = WIDTH / 2 - self.img.get_width() / 2
        self.y = self.img.get_height()
        self.midpoint = (self.x + self.img.get_width() / 2,
                         self.y + self.img.get_height() / 2) 
        self.maxHP = HP
        self.HP = HP
        self.HPBar = HPBar(HP, self)
        self.rect = pygame.Rect((self.x, self.y), self.img.get_size())
        self.score = 0
        self.scrap = 0
        self.speed = 1
        self.armour = 1
        self.laserPower = 1
        self.upgradeLevel = self.laserPower + self.armour + self.speed
        self.upgradeCost = 100
        self.laserOffset = 0.8
        self.laserDamage = self.laserPower * self.laserOffset

        #Movement boolean variables

        self.up = False
        self.down = False
        self.left = False
        self.right = False

        self.firing = False
        self.healing = False

        #   #   #   #   #

    def draw(self):
        screen.blit(self.img, (self.x, self.y))
        self.HPBar.draw()

    def regen(self):
        if self.healing and self.scrap > 0:
            self.HP += 1
            self.scrap -= 1

    def addScrap(self, amount):
        self.scrap += amount
        self.score += amount * 10

    def respondToKey(self, key, boolean):
        if key == K_w:
            self.up = boolean
        elif key == K_a:
            self.left = boolean
        elif key == K_s:
            self.down = boolean
        elif key == K_d:
            self.right = boolean

        self.spendScrap(key, boolean)

    def respondToMouse(self, boolean):
        self.firing = boolean

    def spendScrap(self, key, boolean):
        if boolean and key in (K_i, K_o, K_p):
            if key == K_i and self.scrap >= self.upgradeCost * self.laserPower and self.laserPower < 5:
                self.scrap -= self.upgradeCost * self.laserPower
                self.laserPower += 1
                self.laserDamage = self.laserPower * self.laserOffset
            elif key == K_o and self.scrap >= self.upgradeCost * self.armour and self.armour < 5:
                self.scrap -= self.upgradeCost * self.armour
                self.armour += 1
            elif key == K_p and self.scrap >= self.upgradeCost * self.speed and self.speed < 5:
                self.scrap -= self.upgradeCost * self.speed
                self.speed += 1

            self.upgradeLevel = self.laserPower + self.armour + self.speed
            
        if key == K_h:
            self.healing = boolean

    def remHP(self, loss):
        self.HP -= loss * (1 - self.armour / 10)
        self.HPBar.updateHP(self.HP)

    def update(self):
        if self.up or self.down or self.left or self.right:
            if self.up and not self.y < 0:
                self.y -= self.speed * 4
            elif self.down and not self.y > HEIGHT - self.img.get_height():
                self.y += self.speed * 4
            if self.left and not self.x < 0:
                self.x -= self.speed * 4
            elif self.right and not self.x > WIDTH - self.img.get_width():
                self.x += self.speed * 4

            self.midpoint = (self.x + self.img.get_width() / 2,
                             self.y + self.img.get_height() / 2)
            self.rect = pygame.Rect((self.x, self.y), self.img.get_size())

            self.HPBar.move()


        if self.firing:
            return self.fire()
            
        else:
            if self.HP < self.maxHP:
                self.regen()

    def fire(self):
        mousepos = pygame.mouse.get_pos()
        
        pygame.draw.line(screen, red, self.midpoint,
                         mousepos, 3 * self.laserPower)

        points = []
        numpoints = 100

        for i in range(1, numpoints):
            points.append((self.midpoint[0] + (mousepos[0] -
                           self.midpoint[0]) * (i/numpoints),
                           self.midpoint[1] + (mousepos[1] -
                           self.midpoint[1]) * (i/numpoints)))

        return points

class Bullet():
    def __init__(self, startpoint, target,
                 damage = 3, img = "Images/bullet.png"):
        self.img = pygame.image.load(img).convert()
        self.moves = 0
        self.x = startpoint[0]
        self.y = startpoint[1]
        self.target = target
        self.rect = ((self.x, self.y), self.img.get_size())
        self.damage = damage

    def draw(self):
        screen.blit(self.img, (self.x, self.y))

    def move(self):
        self.moves += 1
        self.x += (self.target[0] - self.x) * self.moves / 100
        self.y += (self.target[1] - self.y) * self.moves / 100
        self.rect = ((self.x, self.y), self.img.get_size())
        
class Unit():
    def __init__(self, HP):
        self.HP = HP
        self.HPBar = HPBar(HP, self)
        self.rect = pygame.Rect((self.x, self.y), self.img.get_size())
        self.delete = False

    def remHP(self, loss):
        self.HP -= loss
        self.HPBar.updateHP(self.HP)

    def draw(self):
        screen.blit(self.img, (self.x, self.y))

    
    def move(self):
        if self.x < 0 or self.x > WIDTH - self.img.get_width():
            self.speed = -(self.speed)

            if self.img == self.rightimg:
                self.img = self.leftimg
            else:
                self.img = self.rightimg
        
        self.x += self.speed
        self.rect = pygame.Rect((self.x, self.y), self.img.get_size())
        self.HPBar.move()
        self.midpoint = (self.x + self.img.get_width() / 2,
                         self.y + self.img.get_height() / 2)

    def fire(self, ship):
        return Bullet(self.midpoint, ship.midpoint, self.damage)


class Person(Unit):
    def __init__(self, img = "Images/person.png", HP = 5):
        self.img = pygame.image.load(img).convert_alpha()
        self.x = random.randint(0, WIDTH)
        self.y = HEIGHT - self.img.get_height()
        self.speed = random.randint(-5, 5)
        
        if self.speed == 0:
            self.moves = 0
        elif not isNegative(self.speed):
            self.moves = random.randint(1, math.floor(WIDTH / self.speed))
        else:
            self.moves = random.randint(1, math.floor(self.x / -self.speed))
            
        self.midpoint = (self.x + self.img.get_width() / 2,
                         self.y + self.img.get_height() / 2)
        self.shoots = False # Whether this mob can shoot
        self.scrapValue = 1

        Unit.__init__(self, HP)

    def move(self):
        if self.moves > 0:
            self.x += self.speed
            self.moves -= 1
        else:
            self.speed = -(self.speed)

            if self.speed == 0:
                self.moves = 0
            elif not isNegative(self.speed):
                self.moves = random.randint(1, math.floor(WIDTH / self.speed))
            else:
                self.moves = random.randint(1, math.floor(self.x / -self.speed))

        if self.x > WIDTH or self.x < -self.img.get_width():
            self.delete = True

        self.rect = pygame.Rect((self.x, self.y), self.img.get_size())
        self.HPBar.move()
        self.midpoint = (self.x + self.img.get_width() / 2,
                         self.y + self.img.get_height() / 2)

class Tank(Unit):
    def __init__(self, img = "Images/tank.png", HP = 200, speed = 10):
        self.rightimg = pygame.image.load(img).convert_alpha()
        self.leftimg = pygame.transform.flip(self.rightimg, True, False)
        self.img = self.leftimg
        self.x = random.randint(self.img.get_width(),
                                WIDTH - self.img.get_width())
        self.y = HEIGHT - self.img.get_height()
        self.speed = speed
        self.shoots = True # Whether this mob can shoot
        self.scrapValue = 10
        self.damage = 5

        Unit.__init__(self, HP)

class Helicopter(Unit):
    def __init__(self, img = "Images/helicopter.png", HP = 50, speed = 15):
        self.rightimg = pygame.image.load(img).convert_alpha()
        self.leftimg = pygame.transform.flip(self.rightimg, True, False)
        self.img = self.leftimg
        self.x = random.randint(self.img.get_width(),
                                WIDTH - self.img.get_width())
        self.y = random.randint(0, int(HEIGHT - HEIGHT / 4))
        self.speed = speed
        self.shoots = True # Whether this mob can shoot
        self.scrapValue = 7
        self.damage = 4

        Unit.__init__(self, HP)

class StealthPlane(Unit):
    def __init__(self, img = "Images/stealth plane.png", HP = 20):
        rightimg = pygame.image.load(img).convert_alpha()
        leftimg = pygame.transform.flip(rightimg, True, False)

        self.dir = random.choice(("left", "right"))
        self.speed = random.randint(20, 30)

        if self.dir == "left":
            self.img = leftimg
            self.speed = -(self.speed)
        else:
            self.img = rightimg

        self.y = random.randint(0, HEIGHT / 4)

        if self.dir == "left":
            self.x = WIDTH
        else:
            self.x = -self.img.get_width()

        self.scrapValue = deNegate(self.speed) * 5
        self.shoots = False
        Unit.__init__(self, HP)

    def move(self):
        self.x += self.speed
        self.rect = pygame.Rect((self.x, self.y), self.img.get_size())
        self.HPBar.move()

        if self.x > WIDTH and self.dir == "right":
            self.delete = True
        elif self.x < -self.img.get_width() and self.dir == "left":
            self.delete = True

class Soldier(Person):
    def __init__(self, img = "Images/soldier.png", HP = 8):
        Person.__init__(self, img, HP)
        self.shoots = True
        self.scrapValue = 2
        self.damage = 3

class Background():
    def __init__(self, img):
        self.img = pygame.image.load(img).convert()

        if self.img.get_size() != screen.get_size():
            self.img = pygame.transform.scale(self.img, screen.get_size())

    def draw(self):
        screen.blit(self.img, (0, 0))

def spawn(unitclass, units):
    units.append(unitclass())
    
def play(gm, sm, cursor):
    bg = Background("Images/bg.png")
    ship = Ship()
    numunits = 10
    baseSpawnRate = 80
    fireRate = 100

    units = []
    bullets = []
    
    while True:
        clock.tick(30)
        bg.draw()
        ship.draw()
        beam = ship.update()

        if random.randint(1, int((baseSpawnRate / ship.upgradeLevel) * len(units) + 1)) == 1:
            choice = random.randrange(1, 20)
            if choice in range(1, 6):
                spawn(Person, units)
            elif choice in range(6, 12):
                spawn(Soldier, units)
            elif choice == 13:
                spawn(StealthPlane, units)
            elif choice in range(13, 18):
                spawn(Helicopter, units)
            elif choice in range(19, 20):
                spawn(Tank, units)



        for unit in units:
            unit.draw()
            unit.move()
            unit.HPBar.draw()

            if beam:
                for point in beam:
                    if unit.rect.collidepoint(point):
                        unit.remHP(ship.laserDamage)
                        break

            if unit.shoots and random.randint(1, fireRate) == 1:
                sm.play("bullet")
                bullets.append(unit.fire(ship))

            if unit.HP <= 0:
                units.remove(unit)
                ship.addScrap(unit.scrapValue)

            if unit.delete:
                units.remove(unit)

        for bullet in bullets:
            bullet.move()
            bullet.draw()

            if ship.rect.colliderect(bullet.rect):
                 bullets.remove(bullet)
                 ship.remHP(bullet.damage)

            elif (bullet.x, bullet.y) == bullet.target:
                bullets.remove(bullet)

        if ship.HP <= 0:
            return ship.score

        gm.drawGUI(ship)
        cursor.draw()
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            elif event.type == KEYDOWN:
                ship.respondToKey(event.key, True)
            elif event.type == KEYUP:
                ship.respondToKey(event.key, False)
            elif event.type == MOUSEBUTTONDOWN:
                ship.respondToMouse(True)
                sm.play("laserstart")
            elif event.type == MOUSEBUTTONUP:
                ship.respondToMouse(False)
                sm.play("laserstop")

def main():
    cursor = Cursor()
    gm = GUIManager()
    sm = SoundManager()
    hsm = HighScoreManager()
    sm.loadSong("menu")

    while True:
        gm.menu(cursor, sm, hsm)
        sm.stopSong(1000)
        sm.loadSong("battle")
        score = play(gm, sm, cursor)
        sm.stopSong(2000)
        
        sm.loadSong("menu")
        if hsm.checkScore(score):
            hsm.addScore(gm.newHighScore(), score)
        else:
            gm.lose()

if __name__ == "__main__":
    main()
