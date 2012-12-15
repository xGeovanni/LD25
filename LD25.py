# Title
# Description
# Bobby Clarke

#Imports
import pygame
import sys
import random
import math
from pygame.locals import *
pygame.init()

clock = pygame.time.Clock()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("LD25")
pygame.mouse.set_visible(False)

class Cursor():
    def __init__(self, img = "Images/cursor.png"):
        self.img = pygame.image.load(img)

    def draw(self):
        screen.blit(self.img, (pygame.mouse.get_pos()[0] -
                               self.img.get_width() / 2,
                               pygame.mouse.get_pos()[1] -
                               self.img.get_height() / 2))

class HPBar():
    def __init__(self, maxHP, x, y):
        self.maxHP = maxHP
        self.currentHP = maxHP

        self.greenbar = pygame.image.load("Images/HPbars/greenbar.png").convert() 
        self.redbar = pygame.image.load("Images/HPbars/redbar.png").convert() 

        if maxHP >= 100:
            self.greenbar = pygame.transform.scale(self.greenbar, (self.greenbar.get_width() * math.floor(maxHP / 100), self.redbar.get_height()))
            self.redbar = pygame.transform.scale(self.redbar, (self.redbar.get_width() * math.floor(maxHP / 100), self.redbar.get_height()))
        
        self.maxwidth = self.greenbar.get_width()
        self.x = x
        self.y = y
    def updateHP(self, currentHP):
        self.currentHP = currentHP
        newwidth = math.floor(self.maxwidth * (self.currentHP / self.maxHP))
        self.greenbar = pygame.transform.scale(self.greenbar, (newwidth, self.greenbar.get_height()))

    def draw(self):
        screen.blit(self.redbar, (self.x, self.y))
        screen.blit(self.greenbar, (self.x, self.y))

    def move(self, point):
        self.x = point[0]
        self.y = point[1]

class Ship():
    def __init__(self, speed = 8, damage = 1,
                 img = "Images/ship.png", HP = 500):
        self.img = pygame.image.load(img).convert_alpha()
        self.x = WIDTH / 2 - self.img.get_width() / 2
        self.y = self.img.get_height()
        self.speed = speed
        self.damage = damage
        self.maxHP = HP
        self.HP = HP
        self.HPBar = HPBar(HP, self.x, self.y - 16)
        self.rect = pygame.Rect((self.x, self.y), self.img.get_size())

        self.midpoint = (self.x + self.img.get_width() / 2,
                         self.y + self.img.get_height() / 2)        

        #Movement boolean variables

        self.up = False
        self.down = False
        self.left = False
        self.right = False

        self.firing = False

        #   #   #   #   #

    def draw(self):
        screen.blit(self.img, (self.x, self.y))
        self.HPBar.draw()

    def respondToKey(self, key, boolean):
        if key == K_UP:
            self.up = boolean
        elif key == K_DOWN:
            self.down = boolean
        elif key == K_LEFT:
            self.left = boolean
        elif key == K_RIGHT:
            self.right = boolean

    def respondToMouse(self, boolean):
        self.firing = boolean

    def remHP(self, loss):
        self.HP -= loss
        self.HPBar.updateHP(self.HP)

    def update(self):
        if self.up or self.down or self.left or self.right:
            if self.up and not self.y < 0:
                self.y -= self.speed
            elif self.down and not self.y > HEIGHT - self.img.get_height():
                self.y += self.speed   
            if self.left and not self.x < 0:
                self.x -= self.speed
            elif self.right and not self.y > WIDTH - self.img.get_width():
                self.x += self.speed

            self.midpoint = (self.x + self.img.get_width() / 2,
                             self.y + self.img.get_height() / 2)
            self.rect = pygame.Rect((self.x, self.y), self.img.get_size())

            HPBar.move(self.HPBar, (self.x, self.y - 16))


        if self.firing:
            return self.fire()
        else:
            if self.HP < self.maxHP:
                self.remHP(-1 / 50)

    def fire(self):
        mousepos = pygame.mouse.get_pos()
        
        pygame.draw.line(screen, (255, 0, 0), self.midpoint,
                         mousepos, 5)

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
        
