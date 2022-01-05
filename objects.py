import pygame
import random
from obj_extensions import Gold_boss_arm
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
red_beam = red_laser = pygame.image.load("assets/pixel_red_beam.png")

# Loads in micelaneous entitys
fire_ball = pygame.image.load("assets/pixel_fire_ball.png")
goldboss_left_arm = pygame.image.load("assets/gold_boss_ext1.png")
goldboss_right_arm = pygame.image.load("assets/gold_boss_ext2.png")

# Loads in bosses
green_boss = pygame.image.load("assets/pixel_green_boss.png")
red_boss = pygame.image.load("assets/pixel_red_boss.png")
gold_boss = pygame.image.load("assets/pixel_gold_boss.png")

# Loads in audio
player_laser_sound = pygame.mixer.Sound("audio/player_laser_sound.wav")
enemy_laser_sound = pygame.mixer.Sound("audio/enemy_laser_sound.wav")
boss_laser_sound = pygame.mixer.Sound("audio/boss_laser_sound.wav")
player_impact_sound = pygame.mixer.Sound("audio/player_impact_sound.wav")

player_laser_sound.set_volume(.8)
boss_laser_sound.set_volume(.2)


# Objects used in game
class Laser:
    def __init__(self, x, y, img, color, velocity):
        self.x = x
        self.y = y
        self.img = img
        self.color = color
        self.mask = pygame.mask.from_surface(self.img)
        self.velocity = velocity
        
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
        
    def move(self):
        self.y += self.velocity
    
    def off_screen(self, height):
        return self.y > height or self.y < - self.img.get_height()
    
    def collision(self, object):
        return collide(object, self)

class Beam(Laser):
    def __init__(self, x, y, img, velocity):
        self.img = img
        self.velocity = velocity
        self.x = x[0] + x[1]
        self.y = y[0] + x[1]
        self.x_diff = x[1]
        self.y_diff = y[1]
        
    def move(self, x):
        self.x = x + self.x_diff
        self.y += self.velocity

class Ship:
    max_cooldown = 25
    max_cooldown2 = 120
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.color = None
        
        self.cool_down_counter = 0
        self.cool_down_counter2 = 0
    
    def off_screen(self, height):
        return self.y > height or self.y < - self.img.get_height()
    
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
    
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
            
    def cooldown2(self):
        if self.cool_down_counter2 >= self.max_cooldown2:
            self.cool_down_counter2 = 0
        if self.cool_down_counter2 > 0:
            self.cool_down_counter2 += 1
            
    def shoot(self, vel):
        if self.cool_down_counter == 0:
            player_laser_sound.play()
            laser = Laser(self.x, self.y, self.laser_img, self.color, vel)
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
            
    def move_lasers(self, enemies, bosses):
        self.cooldown()
        for laser in self.lasers:
            laser.move()
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
        self.direction = True
    
    def move(self, velocity):
        self.y += velocity
    
        if self.counter % 40 == 0 or self.x + Enemy.shift > WIDTH - self.get_width() - 10 or self.x - Enemy.shift < 10:
            self.direction = not(self.direction)
            
        if self.direction == True:
            self.counter += .5
            self.x += Enemy.shift
        else:
            self.counter -= .5
            self.x -= Enemy.shift
            
    def shoot(self, vel):
        if not(self.off_screen()):
            diff_map = {
                "red": 60,
                "green": 50,
                "blue": 50
            }
            enemy_laser_sound.play()
            loc1 = self.x + self.get_width()/2 - 50
            loc2 = self.y + self.get_height() - diff_map[self.color]
            laser = Laser(loc1, loc2, self.laser_img, self.color, vel)
            return laser

class Boss(Ship):
    shift = 1.5
    max_cooldown = 12
    damage = False
    
    COLOR_MAP = {
        "red": (red_boss, red_laser),
        "green": (green_boss, green_boss_laser),
        "gold": (gold_boss, yellow_laser)
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
        self.extentions = []
        if self.color == "gold":
            ext1 = Gold_boss_arm((self.x, -40), (self.y, -10), goldboss_left_arm)
            ext2 = Gold_boss_arm((self.x, 370), (self.y, -10), goldboss_right_arm)
            self.extentions.extend([ext1, ext2])
        
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for ext in self.extentions:
            ext.draw(window)
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
        elif self.color == "gold":
            if self.x + self.shift > WIDTH - self.get_width() - 50 or self.x - self.shift < 50:
                self.direction = not(self.direction)
                
        if self.direction == True:
            self.x += self.shift
        else:
            self.x -= self.shift
        
        for ext in self.extentions:
            ext.follow(self.x, self.y)
    
    def shoot(self, vel):
        self.cooldown()
        if self.color == "green":
            if self.cool_down_counter == 0 and self.shoot_now:
                boss_laser_sound.play()
                loc_x = self.x + self.get_width()/2 - 50
                loc_y = self.y + self.get_height() - 20
                laser = Laser(loc_x, loc_y, self.laser_img, self.color, vel)
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
                
                laser1 = Laser(loc_x1, loc_y, self.laser_img, self.color, vel)
                laser2 = Laser(loc_x2, loc_y1, self.laser_img, self.color, vel)
                laser3 = Laser(loc_x3, loc_y, self.laser_img, self.color, vel)
                self.cool_down_counter += 1
                return [laser1, laser2, laser3]
            
        if self.color == "gold":
            self.cooldown2()
            if self.cool_down_counter == 0 and self.shoot_now:
                self.cool_down_counter += 1
            
            if self.cool_down_counter2 == 0 and self.shoot_now:
                boss_laser_sound.play()
                fb1 = Laser(self.x - 35, self.y - 5, fire_ball, None, 4)
                fb2 = Laser(self.x + 365, self.y - 5, fire_ball, None, 4)
                
                self.cool_down_counter2 += 1
                return[fb1, fb2]
                
    def healthbar(self, window):
        pygame.draw.rect(window, (240,90,0), (self.x, self.y - 10, self.ship_img.get_width(), 15))
        pygame.draw.rect(window, (40,255,0), (self.x, self.y - 10, self.ship_img.get_width() * (self.health/self.max_health), 15))
    
# GUI objects
class Button:
    def __init__(self, x, y, color, label):
        self.color = color
        self.rect = pygame.Rect(x, y, label.get_width() + 20, label.get_height() + 20)
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
            if self.counter > time - self.slide_time*2.5:
                    self.x += velocity
                    window.blit(self.label, (self.x, self.y))
            else:
                window.blit(self.label, (self.x, self.y))
                self.counter += 1
        

# Assistive functions
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (int(offset_x), int(offset_y))) != None