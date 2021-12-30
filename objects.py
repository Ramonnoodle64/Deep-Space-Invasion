import pygame
import os
import random

WIDTH, HEIGHT = 750, 750

# Loads in spaceship assests
red_space_ship = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
blue_space_ship = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
green_space_ship = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))

yellow_space_ship = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Loads in laser and backgroung assets
red_laser = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
green_laser = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
blue_laser = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
yellow_laser = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))


# All objects used
class Laser:
    def __init__(self, x, y, img, color):
        self.x = x
        self.y = y
        self.img = img
        self.color = color
        self.mask = pygame.mask.from_surface(self.img)
        
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
        
    def move(self, velocity):
        self.y += velocity
    
    def off_screen(self, height):
        return self.y > height or self.y < - self.img.get_height()
    
    def collision(self, object):
        return collide(object, self)


class Ship:
    max_cooldown = 25
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.color = None
        
        self.cool_down_counter = 0
    
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
    
    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()
    
    def cooldown(self):
        if self.cool_down_counter >= Player.max_cooldown:
            self.cool_down_counter = 0
        if self.cool_down_counter > 0:
            self.cool_down_counter += 1
            
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img, self.color)
            self.lasers.append(laser)
            self.cool_down_counter = 1
    
                
class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = yellow_space_ship
        self.laser_img = yellow_laser
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.lasers = []
        self.color = "yellow"
    
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        self.healthbar(window)
        for laser in self.lasers:
            laser.draw(window)
            
    def move_lasers(self, velocity, objects):
        self.cooldown()
        for laser in self.lasers:
            laser.move(velocity)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for object in objects:
                    if laser.collision(object):
                        objects.remove(object)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def healthbar(self, window):
        pygame.draw.rect(window, (240,90,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (40,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    shift = 0
    
    COLOR_MAP = {
        "red": ("red", red_space_ship, red_laser),
        "green": ("green", green_space_ship, green_laser),
        "blue": ("blue", blue_space_ship, blue_laser)
    }
    
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.color, self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.counter = 0
        self.direction = "right"
    
    def move(self, velocity):
        self.y += velocity
    
        if self.counter % 20 == 0 or self.x + Enemy.shift > WIDTH - self.get_width() - 10 or self.x - Enemy.shift < 10:
            self.direction = invert(self.direction)
            
        if self.direction == "right":
            self.counter += .5
            self.x += Enemy.shift
        else:
            self.counter -= .5
            self.x -= Enemy.shift
            
    def shoot(self):
        laser = Laser(self.x - 20, self.y, self.laser_img, self.color)
        return laser



# Assistive functions
def invert(value):
    if value == "right":
        return "left"
    else:
        return "right"

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (int(offset_x), int(offset_y))) != None