import pygame
import os
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

#define player action variables
moving_left = False
moving_right = False

BG = (144, 201, 120)
RED = (255, 0, 0)

def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))

class Ninja(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        
        #load all of the images for the player
        animation_types = ['Idle', 'Run', 'Jump']
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
            self.frame_index = 0


    def update_action(self, new_action):
        #check if the new action is different from the previous one
        if new_action != self.action:
            self.action = new_action
            #update the frame index to 0
            self.frame_index = 0
            #update the time
            self.update_time = pygame.time.get_ticks()


    def draw(self):
        screen.blit(pygame.transform.flip(self.img, self.flip, False,), self.rect)

player = Ninja('player', 200, 200, 3, 5)
enemy = Ninja('enemy', 400, 200, 3, 5)

run = True
while run:
    
    clock.tick(FPS)

    draw_bg()

    player.update_animation()
    player.draw()
    enemy.draw()

    player.move(moving_left, moving_right)

    #update player actions
    if player.alive:
        if player.in_air:
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
            if event.key == pygame.K_w:
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False

        #keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            


    pygame.display.update()

pygame.quit()