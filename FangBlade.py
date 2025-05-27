import pygame
import os
import random
import csv
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("FangBlade")

#set framerate
clock = pygame.time.Clock()
FPS = 60

#define game variables
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 9
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
level_complete = False

#define player action variables
moving_left = False
moving_right = False
shoot = False
lightslash = False
heavyslash = False
global damage_boost
damage_boost = 0


#load images
start_img = pygame.image.load('/Users/abhinava/VisualStudioCode/fangblade_assets/start_btn.png').convert_alpha()
restart_img = pygame.image.load('/Users/abhinava/VisualStudioCode/fangblade_assets/start_btn.png').convert_alpha()
quit_img = pygame.image.load('/Users/abhinava/VisualStudioCode/fangblade_assets/quit_btn.png').convert_alpha()
start_screen_img = pygame.image.load('/Users/abhinava/VisualStudioCode/fangblade_assets/fangblade_start_2_65.jpg').convert_alpha()
bg_img = pygame.image.load('/Users/abhinava/VisualStudioCode/fangblade_assets/fangblade_bg3.jpg').convert_alpha()
#store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'/Users/abhinava/VisualStudioCode/fangblade_assets/Tile/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)
#shuriken
shuriken_img = pygame.image.load('/Users/abhinava/VisualStudioCode/fangblade_assets/Shuriken/shuriken.png').convert_alpha()
bat_img = pygame.image.load('/Users/abhinava/VisualStudioCode/fangblade_assets/Bat/bat.png').convert_alpha()
lightslashsprite_img = pygame.image.load('/Users/abhinava/VisualStudioCode/fangblade_assets/SlashSprite/lightslash.png').convert_alpha()
heavyslashsprite_img = pygame.image.load('/Users/abhinava/VisualStudioCode/fangblade_assets/SlashSprite/heavyslash.png').convert_alpha()
#load item boxes
heal_box_img = pygame.image.load('/Users/abhinava/VisualStudioCode/fangblade_assets/ItemBoxes/heal_box.png').convert_alpha()
ammo_box_img = pygame.image.load('/Users/abhinava/VisualStudioCode/fangblade_assets/ItemBoxes/ammo_box.png').convert_alpha()
damage_box_img = pygame.image.load('/Users/abhinava/VisualStudioCode/fangblade_assets/ItemBoxes/damage_box.png').convert_alpha()
coin_box_img = pygame.image.load('/Users/abhinava/VisualStudioCode/fangblade_assets/ItemBoxes/coin_box.png').convert_alpha()
item_boxes = {
    'Heal': heal_box_img,
    'Ammo': ammo_box_img,
    'Damage': damage_box_img,
    'Coin': coin_box_img
}

BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

#define font
font = pygame.font.SysFont(None, 30)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_bg():
    screen.fill(BG)
    width = bg_img.get_width()
    for x in range(5):
        screen.blit(bg_img, ((x * width - 50) - screen_scroll, 0))

def reset_level():
    enemy_group.empty()
    shuriken_group.empty()
    bat_group.empty()
    lightslashsprite_group.empty()
    heavyslashsprite_group.empty()
    item_box_group.empty()

    #create empty tile list
    world_data = []
    for row in range(ROWS):
        r = [-1] * COLS
        world_data.append(r)
    return world_data