class Target():
    def __init__(self, HP):
        self.HP = HP
        self.HPBar = HPBar(HP, self.x, self.y - 16)

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
        self.HPBar.move((self.x, self.y - 16))
        self.midpoint = (self.x + self.img.get_width() / 2,
                         self.y + self.img.get_height() / 2)   


class Person(Target):
    def __init__(self, img = "Images/person.png", HP = 5):
        self.img = pygame.image.load(img)
        self.x = random.randint(0, WIDTH)
        self.y = HEIGHT - self.img.get_height()
        self.rect = pygame.Rect((self.x, self.y), self.img.get_size())
        self.speed = random.randint(-5, 5)
        self.moves = random.randint(1, 3)
        self.shoots = False # Whether this mob can shoot

        Target.__init__(self, HP)

    def move(self):
        if self.moves > 0:
            self.x += self.speed
            self.moves -= 1
        else:
            self.speed = -(self.speed)
            self.moves = random.randint(1, 20)

        self.rect = pygame.Rect((self.x, self.y), self.img.get_size())
        self.HPBar.move((self.x, self.y - 16))

class Tank(Target):
    def __init__(self, img = "Images/tank.png", HP = 200, speed = 10):
        self.rightimg = pygame.image.load(img).convert_alpha()
        self.leftimg = pygame.transform.flip(self.rightimg, True, False)
        self.img = self.leftimg
        self.x = random.randint(self.img.get_width(),
                                WIDTH - self.img.get_width())
        self.y = HEIGHT - self.img.get_height()
        self.rect = pygame.Rect((self.x, self.y), self.img.get_size())
        self.speed = speed
        self.shoots = True # Whether this mob can shoot

        Target.__init__(self, HP)

    def fire(self, ship):
        return Bullet(self.midpoint, ship.midpoint)

class Helicopter(Target):
    def __init__(self, img = "Images/helicopter.png", HP = 50, speed = 15):
        self.rightimg = pygame.image.load(img).convert_alpha()
        self.leftimg = pygame.transform.flip(self.rightimg, True, False)
        self.img = self.leftimg
        self.x = random.randint(self.img.get_width(),
                                WIDTH - self.img.get_width())
        self.y = random.randint(0, int(HEIGHT - HEIGHT / 4))
        self.rect = pygame.Rect((self.x, self.y), self.img.get_size())
        self.speed = speed
        self.shoots = True # Whether this mob can shoot

        Target.__init__(self, HP)

    def fire(self, ship):
        return Bullet(self.midpoint, ship.midpoint)

class Background():
    def __init__(self, img):
        self.img = pygame.image.load(img)

        if self.img.get_size() != screen.get_size():
            self.img = pygame.transform.scale(self.img, screen.get_size())

    def draw(self):
        screen.blit(self.img, (0, 0))

def spawn(targetclass, targets):
    targets.append(targetclass())
    
def main():
    bg = Background("Images/bg.png")
    cursor = Cursor()
    
    ship = Ship()
    numtargets = 10

    targets = [Person() for i in range(numtargets)]
    spawn(Tank, targets)
    spawn(Helicopter, targets)

    bullets = []

    targetClasses = (Person, Tank, Helicopter)
    
    while True:
        clock.tick(30)
        bg.draw()
        ship.draw()
        beam = ship.update()

        if random.randint(1, 300) == 1:
            spawn(random.choice(targetClasses), targets)

        for target in targets:
            target.draw()
            target.move()
            target.HPBar.draw()

            if beam:
                for point in beam:
                    if target.rect.collidepoint(point):
                        target.remHP(ship.damage)
                        break

            if target.shoots and random.randint(1, 100) == 1:
                bullets.append(target.fire(ship))

            if target.HP <= 0:
                targets.remove(target)

        for bullet in bullets:
            bullet.move()
            bullet.draw()

            if ship.rect.colliderect(bullet.rect):
                 bullets.remove(bullet)
                 ship.remHP(bullet.damage)

            elif (bullet.x, bullet.y) == bullet.target:
                bullets.remove(bullet)

            
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
            elif event.type == MOUSEBUTTONUP:
                ship.respondToMouse(False)


if __name__ == "__main__":
    main()


       






