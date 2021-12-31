import pygame
import os
import time
import random
from objects import collide, Player, Enemy
pygame.font.init()

# Sets up pygame window
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fake Space Invaders")

BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT) )

    
def main():
    run = True
    FPS = 60
    lost = False
    won = False
    new_level = False
    
    stop_timer = 0
    level = 0
    lives = 5
    wave = 1
    
    main_font = pygame.font.SysFont("comicsans", 55)
    end_font = pygame.font.SysFont("arial", 80)
    wave_font = pygame.font.SysFont("comicsans", 100)
    
    laser_velocity = 6
    laser_velocity2 = 8
    player_velocity = 4
    fire_rate = 7
    wave_length = 5
    wave_range = -1500
    enemy_velocity = 1
    Enemy.shift = 0
    
    enemies = []
    lasers = []
    
    player = Player(300, 620)
    
    clock = pygame.time.Clock()
    
    def move_lasers(velocity, object):
        for laser in lasers:
            laser.move(velocity)
            if laser.off_screen(HEIGHT):
                lasers.remove(laser)
            elif laser.collision(object):
                if laser.color == "green":
                    object.health -= 15
                elif laser.color == "red":
                    object.health -= 10
                else:
                    object.health -= 5
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
        
        if new_level == True:
            new_level_label = wave_font.render(f"Wave {wave}", 1, (255,255,255))
            WIN.blit(new_level_label, (WIDTH/2 - new_level_label.get_width()/2, 350))
            
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
        if new_level:
            if stop_timer > FPS*2:
                new_level = False
                stop_timer = 0
                wave += 1 
            else: 
                stop_timer += 1
                if len(player.lasers) != 0:
                    player.lasers.clear()
                continue
            
        if lives <= 0 or player.health <= 0:
            lost = True 
            stop_timer += 1
            
        if len(enemies) == 0 and level == 30:
            won = True
            stop_timer += 1
        
        if lost or won:
            if stop_timer > FPS*3:
                run = False
            else: 
                continue
        
        # Spawns enemies and handles difficulty ramp with new waves
        if len(enemies) == 0:
            
            player_velocity += .2
            enemy_velocity += .1
            wave_length += 1

            if level % 10 == 0 and level != 0:
                player.max_health += 100
                fire_rate -= 1
                
            if level % 5 == 0 and level != 0:
                wave_range -= 500
                Enemy.shift += .5
                player.health = player.max_health
                if Player.max_cooldown > 10:
                    Player.max_cooldown -= 5
                    
            if level % 5 == 0:
                new_level = True
            
            for i in range(wave_length):
                enemy = Enemy(random.randrange(100, WIDTH-100), random.randrange(wave_range, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)
                
            level += 1

        # Checks to see if program has been quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
               quit()
        
        # Makes the ship respond to keypresses (Move and shoot)
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and player.y - player_velocity > 70: # Forward
            player.y -= player_velocity   
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player.y + player_velocity < HEIGHT - player.get_height() - 20: # Backward
            player.y += player_velocity
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player.x + player_velocity < WIDTH - player.get_width() - 10: # Right
            player.x += player_velocity
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player.x - player_velocity > 10: # Left
            player.x -= player_velocity
        
        if keys[pygame.K_SPACE]:
            player.shoot()
        
        # Returns to main menu if esc is pressed
        if keys[pygame.K_ESCAPE]:
            run = False
        
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
        
        
        
               
def main_menu():
    title_font = pygame.font.SysFont("comicsans", 50)
    run = True
    while run:
        WIN.blit(BACKGROUND, (0,0))
        title_label = title_font.render("Press enter to begin..", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            main()
            
    pygame.quit()
    
main_menu()
            
