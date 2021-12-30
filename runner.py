from typing import List
import pygame
import os
import time
import random

from pygame.constants import NOEVENT
from helpers import invert, collide
pygame.font.init()

# Sets up pygame window
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fake Space Invaders")

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

BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT) )

# Laser object
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
        for laser in self.lasers:
            for object in objects:
                if laser.collision(object):
                    objects.remove(object)
                    self.lasers.remove(laser)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,40,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (20,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

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


                
def main():
    run = True
    FPS = 60
    lost = False
    won = False
    new_level = False
    
    stop_timer = 0
    level = 0
    lives = 5
    
    main_font = pygame.font.SysFont("arial", 40)
    end_font = pygame.font.SysFont("arial", 70)
    
    laser_velocity = 6
    laser_velocity2 = 8
    player_velocity = 4
    fire_rate = 6
    wave_length = 5
    wave_range = -2000
    enemy_velocity = 1
    
    enemies = []
    lasers = []
    player_lasers = []
    
    
    player = Player(300, 650)
    
    clock = pygame.time.Clock()
    
    def move_lasers(velocity, object):
        for laser in lasers:
            laser.move(velocity)
            if laser.off_screen(HEIGHT):
                lasers.remove(laser)
            elif laser.collision(object):
                if laser.color == "blue":
                    object.health -= 5
                else:
                    object.health -= 10
                lasers.remove(laser)
    
    def draw_window():
        # Displays everything on screen
        WIN.blit(BACKGROUND, (0,0))
        
        lives_label = main_font.render(f"Lives- {lives}", 1, (240,240,240))
        level_label = main_font.render(f"Level {level}", 1, (240,240,240))
        WIN.blit(lives_label, (20, 10))
        WIN.blit(level_label, (600, 10))
        
        for enemy in enemies:
            enemy.draw(WIN)
            
        for laser in lasers:
            laser.draw(WIN)
            
        player.draw(WIN)
        
        if len(enemies) == 0 and level % 5 == 0:
            level_labelA = main_font.render(f"Level {level}", 1, (255,255,255))
            WIN.blit(level_labelA, (WIDTH/2 - level_labelA.get_width()/2, 350))
            
        if lost == True:
            lost_label = end_font.render("You Lost!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))
            
        if won == True:
            won_label = end_font.render("You Won!!", 1, (255,255,255))
            WIN.blit(won_label, (WIDTH/2 - won_label.get_width()/2, 350))
            
        pygame.display.update()
    
    # Main loop
    while run:
        clock.tick(FPS)
        draw_window()
        
        # Pauses if there is a new level, the player has won, or the player has lost
        if len(enemies) == 0 and level % 5 == 0 and level != 0:
            new_level = True
            stop_timer += 1
        
        if new_level:
            if stop_timer > FPS*1:
                run = True
            else:
                continue
            
        if lives <= 0 or player.health <= 0:
            lost = True 
            stop_timer += 1
            
        if len(enemies) == 0 and level > 30:
            won = True
            stop_timer += 1
        
        if lost or won:
            if stop_timer > FPS*3:
                run = False
            else: 
                continue
        
        # Spawns enemies and handles difficulty ramp with new waves
        if len(enemies) == 0:
            level += 1
            player_velocity += .25
            if level % 5 == 0:
                wave_range -= 1000
                Enemy.shift += .5
                player.health = player.max_health
                if Player.max_cooldown > 10:
                    Player.max_cooldown -= 5
            
            if level % 10 == 0:
                player.max_health += 100
                
            if wave_length < 50:
                wave_length += 2
            if enemy_velocity < 9:
                enemy_velocity += .3
            for i in range(wave_length):
                enemy = Enemy(random.randrange(100, WIDTH-100), random.randrange(wave_range, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)
                
        # Checks to see if program has been quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
               run = False
        
        # Makes the ship respond to keypresses (Move and shoot)
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and player.y - player_velocity > 70: # Forward
            player.y -= player_velocity   
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player.y + player_velocity < HEIGHT - player.get_height() - 10: # Backward
            player.y += player_velocity
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player.x + player_velocity < WIDTH - player.get_width() - 10: # Right
            player.x += player_velocity
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player.x - player_velocity > 10: # Left
            player.x -= player_velocity
        
        if keys[pygame.K_SPACE]:
            player.shoot()
        
        move_lasers(laser_velocity, player)
        
        # Moves enemies and shoots lasers
        for enemy in enemies[:]:
            enemy.move(enemy_velocity)
            
            # Enemies shoot lasers
            if random.randrange(0, fire_rate*60) == 1:
                laser = enemy.shoot()
                lasers.append(laser)
            # Player loses health if they collide with an enemy
            if collide(enemy, player):
                if enemy.color == "blue":
                    player.health -= 5
                else:
                    player.health -= 10
                enemies.remove(enemy)
            # Enemies disppear when they are hit
            if enemy.health <= 0:
                enemies.remove(enemy)
            # Player loses a life if an enemy reaches the end of the screen
            if enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
                
        player.move_lasers(-laser_velocity2, enemies)
               
main()
            