class Ronin(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.lightslash_cooldown = 0
        self.heavyslash_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        #ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0
        
        #load all of the images for the player
        animation_types = ['Idle', 'Run', 'Jump', 'Death', 'LightSlash', 'HeavySlash']
        for animation in animation_types:
            #reset temporary list of image
            temp_list = []
            #count number of images in the folder
            num_of_frames = len(os.listdir(f'/Users/abhinava/VisualStudioCode/fangblade_assets/{animation}'))
            for i in range(num_of_frames - 1):
                img = pygame.image.load(f'/Users/abhinava/VisualStudioCode/fangblade_assets/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
            
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        #update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.lightslash_cooldown > 0:
            self.lightslash_cooldown -= 1
        if self.heavyslash_cooldown > 0:
            self.heavyslash_cooldown -= 1
    
    def move(self, moving_left, moving_right):
        #reset movement variables
        screen_scroll = 0
        dx = 0
        dy = 0

        #assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        #jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        #apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        #check for collision
        for tile in world.obstacle_list:
            #check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                #if the ai has hit a wall then make it turn around
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            #check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #check if below the ground, i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                #check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom


        #check if going off the edges of the screen
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        #update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        #update scroll based on player position
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
                or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll



    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            shuriken = Shuriken(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            shuriken_group.add(shuriken)
            #reduce ammo
            self.ammo -= 1

    def lightslash(self):
        if self.lightslash_cooldown == 0:
            self.update_action(4)
            self.lightslash_cooldown = 50
            
            lightslashsprite = LightSlashSprite(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery, self.direction, 250)
            lightslashsprite_group.add(lightslashsprite)
    
    def heavyslash(self):
        if self.heavyslash_cooldown == 0:
            self.update_action(5)
            self.heavyslash_cooldown = 100
            
            heavyslashsprite = HeavySlashSprite(self.rect.centerx + (self.rect.size[0] * self.direction), self.rect.centery, self.direction, 250)
            heavyslashsprite_group.add(heavyslashsprite)
            
    
    def update_animation(self):
        #update the animation
        ANIMATION_COOLDOWN = 100
        #update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN: 
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #if the animation has reached the end, reset to 0
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0


    def update_action(self, new_action):
        #check if the new action is different from the previous one
        if new_action != self.action:
            self.action = new_action
            #update the frame index to 0
            self.frame_index = 0
            #update the time
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False,), self.rect)

class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
    # Iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 1:
                        self.obstacle_list.append(tile_data)
                    elif tile == 2:  # Create player
                        global player, health_bar
                        player = Ronin('player', x * TILE_SIZE, y * TILE_SIZE, 3.5, 7, 20)
                        health_bar = HealthBar(10, 10, player.health, player.max_health)
                    elif tile == 3:  # Create enemies
                        enemy = Vampire('enemy', x * TILE_SIZE, y * TILE_SIZE, 3.5, 2, 20)
                        enemy_group.add(enemy)
                    elif tile == 4:  # Coin
                        item_box = ItemBox('Coin', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 5:  # Ammo
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 6:  # Health
                        item_box = ItemBox('Heal', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 7:  # Damage Boost
                        item_box = ItemBox('Damage', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 8:
                        boss = Boss('boss', x * TILE_SIZE, y * TILE_SIZE, 5, 2, 20)
                        boss_group.add(boss)


        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1].x += screen_scroll
            screen.blit(tile[0], tile[1])



class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll
        #check if player has picked up the box
        if pygame.sprite.collide_rect(self, player):
            #check what kind of box it was
            if self.item_type == 'Heal':
                print(f"Player health before healing: {player.health}")
                player.health = min(player.health + 20, player.max_health)  # Cap health at max_health
                print(f"Player health after healing: {player.health}")
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 5
            elif self.item_type == 'Damage':
                global damage_boost                
                damage_boost += 5
            elif self.item_type == 'Coin':
                global player_currency
                player_currency += 10
            self.kill()

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health
        
    def draw(self, health):
        #update with new health
        self.health = health
        #calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

class Shuriken(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = shuriken_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        #move shuriken
        self.rect.x += (self.speed * self.direction)
        #check if shuriken is off screen
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.kill()
        #check for collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        #check for collision with characters
        if pygame.sprite.spritecollide(player, shuriken_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, shuriken_group, False):
                if enemy.alive:
                    enemy.health -= (25 + damage_boost)
                    print(enemy.health)
                    self.kill()
        if pygame.sprite.spritecollide(boss, shuriken_group, False):
            if boss.alive:
                boss.health -= (25 + damage_boost)
                print(boss.health)
                self.kill()
                
class Vampire(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        #ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0
        
        #load all of the images for the player
        animation_types = ['Idle', 'Run', 'Death', 'Attack']
        for animation in animation_types:
            #reset temporary list of image
            temp_list = []
            #count number of images in the folder
            num_of_frames = len(os.listdir(f'/Users/abhinava/VisualStudioCode/fangblade_assets/Enemy/{animation}'))
            for i in range(num_of_frames - 1):
                img = pygame.image.load(f'/Users/abhinava/VisualStudioCode/fangblade_assets/Enemy/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
            
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        #update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
    
    def move(self, moving_left, moving_right):
        dx = 0
        dy = 0

        # Assign movement variables if moving left or right
        if self.alive:
            if moving_left:
                dx = -self.speed
                self.flip = True
                self.direction = -1
            if moving_right:
                dx = self.speed
                self.flip = False
                self.direction = 1

        # Apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # Check collision with floor
        for tile in world.obstacle_list:
            # Check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            # Check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:  # Jumping
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:  # Falling
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # Update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        # Check if the vampire is still in the air
        if self.rect.bottom < SCREEN_HEIGHT:
            self.in_air = True

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 30
            bat = Bat(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery, self.direction, 250)
            bat_group.add(bat)
            #reduce ammo
            self.ammo -= 1

    def ai(self):
        if self.alive and player.alive:
            if not self.idling and random.randint(1, 200) == 1:
                self.update_action(0)  # 0: idle
                self.idling = True
                self.idling_counter = 50

            # Check if player is in vision
            if self.vision.colliderect(player.rect):
                self.update_action(3)  # 3: Attack
                self.shoot()
            else:
                if not self.idling:
                    # Move in the current direction
                    ai_moving_right = self.direction == 1
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # 1: Run
                    self.move_counter += 1

                    # Update AI vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    # Reverse direction if move_counter exceeds range
                    if abs(self.move_counter) > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter = 0
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        # Adjust position for screen scrolling
        self.rect.x += screen_scroll
               
    def update_animation(self):
        #update the animation
        ANIMATION_COOLDOWN = 100
        #update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN: 
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #if the animation has reached the end, reset to 0
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 2:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0


    def update_action(self, new_action):
        #check if the new action is different from the previous one
        if new_action != self.action:
            self.action = new_action
            #update the frame index to 0
            self.frame_index = 0
            #update the time
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(2)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False,), self.rect)

class Boss(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        #ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0
        
        #load all of the images for the player
        animation_types = ['Idle', 'Run', 'Death', 'Attack']
        for animation in animation_types:
            #reset temporary list of image
            temp_list = []
            #count number of images in the folder
            num_of_frames = len(os.listdir(f'/Users/abhinava/VisualStudioCode/fangblade_assets/Enemy/{animation}'))
            for i in range(num_of_frames - 1):
                img = pygame.image.load(f'/Users/abhinava/VisualStudioCode/fangblade_assets/Enemy/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
            
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        global level_complete
        self.update_animation()
        self.check_alive()
        #update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if not self.alive:
            level_complete = True
    
    def move(self, moving_left, moving_right):
        dx = 0
        dy = 0

        # Assign movement variables if moving left or right
        if self.alive:
            if moving_left:
                dx = -self.speed
                self.flip = True
                self.direction = -1
            if moving_right:
                dx = self.speed
                self.flip = False
                self.direction = 1

        # Apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # Check collision with floor
        for tile in world.obstacle_list:
            # Check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            # Check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:  # Jumping
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:  # Falling
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # Update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        # Check if the vampire is still in the air
        if self.rect.bottom < SCREEN_HEIGHT:
            self.in_air = True

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 30
            bat = Bat(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery, self.direction, 250)
            bat_group.add(bat)
            #reduce ammo
            self.ammo -= 1

    def ai(self):
        if self.alive and player.alive:
            if not self.idling and random.randint(1, 200) == 1:
                self.update_action(0)  # 0: idle
                self.idling = True
                self.idling_counter = 50

            # Check if player is in vision
            if self.vision.colliderect(player.rect):
                self.update_action(3)  # 3: Attack
                self.shoot()
            else:
                if not self.idling:
                    # Move in the current direction
                    ai_moving_right = self.direction == 1
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # 1: Run
                    self.move_counter += 1

                    # Update AI vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    # Reverse direction if move_counter exceeds range
                    if abs(self.move_counter) > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter = 0
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        # Adjust position for screen scrolling
        self.rect.x += screen_scroll
               
    def update_animation(self):
        #update the animation
        ANIMATION_COOLDOWN = 100
        #update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN: 
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #if the animation has reached the end, reset to 0
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 2:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0


    def update_action(self, new_action):
        #check if the new action is different from the previous one
        if new_action != self.action:
            self.action = new_action
            #update the frame index to 0
            self.frame_index = 0
            #update the time
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(2)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False,), self.rect)

class Bat(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, scale):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.scale = scale
        self.image = bat_img
        if direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.flip = False

    def update(self):
        #move bat
        self.rect.x += (self.speed * self.direction)
        #check if bat is off screen
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.kill()
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        #check for collision with characters
        if pygame.sprite.spritecollide(player, bat_group, False):
            if player.alive:
                player.health -= 5
                self.kill()

class LightSlashSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, scale):
        pygame.sprite.Sprite.__init__(self)
        self.scale = scale
        self.speed = 7
        self.image = lightslashsprite_img
        if direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.spawn_x = x
        self.flip = False

    def update(self):
        #move slash
        self.rect.x += (self.speed * self.direction)
        #check if slash is off screen
        if abs(self.rect.x - self.spawn_x) > 100:
            self.kill()
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        

    #check for collision with characters
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, lightslashsprite_group, False):
                if enemy.alive:
                    enemy.health -= (50 + damage_boost)
                    print(enemy.health)
                    self.kill()
        if pygame.sprite.spritecollide(boss, lightslashsprite_group, False):
            if boss.alive:
                boss.health -= (50 + damage_boost)
                print(boss.health)
                self.kill()

class HeavySlashSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, scale):
        pygame.sprite.Sprite.__init__(self)
        self.scale = scale
        self.speed = 5
        self.image = heavyslashsprite_img
        if direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.spawn_x = x

    def update(self):
        #move slash
        self.rect.x += (self.speed * self.direction)
        #check if slash is off screen
        if abs(self.rect.x - self.spawn_x) > 50:
            self.kill()
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

    #check for collision with characters
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, heavyslashsprite_group, False):
                if enemy.alive:
                    enemy.health -= (100 + damage_boost)
                    print(enemy.health)
                    self.kill()
        if pygame.sprite.spritecollide(boss, heavyslashsprite_group, False):
                if boss.alive:
                    boss.health -= (100 + damage_boost)
                    print(boss.health)
                    self.kill()

