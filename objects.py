import pygame
import os
import random
pygame.init()

WIDTH, HEIGHT = 750, 750

# Loads in enemies and player
red_space_ship = pygame.image.load("assets/pixel_red_ship.png")
blue_space_ship = pygame.image.load("assets/pixel_blue_ship_s.png")
green_space_ship = pygame.image.load("assets/pixel_green_ship.png")

yellow_space_ship = pygame.image.load("assets/pixel_player_ship.png")
    
# Loads in lasers
red_laser = pygame.image.load("assets/pixel_red_laser.png")
green_laser = pygame.image.load("assets/pixel_green_laser.png")
blue_laser = pygame.image.load("assets/pixel_blue_laser.png")
yellow_laser = pygame.image.load("assets/pixel_yellow_laser.png")

green_boss_laser = pygame.image.load("assets/pixel_green_boss_laser.png")

# Loads in bosses
green_boss = pygame.image.load("assets/pixel_green_boss.png")

# Loads in audio
player_laser_sound = pygame.mixer.Sound("audio/player_laser_sound.wav")
player_laser_sound.set_volume(.7)

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
        if self.cool_down_counter >= self.max_cooldown:
            self.cool_down_counter = 0
        if self.cool_down_counter > 0:
            self.cool_down_counter += 1
            
    def shoot(self):
        if self.cool_down_counter == 0:
            player_laser_sound.play()
            laser = Laser(self.x, self.y, self.laser_img, self.color)
            self.lasers.append(laser)
            self.cool_down_counter = 1
    
                
class Player(Ship):
    damage = True
    
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
            
    def move_lasers(self, velocity, enemies, bosses):
        self.cooldown()
        for laser in self.lasers:
            laser.move(velocity)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for enemy in enemies:
                    if laser.collision(enemy):
                        enemies.remove(enemy)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                            
                for boss in bosses:
                    if laser.collision(boss):
                        if Boss.damage == True:
                            boss.health -= 10
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def healthbar(self, window):
        pygame.draw.rect(window, (240,90,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (40,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    shift = 0
    
    COLOR_MAP = {
        "red": (red_space_ship, red_laser),
        "green": (green_space_ship, green_laser),
        "blue": (blue_space_ship, blue_laser)
    }
    
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.color = color
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.counter = random.randrange(0,40)
        self.direction = "right"
    
    def move(self, velocity):
        self.y += velocity
    
        if self.counter % 40 == 0 or self.x + Enemy.shift > WIDTH - self.get_width() - 10 or self.x - Enemy.shift < 10:
            self.direction = invert(self.direction)
            
        if self.direction == "right":
            self.counter += .5
            self.x += Enemy.shift
        else:
            self.counter -= .5
            self.x -= Enemy.shift
            
    def shoot(self):
        diff_map = {
            "red": 60,
            "green": 50,
            "blue": 50
        }
        loc1 = self.x + self.get_width()/2 - 50
        loc2 = self.y + self.get_height() - diff_map[self.color]
        laser = Laser(loc1, loc2, self.laser_img, self.color)
        return laser

class Boss(Ship):
    shift = 1.3
    max_cooldown = 12
    damage = False
    
    COLOR_MAP = {
        "red": ("", red_laser),
        "green": (green_boss, green_boss_laser),
        "blue": ("", blue_laser)
    }
    
    def __init__(self, x, y, color, health=200):
        super().__init__(x, y, health)
        self.color = color
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.counter = 0
        self.direction = "right"
        self.shoot_now = False
    
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        self.healthbar(window)
        
    def move(self, velocity):
        if self.y < 40:
            self.y += velocity
        else:
            self.shoot_now = True
            Enemy.damage = True
            
        if self.x + self.shift > WIDTH - self.get_width() - 130 or self.x - self.shift < 130:
            self.direction = invert(self.direction)
            
        if self.direction == "right":
            self.counter += .5
            self.x += self.shift
        else:
            self.counter -= .5
            self.x -= self.shift
    
    def shoot(self):
        if self.color == "green":
            if self.cool_down_counter == 0 and self.shoot_now:
                loc1 = self.x + self.get_width()/2 - 50
                loc2 = self.y + self.get_height() - 20
                laser = Laser(loc1, loc2, self.laser_img, self.color)
                self.cool_down_counter += 1
                return laser
    
    def healthbar(self, window):
        if self.color == "green":
            pygame.draw.rect(window, (240,90,0), (self.x, self.y - 10, self.ship_img.get_width(), 15))
            pygame.draw.rect(window, (40,255,0), (self.x, self.y - 10, self.ship_img.get_width() * (self.health/self.max_health), 15))
    

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