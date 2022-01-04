import pygame
import random
import sys
from objects import collide, Player, Enemy, Boss, Button

pygame.font.init()

# Sets up pygame window
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fake Space Invaders")

# Loads in assets
enemy_collide_sound = pygame.mixer.Sound("audio/enemy_collide_sound.wav")
player_impact_sound = pygame.mixer.Sound("audio/player_impact_sound.wav")
player_impact_sound.set_volume(.4)

BACKGROUND = pygame.transform.scale(pygame.image.load("assets/background-black.png"), (WIDTH, HEIGHT))

def main(): 
    FPS = 60
    run = True
    lost = False
    won = False
    new_level = False
    pause = False
    
    # Counter variables
    colide_cooldown = 0
    stop_timer = 0
    level = 0
    lives = 5
    wave = 1
    
    # All fonts
    display_font = pygame.font.SysFont("arial", 40)
    end_font = pygame.font.SysFont("arial", 80)
    title_font_large = pygame.font.SysFont("comicsans", 70)
    title_font = pygame.font.SysFont("comicsans", 40)
    wave_font = pygame.font.SysFont("comicsans", 100)
    
    # Velocitys
    laser_velocity = 6
    laser_velocity_player = 8
    player_velocity = 4
    enemy_velocity = 1
    boss_velocity = .5
    
    # Progressive values
    fire_rate = 7
    wave_length = 5
    wave_range = -1300
    Enemy.shift = 0
    Player.max_cooldown = 25
    
    # Objects lists
    bosses = []
    enemies = []
    lasers = []
    
    player = Player(300, 600)
    
    clock = pygame.time.Clock()
    
    # Moves enemy lasers and checks for collisions
    def move_lasers(velocity, object):
        for laser in lasers:
            laser.move(velocity)
            if laser.off_screen(HEIGHT):
                lasers.remove(laser)
            elif laser.collision(object):
                player_impact_sound.play()
                if Player.damage:
                    object.health -= 10
                lasers.remove(laser)
    
    # Defines buttons        
    resume_label = title_font.render("Resume", 1, (220,220,220))
    menu_label = title_font.render("Main Menu", 1, (200,200,200))
    
    resume_button = Button((150, 380, 160, 80), (60,60,60), resume_label)
    main_menu_button = Button((400, 380, 220, 80), (60,60,60), menu_label)
    
    # Displays everything on screen
    def draw_window():
        WIN.blit(BACKGROUND, (0,0))
        
        lives_label = display_font.render(f"Lives- {lives}", 1, (240,240,240))
        level_label = display_font.render(f"Level {level}", 1, (240,240,240))
        WIN.blit(lives_label, (20, 10))
        WIN.blit(level_label, (590, 10))
        
        for enemy in enemies:
            enemy.draw(WIN)
            
        for boss in bosses:
            boss.draw(WIN)
            
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
        
        if pause == True:
            WIN.blit(BACKGROUND, (0,0))
            pause_label = title_font_large.render("PAUSE", 1, (250,250,250))
            WIN.blit(pause_label, (WIDTH/2 - pause_label.get_width()/2, 180))
            WIN.blit(lives_label, (20, 10))
            WIN.blit(level_label, (590, 10))
            
            resume_button.draw(WIN)
            main_menu_button.draw(WIN)
            
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
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                stop_timer += 1
                if len(lasers) != 0 or len(player.lasers) != 0:
                    lasers.clear()
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
        
        if pause:   
            for event in pygame.event.get():
                if resume_button.click(event):
                    pause = False
                if main_menu_button.click(event):
                    run = False
                else:  
                    if event.type == pygame.QUIT:
                        sys.exit()
            continue
            
            
        if len(enemies) == 0 and len(bosses) == 0:
            
            #Handles difficulty ramp
            player_velocity += .2
            enemy_velocity += .1
            wave_length += 1

            if level % 10 == 0 and level != 0:
                fire_rate -= 1
                player.health = player.max_health
                Player.max_cooldown -= 5
                wave_length -= 5
                
            if level % 5 == 0 and level != 0:
                wave_range -= 500
                Enemy.shift += .5
                if player.health + 20 < player.max_health:
                    player.health += 20
                    
                    
            if level % 5 == 0:
                new_level = True
            
            #Spwans bosses
            if level == 9:
                boss = Boss(350, -300, "green")
                bosses.append(boss)
            elif level == 19:
                boss = Boss(350, -300, "red", 400)
                Boss.shift = 1.7
                Boss.max_cooldown = 6
                bosses.append(boss)
                
            #Spawns enemies
            else:
                for i in range(wave_length):
                    enemy = Enemy(random.randrange(100, WIDTH-100), random.randrange(wave_range, -100), random.choice(["red", "blue", "green"]))
                    enemies.append(enemy)
                    
                for enemy in enemies:
                    for enemy2 in enemies:
                        if enemy != enemy2:
                            if collide(enemy, enemy2):
                                enemies.remove(enemy2)
                                enemy = Enemy(random.randrange(100, WIDTH-100), random.randrange(wave_range, -100), random.choice(["red", "blue", "green"]))
                                enemies.append(enemy)
            
            level += 1

        # Checks to see if program has been quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        
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
            pause = True
        
        
        move_lasers(laser_velocity, player)
        
        # Handles enemies
        for enemy in enemies[:]:
            enemy.move(enemy_velocity)
            
            # Enemies shoot lasers
            if random.randrange(0, fire_rate*60) == 1:
                laser = enemy.shoot()
                if laser != None:
                    lasers.append(laser)
                
            # Player loses health if they collide with an enemy
            if collide(enemy, player):
                if Player.damage:
                    if enemy.color == "blue":
                        player.health -= 5
                    else:
                        player.health -= 10
                enemy_collide_sound.play()
                enemies.remove(enemy)
                
            # Player loses a life if an enemy reaches the end of the screen
            if enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
        
        # Handles bosses
        if len(bosses) > 0:
            boss = bosses[0]
            
            boss.move(boss_velocity)
            boss.cooldown()
            lasers_in = boss.shoot()
            if lasers_in != None:
                for laser in lasers_in:
                    lasers.append(laser)
            
            # Player and boss lose health when they collide
            if collide(boss, player):
                if colide_cooldown > 30:
                    colide_cooldown = 0
                    
                if colide_cooldown == 0:
                    colide_cooldown = 1
                    if boss.color == "green":
                        player.health -= 20
                        boss.health -= 10
                else:
                    colide_cooldown += 1

            if boss.health <= 0:
                bosses.remove(boss)
                Boss.damage = False
                    
                
        player.move_lasers(-laser_velocity_player, enemies, bosses)
        
        
        
               
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

if __name__ == "__main__":
    main_menu()
            
