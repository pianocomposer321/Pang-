import pygame, sys
from pygame.locals import *
from random import *
from math import sqrt
import time

pygame.font.init()
font = pygame.font.Font("freesansbold.ttf", 12)
ywfont = pygame.font.Font("freesansbold.ttf", 36) # "You win" font

class Paddle(pygame.sprite.Sprite):
    _instances = list()

    def __init__(self, name):
        pygame.sprite.Sprite.__init__(self)
        self.width, self.height = 10, 50
        self.name = name
        
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.points = 0
        self.pointText = f"{self.name}: {self.points}"
        self.text = font.render(self.pointText, True, (255, 255, 255))
        self.textRect = self.text.get_rect()
        self.textRect = self.textRect.move(0, 0 if self.name == "You" else self.textRect.height)
        self._instances.append(self)
    
    @classmethod
    def getInstances(self):
        return self._instances

    def addPoints(self):
        self.points += 1
        if self.points == 3:
            pygame.display.get_surface().fill((0, 0, 0))
            self.text = ywfont.render("You Win!" if Paddle.getInstances()[0] == self else "You Lose!", True, (0, 255, 0))
            self.textRect = self.text.get_rect()
            self.textRect = self.textRect.move(pygame.display.get_surface().get_rect().width/2 - self.textRect.width/2, pygame.display.get_surface().get_rect().height/2 - self.textRect.height/2)
            return
        self.pointText = f"{self.name}: {self.points}"
        self.text = font.render(self.pointText, True, (255, 255, 255))
        self.textRect = self.text.get_rect()
        self.textRect = self.textRect.move(0, 0 if self.name == "You" else self.textRect.height)

        time.sleep(1)
    
    def goto(self, *pos):
        self.rect = self.rect.move(pos[0]-self.rect.x, pos[1]-self.rect.y)

class playerPaddle(Paddle):
    def __init__(self, name):
        Paddle.__init__(self, name)
        self.goto(10, pygame.display.get_surface().get_height()/2 - self.height/2)
        
    def reset(self):
        self.lives = 3

class compPaddle(Paddle):
    def __init__(self, name):
        Paddle.__init__(self, name)
        self.goto(pygame.display.get_surface().get_width() - 20, pygame.display.get_surface().get_height()/2 - self.rect.height/2)
    
    def move(self, direct):
        if direct == "up":
            self.rect = self.rect.move([0, -2])
        elif direct == "down":
            self.rect = self.rect.move([0, 2])
        else:
            print("Error: direction must be up or down!")
    
    def update(self):
        if Ball.getInstances()[0].rect.bottom > self.rect.center[1]:
            self.move("down")
        elif Ball.getInstances()[0].rect.top < self.rect.center[1]:
            self.move("up")

class Ball(pygame.sprite.Sprite):
    _instances = list()

    def __init__(self, paddlegroup):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("ball.png")
        self.rect = self.image.get_rect()
        self.speed = 4
        self.resetdir()
        self.reset()
        self.paddles = paddlegroup

        self._instances.append(self)
    
    def resetdir(self):
        x = 0
        while x == 0:
            x = randint(-3, 3)
        y = self.findx(x, self.speed)
        if randint(0, 1) == 0:  y = -y
        self.direction = [x, y]
    
    def reset(self):
        self.goto(pygame.display.get_surface().get_width()/2, \
                  pygame.display.get_surface().get_height()/2)
        self.resetdir()
    
    @classmethod
    def getInstances(self):
        return self._instances

    def goto(self, *pos):
        self.rect = self.rect.move(pos[0]-self.rect.x, pos[1]-self.rect.y)

    def findx(self, y, dis):
        y = y % dis
        x = sqrt(dis**2 - y**2)
        return x

    def checkForCollisions(self, index):
        if pygame.sprite.collide_rect(self, Paddle.getInstances()[index]):
            
            if index == 0:
                self.rect.x = Paddle.getInstances()[index].rect.right
            elif index == 1:
                self.rect.right = Paddle.getInstances()[index].rect.left - 1

            self.direction[0] = -self.direction[0]

            difference = self.rect.center[1] - \
                Paddle.getInstances()[index].rect.center[1]
            if index == 0:
                self.direction[1] -= difference/30
            self.direction[1] = self.direction[1] % self.speed
            self.direction[0] = self.findx(self.direction[1], self.speed)
            if self.direction[0] < 1:
                self.resetdir()
            if index == 1:
                self.direction[0] = -self.direction[0]
            self.speed += 0.1

    def update(self):
        self.rect = self.rect.move(self.direction)
        self.checkForCollisions(0)
        self.checkForCollisions(1)

        if self.rect.top < 0: # if it's too high
            self.rect.top = 0
            self.direction[1] = -self.direction[1]
        elif self.rect.bottom > pygame.display.get_surface().get_height(): # if it's too low
            self.rect.bottom = pygame.display.get_surface().get_height()
            self.direction[1] = -self.direction[1]
        
        if self.rect.right > pygame.display.get_surface().get_width(): # if it's to far to the right
            self.reset()
            Paddle.getInstances()[0].addPoints()

        elif self.rect.left < 0: # if it's too far to the left
            self.reset()
            Paddle.getInstances()[1].addPoints()

import pygame, sys, os
from pygame.locals import *
import time

def setup():
    os.environ['SDL_VIDEO_WINDOW_POS'] = "300,30"
    pygame.init()
    global font, scr, player, comp, ball, sprites, paddles, clock
    scr = pygame.display.set_mode([608, 720])
    pygame.display.set_caption("Pang!")
    clock = pygame.time.Clock()
    player = playerPaddle("You")
    comp = compPaddle("Computer")
    paddles = pygame.sprite.Group(player, comp)
    ball = Ball(paddles)
    sprites = pygame.sprite.Group(player, comp, ball)

def events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEMOTION:
            player.goto(player.rect.x, event.pos[1] - player.rect.height/2)

def updates():
    sprites.update()

def render():
    scr.fill((0, 0, 0))
    scr.blit(player.text, player.textRect)
    scr.blit(comp.text, comp.textRect)
    if player.points == 3 or comp.points == 3:
        pygame.display.flip()
        time.sleep(1)
        sys.exit()
    scr.blit(player.image, player.rect)
    scr.blit(comp.image, comp.rect)
    scr.blit(ball.image, ball.rect)

    pygame.display.flip()

setup()

while True:
    clock.tick(100)

    events()
    updates()
    render()