class Button():
	def __init__(self,x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action

class ShopMenu:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.items = [
            {"name": "Health Potion", "price": 50},
            {"name": "Ammo Pack", "price": 30},
            {"name": "Damage Boost", "price": 100},
        ]
        self.selected_index = 0

    def draw(self, player_currency):
        # Draw the shop background
        pygame.draw.rect(self.screen, (0, 0, 0), (200, 100, 400, 400))
        pygame.draw.rect(self.screen, (255, 255, 255), (200, 100, 400, 400), 3)

        # Draw the shop title
        title_text = self.font.render("Shop Menu", True, (255, 255, 255))
        self.screen.blit(title_text, (300, 120))

        # Draw the player's currency
        currency_text = self.font.render(f"Currency: {player_currency}", True, (255, 255, 0))
        self.screen.blit(currency_text, (250, 160))

        # Draw the items
        for i, item in enumerate(self.items):
            color = (255, 255, 255) if i == self.selected_index else (150, 150, 150)
            item_text = self.font.render(f"{item['name']} - {item['price']} coins", True, color)
            self.screen.blit(item_text, (250, 200 + i * 40))

    def handle_input(self, event, player_currency):
        # Navigate the menu
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.selected_index = (self.selected_index - 1) % len(self.items)
            if event.key == pygame.K_s:
                self.selected_index = (self.selected_index + 1) % len(self.items)
            if event.key == pygame.K_j:  # Purchase the selected item
                selected_item = self.items[self.selected_index]
                if player_currency >= selected_item["price"]:
                    return selected_item
        return None
    
#create button groups
start_button = Button(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 50, start_img, 1)
quit_button = Button(SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2 + 50, quit_img, 1)
restart_button = Button(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 50, restart_img, 2)

#create sprite groups
enemy_group = pygame.sprite.Group()
shuriken_group = pygame.sprite.Group()
bat_group = pygame.sprite.Group()
lightslashsprite_group = pygame.sprite.Group()
heavyslashsprite_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
boss_group = pygame.sprite.Group()


#create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
#load in level data and create world
with open(f'/Users/abhinava/VisualStudioCode/fangblade_assets/level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
                world_data[x][y] = int(tile)

world = World()
player, health_bar = world.process_data(world_data)

font = pygame.font.SysFont(None, 24)
shop_menu = ShopMenu(screen, font)
shop_open = False
player_currency = 100  # Starting currency

run = True
while run:
    
    clock.tick(FPS)

    if level_complete == True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        #draw menu
        screen.fill(BG)
        screen.blit(start_screen_img, (-230, -60))
        draw_text(f'YOU WIN', font, WHITE, SCREEN_WIDTH // 2 - 20, 55)

    else:        
        if start_game == False:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            #draw menu
            screen.fill(BG)
            screen.blit(start_screen_img, (-230, -60))
            #add buttons
            if start_button.draw(screen):
                start_game = True
            if quit_button.draw(screen):
                run = False
            
            
        else:
            if shop_open:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                # Draw the shop menu
                draw_bg()
                shop_menu.draw(player_currency)
                

                # Handle shop menu input
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                        shop_open = False
                    purchased_item = shop_menu.handle_input(event, player_currency)
                    if purchased_item:
                        if purchased_item["name"] == "Health Potion":
                            player.health = min(player.health + 20, player.max_health)
                        elif purchased_item["name"] == "Ammo Pack":
                            player.ammo += 5
                        elif purchased_item["name"] == "Damage Boost":
                            damage_boost += 5
                        player_currency -= purchased_item["price"]
                        print(f"Purchased: {purchased_item['name']}")

            else:
                draw_bg()
                world.draw()
                #show player health
                health_bar.draw(player.health)
                #show values
                draw_text(f'CURRENCY: {player_currency}', font, WHITE, 10, 35)
                draw_text(f'AMMO: ', font, WHITE, 10, 55)
                for i in range(player.ammo):
                    screen.blit(shuriken_img, (70 + (i * 10), 55))
                draw_text(f'DAMAGE BOOST: {damage_boost}', font, WHITE, 10, 75)
                draw_text(f'LIGHT SLASH COOLDOWN: {player.lightslash_cooldown}', font, WHITE, 10, 95)
                draw_text(f'HEAVY SLASH COOLDOWN: {player.heavyslash_cooldown}', font, WHITE, 10, 115)

                player.update()
                player.draw()

                for enemy in enemy_group:
                    enemy.ai()
                    enemy.update()
                    enemy.draw()

                for boss in boss_group:
                    boss.ai()
                    boss.update()
                    boss.draw()

                #update and draw groups
                shuriken_group.update()
                shuriken_group.draw(screen)
                bat_group.update()
                bat_group.draw(screen)
                lightslashsprite_group.update()
                lightslashsprite_group.draw(screen)
                heavyslashsprite_group.update()
                heavyslashsprite_group.draw(screen)
                item_box_group.update()
                item_box_group.draw(screen)

                #update player actions
                if player.alive:
                    if player.action == 4 and player.frame_index == len(player.animation_list[4]) - 1:
                        lightslash = False
                    if player.action == 5 and player.frame_index == len(player.animation_list[5]) - 1:
                        heavyslash = False
                    #shoot shuriken
                    if shoot:
                        player.shoot()
                    elif lightslash:
                        player.lightslash()
                    elif heavyslash:
                        player.heavyslash()
                    elif player.in_air:
                        player.update_action(2)#2: jump
                    elif moving_left or moving_right:
                        player.update_action(1)#1: run
                    else:
                        player.update_action(0)#0: idle
                    
                    screen_scroll = player.move(moving_left, moving_right)
                    bg_scroll = screen_scroll
                else:
                    screen_scroll = 0
                    if restart_button.draw(screen):
                        bg_scroll = 0
                        world_data = reset_level()
                        with open(f'/Users/abhinava/VisualStudioCode/fangblade_assets/level{level}_data.csv', newline='') as csvfile:
                            reader = csv.reader(csvfile, delimiter=',')
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                        world_data[x][y] = int(tile)
                        world = World()
                        player, health_bar = world.process_data(world_data)
                    

                for event in pygame.event.get():
                    #quit game
                    if event.type == pygame.QUIT:
                        run = False
                    #keyboard presses
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_a:
                            moving_left = True
                        if event.key == pygame.K_d:
                            moving_right = True
                        if event.key == pygame.K_j:
                            shoot = True
                        if event.key == pygame.K_k:
                            lightslash = True
                        if event.key == pygame.K_l:
                            heavyslash = True
                        if event.key == pygame.K_w:
                            player.jump = True
                        if event.key == pygame.K_ESCAPE:
                            run = False
                        if event.key == pygame.K_e:
                            shop_open = not shop_open

                    #keyboard button released
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_a:
                            moving_left = False
                        if event.key == pygame.K_d:
                            moving_right = False
                        if event.key == pygame.K_j:
                            shoot = False
                    
            
            


    pygame.display.update()

pygame.quit()