import pygame
from pygame.locals import *
import random


class Ball():
    def __init__(self, window, windowWidth, windowHeight):
        self.window = window
        self.windowWidth = windowWidth
        self.windowHeight = windowHeight
        self.image = pygame.image.load('images/ball.png')

        ballRect = self.image.get_rect()
        self.width = ballRect.width
        self.height = ballRect.height
        self.maxWidth = windowWidth - self.width
        self.maxHeight = windowHeight - self.height

        self.x = random.randrange(0, self.maxWidth)
        self.y = random.randrange(0, self.maxHeight)

        speedList = [-4, -3, -2, -1, 1, 2, 3, 4]
        self.xSpeed = random.choice(speedList)
        self.ySpeed = random.choice(speedList)

    def update(self):
        if (self.x < 0) or (self.x >= self.maxWidth):
            self.xSpeed = -self.xSpeed

        if (self.y < 0) or (self.y >= self.maxHeight):
            self.ySpeed = -self.ySpeed

        self.x = self.x + self.xSpeed
        self.y = self.y + self.ySpeed

    def draw(self):
        self.window.blit(self.image, (self.x, self.y))
