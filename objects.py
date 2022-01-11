import pygame
import random
import os
pygame.init()

WIDTH, HEIGHT = 750, 750

# Loads in enemies and player
red_space_ship = pygame.image.load("assets/pixel_red_ship.png")
blue_space_ship = pygame.image.load("assets/pixel_blue_ship.png")
green_space_ship = pygame.image.load("assets/pixel_green_ship.png")

yellow_space_ship = pygame.image.load("assets/pixel_player_ship.png")
    
# Loads in animations
green_ship_death = []
red_ship_death = []
blue_ship_death = []
for file in os.listdir(os.getcwd()+"/assets/green_ship_death"):
    green_ship_death.append(pygame.image.load(f"assets/green_ship_death/{file}"))
for file in os.listdir(os.getcwd()+"/assets/red_ship_death"):
    red_ship_death.append(pygame.image.load(f"assets/red_ship_death/{file}"))
for file in os.listdir(os.getcwd()+"/assets/blue_ship_death"):
    blue_ship_death.append(pygame.image.load(f"assets/blue_ship_death/{file}"))

# Loads in lasers
red_laser = pygame.image.load("assets/pixel_red_laser.png")
green_laser = pygame.image.load("assets/pixel_green_laser.png")
blue_laser = pygame.image.load("assets/pixel_blue_laser.png")
yellow_laser = pygame.image.load("assets/pixel_yellow_laser.png")

green_boss_laser = pygame.image.load("assets/pixel_green_boss_laser.png")

# Loads in bosses
green_boss = pygame.image.load("assets/pixel_green_boss.png")
red_boss = pygame.image.load("assets/pixel_red_boss.png")

# Loads in audio
player_laser_sound = pygame.mixer.Sound("audio/player_laser_sound.wav")
enemy_laser_sound = pygame.mixer.Sound("audio/enemy_laser_sound.wav")
boss_laser_sound = pygame.mixer.Sound("audio/boss_laser_sound.wav")

player_laser_sound.set_volume(.8)
boss_laser_sound.set_volume(.2)


# Objects used in game
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

        self.curr_frame = 0
        self.animate = False
        self.delete = False
        self.cool_down_counter = 0
    
    def off_screen(self, height):
        return self.y > height or self.y < - self.img.get_height()
    
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        if self.animate == True:
            self.animate_death()
    
    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()
    
    def off_screen(self):
        return self.y > 730 or self.y < - self.ship_img.get_height()
    
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
    
    def animate_death(self):
        self.ship_img = self.frames[int(self.curr_frame)]
        if self.curr_frame < len(self.frames)-1:
            self.curr_frame += .3
        else:
            self.animate = False
            self.delete = True
            
                
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
                        enemy.animate = True
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
    shoot = True

    COLOR_MAP = {
        "red": (red_space_ship, red_laser, red_ship_death),
        "green": (green_space_ship, green_laser, green_ship_death),
        "blue": (blue_space_ship, blue_laser, blue_ship_death)
    }
    
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.color = color
        self.ship_img, self.laser_img, self.frames = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.shift_counter = random.randrange(0,40)
        self.direction = True
    
    def move(self, velocity):
        self.y += velocity
    
        if self.shift_counter % 40 == 0 or self.x + Enemy.shift > WIDTH - self.get_width() - 10 or self.x - Enemy.shift < 10:
            self.direction = not(self.direction)
            
        if self.direction == True:
            self.shift_counter += .5
            self.x += Enemy.shift
        else:
            self.shift_counter -= .5
            self.x -= Enemy.shift
            
    def shoot(self):
        if Enemy.shoot:
            if not(self.off_screen()):
                diff_map = {
                    "red": 60,
                    "green": 50,
                    "blue": 50
                }
                enemy_laser_sound.play()
                loc1 = self.x + self.get_width()/2 - 50
                loc2 = self.y + self.get_height() - diff_map[self.color]
                laser = Laser(loc1, loc2, self.laser_img, self.color)
                return laser

