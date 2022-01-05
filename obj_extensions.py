from os import X_OK
import pygame
pygame.init()

WIDTH, HEIGHT = 750, 750

class Gold_boss_arm:
    def __init__(self, x, y, img):
        self.x = x[0] - x[1]
        self.y = y[0] - y[1]
        self.x_diff = x[1]
        self.y_diff = y[1]
        self.img = img
        
    def follow(self, x, y):
        self.x = x + self.x_diff
        self.y = y + self.y_diff
    
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))