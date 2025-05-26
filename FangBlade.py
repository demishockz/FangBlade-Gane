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
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 8
level = 1

#define player action variables
moving_left = False
moving_right = False
shoot = False
lightslash = False
heavyslash = False
global damage_boost
damage_boost = 0

#load images
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
    pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))

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
            
        self.img = self.animation_list[self.action][self.frame_index]
        self.rect = self.img.get_rect()
        self.rect.center = (x,y)

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

        #check collision with floor
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False

            #update rectangle position
        self.rect.x += dx
        self.rect.y += dy

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
        self.img = self.animation_list[self.action][self.frame_index]
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
        screen.blit(pygame.transform.flip(self.img, self.flip, False,), self.rect)

class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
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
            
        self.img = self.animation_list[self.action][self.frame_index]
        self.rect = self.img.get_rect()
        self.rect.center = (x,y)

    def update(self):
        self.update_animation()
        self.check_alive()
        #update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
    
    def move(self, moving_left, moving_right):
        #reset movement variables
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

        #apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        #check collision with floor
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False

            #update rectangle position
        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 30
            bat = Bat(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery, self.direction, 250)
            bat_group.add(bat)
            #reduce ammo
            self.ammo -= 1

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)  # 0: idle
                self.idling = True
                self.idling_counter = 50
            #check if player is in vision
            if self.vision.colliderect(player.rect):
                #stop running and face the player
                self.update_action(3) 
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # 1: run
                    self.move_counter += 1
                    #update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
               
    def update_animation(self):
        #update the animation
        ANIMATION_COOLDOWN = 100
        #update image depending on current frame
        self.img = self.animation_list[self.action][self.frame_index]
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
        screen.blit(pygame.transform.flip(self.img, self.flip, False,), self.rect)


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
        

    #check for collision with characters
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, lightslashsprite_group, False):
                if enemy.alive:
                    enemy.health -= (50 + damage_boost)
                    print(enemy.health)
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

    #check for collision with characters
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, heavyslashsprite_group, False):
                if enemy.alive:
                    enemy.health -= (100 + damage_boost)
                    print(enemy.health)
                    self.kill()

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
    
#create sprite groups
enemy_group = pygame.sprite.Group()
shuriken_group = pygame.sprite.Group()
bat_group = pygame.sprite.Group()
lightslashsprite_group = pygame.sprite.Group()
heavyslashsprite_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()

#temp - create item boxes
item_box = ItemBox('Heal', 100, 260)
item_box_group.add(item_box)
item_box = ItemBox('Ammo', 400, 260)
item_box_group.add(item_box)
item_box = ItemBox('Damage', 500, 260)
item_box_group.add(item_box)
item_box = ItemBox('Coin', 600, 260)
item_box_group.add(item_box)


player = Ronin('player', 200, 200, 3.5, 5, 20)
health_bar = HealthBar(10, 10, player.health, player.max_health)


enemy = Vampire('enemy', 400, 200, 3.5, 2, 20)
enemy2 = Vampire('enemy', 300, 300, 3.5, 2, 20)
enemy_group.add(enemy)
enemy_group.add(enemy2)

font = pygame.font.SysFont(None, 24)
shop_menu = ShopMenu(screen, font)
shop_open = False
player_currency = 100  # Starting currency

run = True
while run:
    
    clock.tick(FPS)

    if shop_open:
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

        player.move(moving_left, moving_right)

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