class Boss(Ship):
    shift = 1.5
    max_cooldown = 12
    damage = False
    
    COLOR_MAP = {
        "red": (red_boss, red_laser),
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
        self.direction = True
        self.shoot_now = False
    
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        self.healthbar(window)
        
    def move(self, velocity):
        if self.y < 40:
            self.y += velocity
        else:
            self.shoot_now = True
            Boss.damage = True
            
        if self.color == "green":
            if self.x + self.shift > WIDTH - self.get_width() - 100 or self.x - self.shift < 100:
                self.direction = not(self.direction)
        elif self.color == "red":
            if self.x + self.shift > WIDTH - self.get_width() - 70 or self.x - self.shift < 70:
                self.direction = not(self.direction)
            
        if self.direction == True:
            self.x += self.shift
        else:
            self.x -= self.shift
    
    def shoot(self):
        if self.color == "green":
            if self.cool_down_counter == 0 and self.shoot_now:
                boss_laser_sound.play()
                loc_x = self.x + self.get_width()/2 - 50
                loc_y = self.y + self.get_height() - 20
                laser = Laser(loc_x, loc_y, self.laser_img, self.color)
                self.cool_down_counter += 1
                return [laser]
            
        if self.color == "red":
            if self.cool_down_counter == 0 and self.shoot_now:
                boss_laser_sound.play()
                
                loc_y = self.y + self.get_height() - 50
                loc_y1 = self.y + self.get_height() - 60
                loc_x1 = self.x + self.get_width()/2 + 20
                loc_x2 = self.x + self.get_width()/2 - 50
                loc_x3 = self.x + self.get_width()/2 - 120
                
                laser1 = Laser(loc_x1, loc_y, self.laser_img, self.color)
                laser2 = Laser(loc_x2, loc_y1, self.laser_img, self.color)
                laser3 = Laser(loc_x3, loc_y, self.laser_img, self.color)
                self.cool_down_counter += 1
                return (laser1, laser2, laser3)
    
    def healthbar(self, window):
        pygame.draw.rect(window, (240,90,0), (self.x, self.y - 10, self.ship_img.get_width(), 15))
        pygame.draw.rect(window, (40,255,0), (self.x, self.y - 10, self.ship_img.get_width() * (self.health/self.max_health), 15))
    
# GUI objects
class Button:
    def __init__(self, pos, color, label):
        self.color = color
        self.rect = pygame.Rect(pos[0], pos[1], label.get_width() + 20, label.get_height() + 20)
        self.label = label
    
    def draw(self, window):
        back_color = self.shade_color(self.color, 30)
        pygame.draw.rect(window, back_color, (self.rect[0], self.rect[1], self.rect[2] + 10, self.rect[3] + 10))
        if self.hover():
            pygame.draw.rect(window, self.shade_color(self.color, 10), self.rect)
        else:
            pygame.draw.rect(window, self.color, self.rect)
        window.blit(self.label, (self.rect[0] + 10, self.rect[1] + 10))
        
    def click(self, event):
        pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0] == 1:
                if self.rect.collidepoint(pos):
                    return True

    def hover(self):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            return True
    
    def shade_color(self, color, shade):
        nc = [0, 0, 0]
        nc[0] = color[0] - shade
        nc[1] = color[1] - shade
        nc[2] = color[2] - shade
        return tuple(nc)

class Display():
    counter = 0

    def __init__(self, x, y, label):
        self.x = x
        self.y = y
        self.label = label
        self.slide_time = 0

    def draw(self, window):
        window.blit(self.label, (self.x, self.y))

    def slide_draw(self, window, velocity, time):
        if self.x < WIDTH/2 - self.label.get_width()/2:
            self.slide_time += 1
            self.x += velocity  
            window.blit(self.label, (self.x, self.y))

        else:
            if Display.counter > time - self.slide_time*2.5:
                    self.x += velocity
                    window.blit(self.label, (self.x, self.y))
            else:
                window.blit(self.label, (self.x, self.y))
                Display.counter += 1

    def set_origin(self):
        Display.counter = 0
        self.x = -self.label.get_width()
        self.slide_time = 0

# Assistive functions
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (int(offset_x), int(offset_y))) != None

