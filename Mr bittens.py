import pygame
import os
import random
import sys
import re
import time
from collections import OrderedDict
import math
#from images import images
pygame.init()
class Window():
    display_info = pygame.display.Info()
    width, height = display_info.current_w, display_info.current_h
    w, h = width, height
    screen = pygame.display.set_mode((width, height), pygame.NOFRAME, pygame.FULLSCREEN)
    #screen = pygame.display.set_mode((width, height))
    background_colour = (135, 206, 235)
    clock = pygame.time.Clock()
    fps = 60
    run = True
    menu = False
    physics = True
    map_size = w * 3
    enemy_spawn = time.time()
    spawn_rate = 1
    enemies = []
    my_map = {}
    path = os.path.join("Assets", "parralax1.png")
    back_image = pygame.image.load(path).convert_alpha()
    iw, ih = back_image.get_size()
    scale = max(w, h) / max(iw, ih) 
    back_image = pygame.transform.smoothscale(back_image, (iw *scale , ih * scale))
    path = os.path.join("Assets", "parralax2.png")
    p2 = pygame.image.load(path).convert_alpha()
    p2 = pygame.transform.smoothscale(p2, (width, height))
    path = os.path.join("Assets", "parralax3.png")
    p3 = pygame.image.load(path).convert_alpha()
    p3 = pygame.transform.smoothscale(p3, (width, height))
    path = os.path.join("Assets", "parralax4.png")
    p4 = pygame.image.load(path).convert_alpha()
    #p4 = pygame.transform.smoothscale(p4, (width, height))
    islands = []
    images = []
    if True:
        for i in ["1", "2", "3"]:
            path = os.path.join("Assets", i+"foreground.png")
            image1 = pygame.image.load(path).convert_alpha()
            path = os.path.join("Assets", i+"background.png")
            image2 = pygame.image.load(path).convert_alpha()
            path = os.path.join("Assets", i+"collision.png")
            image3 = pygame.image.load(path).convert_alpha()
            images.append((image1, image2, image3))
    else:
        path = os.path.join("Assets", "1foreground.png")
        image1 = pygame.image.load(path).convert_alpha()
        path = os.path.join("Assets", "1background.png")
        image2 = pygame.image.load(path).convert_alpha()
        path = os.path.join("Assets", "1collision.png")
        image3 = pygame.image.load(path).convert_alpha()
        images.append((image1, image2, image3))
        path = os.path.join("Assets", "2foreground.png")
        image1 = pygame.image.load(path).convert_alpha()
        path = os.path.join("Assets", "2background.png")
        image2 = pygame.image.load(path).convert_alpha()
        path = os.path.join("Assets", "2collision.png")
        image3 = pygame.image.load(path).convert_alpha()
        images.append((image1, image2, image3))
    path = os.path.join("Assets", "cat.png")
    cat_image = pygame.image.load(path).convert_alpha()
    cat_mask = pygame.sprite.from_surface(cat_image)
    terminal_velocity = 100
    projectiles = []
    kittens = []
    def __init__(self):
        self.enemies = []
        self.kittens = []
        self.projectiles = []
        w, h = self.w, self.h
        self.buttons = [(make_text_button("Resume Game", "alphbeta", 48, (255, 255, 255), w//2, int(h * 0.3)), self.pause),
               #(make_text_button("meow", "alphbeta", 48, (255, 255, 255), w//2, int(h * 0.4)), meow),
               (make_text_button("Spawn Rate Up", "alphbeta", 48, (255, 255, 255), w//2, int(h * 0.5)), self.shift_spawn_rate_up),
               (make_text_button("Spawn Rate Down", "alphbeta", 48, (255, 255, 255), w//2, int(h * 0.6)), self.shift_spawn_rate_down),
               (make_text_button("Quit Game!!!", "alphbeta", 48, (255, 255, 255), w//2, int(h * 0.7)), self.stop_game)
        ]
        self.buttons2 = [(make_text_button("You Died!", "alphbeta", 48, (255, 255, 255), w//2, int(h * 0.3)), restart_game),
               (make_text_button("You Died!!", "alphbeta", 48, (255, 255, 255), w//2, int(h * 0.4)), restart_game),
               (make_text_button("You Died!!!", "alphbeta", 48, (255, 255, 255), w//2, int(h * 0.5)), restart_game),
               (make_text_button("You Died!!!!", "alphbeta", 48, (255, 255, 255), w//2, int(h * 0.6)), restart_game),
               (make_text_button("You Died!!!!!", "alphbeta", 48, (255, 255, 255), w//2, int(h * 0.7)), restart_game)
        ]
    def event_loop(self):
        m_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.stop_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.pause()
                elif self.physics: self.keypress_inputs(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN and self.menu:
                for b in self.buttons:
                    rect, func = b[0][1], b[1]
                    if rect.collidepoint(m_pos[0], m_pos[1]): func()
            elif event.type == pygame.MOUSEBUTTONDOWN: self.mousepress_inputs(event)
        if self.physics:
            self.held_inputs()
    def step_event(self):
        self.clock.tick(self.fps)
        self.event_loop()
        self.draw_window()
        if self.physics:
            if PLAYER.hp <= 0:
                PLAYER.hp = 0
                self.buttons = self.buttons2
                self.pause()
                return
            if len(self.kittens) == 0:
                self.enemies = []
                self.enemy_spawn = float("inf")
            if self.spawn_rate > 0:
                spawn_delay = 1 / self.spawn_rate
                if time.time() - self.enemy_spawn >= spawn_delay:
                    ex, ey = random.randint(1, self.map_size), random.randint(1, self.map_size)
                    er = 36
                    x, y, r = PLAYER.x, PLAYER.y, PLAYER.w
                    self.enemies.append(Enemy(ex, ey))
                    self.enemy_spawn = time.time()
            if PLAYER.dash_duration > 0:
                PLAYER.dash_duration -= 1 / self.fps
                dx, dy = PLAYER.dash_direct
                PLAYER.move(x = -dx)
                PLAYER.move(y = dy)
                PLAYER.vel = PLAYER.vel[0], 0
            else:
                vx, vy = PLAYER.vel
                if vy + PLAYER.grav / self.fps <= self.terminal_velocity:
                    PLAYER.vel = vx, vy + PLAYER.grav / self.fps
                vx, vy = PLAYER.vel
                PLAYER.move(x = -vx)
                PLAYER.move(y = vy)
            if self.is_grounded(PLAYER):
                PLAYER.dashes = 1
                PLAYER.checkpoint = PLAYER.x, PLAYER.y
                PLAYER.vy, PLAYER.vx = 0, 0
            projectiles = self.projectiles

            for p in projectiles:
                p.x += p.vx
                p.y += p.vy
                if not p.should_exist():
                    projectiles.remove(p)
                p.collide()
            for k in self.kittens:
                if PLAYER.rect.colliderect(k):
                    self.kittens.remove(k)
            for e in self.enemies:
                e.move_to_player()
    def draw_window(self):
        screen = self.screen
        w, h = self.w, self.h
        screen.fill(self.background_colour)
        camera_x, camera_y = -int(PLAYER.x - PLAYER.starting_pos[0]), -int(PLAYER.y - PLAYER.starting_pos[1])
        sx, sy = PLAYER.starting_pos
        if -camera_x + self.width  - PLAYER.width>= self.map_size:
            camera_x = -self.map_size + self.width - PLAYER.width
        elif -camera_x <= 0:
            camera_x = 0
        self.screen.blit(self.back_image, (0, 0))
        self.screen.blit(self.p2, (camera_x//20 + 100, 0))
        self.screen.blit(self.p3, (camera_x//12 -100, 0))
        self.screen.blit(self.p4, (camera_x//5 - 350, 0))
        x, y = pygame.mouse.get_pos()
        for i in self.islands:
            image = i.foreground
            self.screen.blit(image, (i.x + camera_x, i.y + camera_y))
        PLAYER.drawing_rect.x, PLAYER.drawing_rect.y = PLAYER.x + camera_x, PLAYER.y + camera_y
        #pygame.draw.rect(self.screen, PLAYER.colour, PLAYER.drawing_rect)
        if PLAYER.direction == 1:
            image = PLAYER.right
        else:
            image = PLAYER.left
        self.screen.blit(image, (PLAYER.x + camera_x, PLAYER.y + camera_y))
        for k in self.kittens:

            self.screen.blit(self.cat_image, (k.x + camera_x, k.y + camera_y))
        l = len(self.kittens)
        for i in self.islands:
            image = i.background
            self.screen.blit(image, (i.x + camera_x, i.y + camera_y))
        for e in self.enemies:
            #x, y, r = e.x, e.y, e.rad
            if e.direction == 1:
                image = e.right
            else:
                image = e.left
            self.screen.blit(image, (e.x+camera_x + e.rad // 2, e.y+camera_y + e.rad//2))
            #pygame.draw.circle(self.screen, (255, 64, 64), (x + camera_x, y + camera_y), r)
        for p in self.projectiles:
            x, y, r = p.x, p.y, p.r
            #pygame.draw.circle(self.screen, (128, 128, 128), (x + camera_x, y + camera_y), r)
            self.screen.blit(p.image, (x + camera_x + r, y + camera_y + r))
        if l != 0:
            text = f"You need to collect {l:b} more kittens"
            if l == 1:
                text = text[:-1]
            text, _ = self.get_text(text, colour = (255, 255, 255))
            self.screen.blit(text, (0, 0))
        else:
            text = f"congratulations ^_^"
            text, _ = self.get_text(text, colour=(255, 255, 255))
            self.screen.blit(text, (0, 0))
        if PLAYER.hp != 0:
            text = f"HP: {PLAYER.hp:b}"
            text, wh = self.get_text(text, colour = (255, 200, 200))
            self.screen.blit(text, (self.width-wh[0], 0))
        if self.menu: self.draw_menu()
        pygame.display.update()
    def held_inputs(self):
        keys = pygame.key.get_pressed()
        if PLAYER.dash_duration <= 0:
            if keys[pygame.K_d]:
                PLAYER.move(x = -1)
            if keys[pygame.K_a]:
                PLAYER.move(x = 1)
    def keypress_inputs(self, key):
        keys = pygame.key.get_pressed()
        if self.is_grounded(PLAYER) and (key == pygame.K_SPACE):
            PLAYER.rect.x, PLAYER.rect.y = PLAYER.x, PLAYER.y
            PLAYER.jump(PLAYER.jump_height)
        elif PLAYER.dashes > 0 and (key == pygame.K_SPACE):
            if keys[pygame.K_w] and keys[pygame.K_d]:
                PLAYER.dash(1, -1)
            elif keys[pygame.K_d] and keys[pygame.K_s]:
                PLAYER.dash(1, 1)
            elif keys[pygame.K_s] and keys[pygame.K_a]:
                PLAYER.dash(-1, 1)
            elif keys[pygame.K_a] and keys[pygame.K_w]:
                PLAYER.dash(-1, -1)
            
            elif keys[pygame.K_w]:
                PLAYER.dash(0, -1.5)
            elif keys[pygame.K_d]:
                PLAYER.dash(1.5, 0)
            elif keys[pygame.K_s]:
                PLAYER.dash(0, 1.5)
            elif keys[pygame.K_a]:
                PLAYER.dash(-1.5, 0)
    def mousepress_inputs(self, event):
        if event.button == 1:
            PLAYER.attack()
        elif event.button == 3:
            PLAYER.shoot()
    def is_colliding_with_tile(self, rect):
        collided_with = []
        for i in self.islands:
            if PLAYER.rect.colliderect(i.rect):
                collided_with.append(i)
        if PLAYER.direction == 1:
            PLAYER.mask = PLAYER.mask_right
        else:
            PLAYER.mask = PLAYER.mask_left
        if pygame.sprite.spritecollide(PLAYER, collided_with, False, pygame.sprite.collide_mask):
            return True
        return False
    def is_grounded(self, ob):
        rect = ob.rect
        rect.y += 2
        if self.is_colliding_with_tile(rect):
            rect.y -= 2
            return True
        rect.y -= 2
        return False

    def draw_menu(self):
        buttons = self.buttons
        for b in buttons:
            text, rect = b[0]
            self.screen.blit(text, (rect.x, rect.y))
        if len(buttons) == 4:
            text, wh = self.get_text(f"Spawn Rate: {self.spawn_rate}", colour = (255 ,255 ,255))
            x, y = (self.width//2 - wh[0]//2, self.height*0.4 - wh[1]//2)
            self.screen.blit(text, (x, y))
    
    def pause(self):
        self.physics = not self.physics
        self.menu = not self.menu
    def run_game(self):
        while self.run:
            self.step_event()
    def stop_game(self):
        pygame.quit()
        sys.exit()
    def get_text(self, text, font = "alphbeta", fontsize = 48, colour = (0, 0, 0)):
        """returns rendered text and a tuple of (text_width, text_height) assigns it to main class as a memo"""
        if "fonts" not in locals():
            self.fonts = {}
        if (font, fontsize) not in self.fonts:
            #self.fonts[(font, fontsize)] = pygame.font.SysFont(font, fontsize) 
            self.fonts[(font, fontsize)] = pygame.font.Font(os.path.join("Assets", "alphbeta.ttf"), fontsize)

        font = self.fonts[(font, fontsize)]
        return font.render(text, 1, colour), font.size(text)

    def shift_spawn_rate_up(self):
        self.spawn_rate = round(self.spawn_rate + 0.1, 2)
    def shift_spawn_rate_down(self):
        self.spawn_rate = round(self.spawn_rate - 0.1, 2)
class Creature:
    width, height = 24, 36
    w, h = width, height
    image = None
    colour = 212, 175, 55
    move_speed = 5
    jump_height = 1.8
    grav = 5
    vel = (0, 0)
    jump_height = 2
    direction = 1
    def __init__(self, x, y):
        #self.starting_pos = (WIN.width / 2 - self.width / 2, WIN.height / 1.2)
        self.starting_pos = x + self.w, y - self.h
        self.rect = pygame.Rect(self.starting_pos, (self.w, self.h))
        self.x, self.y = self.starting_pos
        self.starting_pos = (WIN.width / 2 - self.width / 2, WIN.height / 2 - self.height / 2)
        self.drawing_rect = pygame.Rect(self.starting_pos, (self.w, self.h))
        self.checkpoint = x, y
    def move(self, x = 0, y = 0):
        og_x, og_y = x, y
        s = self.move_speed
        sw = s
        self.x -= x * sw
        self.y += y * s
        if x > 0: self.direction = -1
        elif x < 0: self.direction = 1
        self.rect.x, self.rect.y = self.x, self.y

        #out_x = self.rect.x < 0 or self.rect.x + self.rect.w > WIN.map_size
        #out_y = self.rect.y < 0  or self.rect.y > WIN.map_size
        if WIN.is_colliding_with_tile(self.rect):# or out_x or out_y:
            vx, vy = self.vel
            if og_x != 0: # if it's x to move
                self.x += og_x * s
                vx = 0
            if og_y != 0: # if it's y to move
                self.y -= og_y * s
                vy = 0
            self.vel = vx, vy
            self.rect.x, self.rect.y = self.x, self.y
            return
        if self.y > WIN.map_size:
            self.x, self.y = self.checkpoint
            if len(WIN.kittens) > 0:
                self.hp -= 1
        self.x = min(self.x, WIN.map_size)
        self.x = max(self.x, 0)


class Player(pygame.sprite.Sprite, Creature):
    jump_height = 2.5
    dashes = 1
    tot_dash_time = 0.3
    dash_duration = 0
    kit_distance = 1 * 64
    hp = 8 
    def __init__(self, x, y):
        Creature.__init__(self, x, y)
        pygame.sprite.Sprite.__init__(self)
        path = os.path.join("Assets", "hero.png")
        self.left = pygame.image.load(path)
        self.right = pygame.transform.flip(self.left, True, False)
        self.mask_left = pygame.mask.from_surface(self.left)
        self.mask_right = pygame.mask.from_surface(self.right)
    def attack(self):
        pass
    def shoot(self):
        #projectile = pos/rad: (x, y, r), #vel: (x, y)
        x, y = self.x + self.direction, self.y
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            projectile = Projectile(x, y, 0, -12)
            WIN.projectiles.append(projectile)
        elif keys[pygame.K_s]:
            projectile = Projectile(x, y, 0, 12)
            WIN.projectiles.append(projectile)
        else:
            projectile = Projectile(x, y, 12*self.direction, 0)
            WIN.projectiles.append(projectile)

    def jump(self, vel):
        vx, vy = self.vel
        self.vel = vx, -vel * 60 / WIN.fps
    def dash(self, x, y):
        self.dash_duration = self.tot_dash_time
        self.dash_direct = (x * 1.7, y * 1.7)
        self.dashes -= 1
    def near_kitten(self):
        for k in WIN.kittens:
            if abs(self.x - k.x) > self.kit_distance and abs(self.y - k.y) > self.kit_distance:
                return True

class Projectile:
    x_image = pygame.image.load(os.path.join("Assets", "bolt.png"))
    y_image = pygame.transform.rotate(x_image.copy(), 90)
    r = 16
    colour = (255, 64, 64)
    def __init__(self, x, y, vx, vy):
        self.x = x + PLAYER.w//2
        self.y = y + PLAYER.h//2
        self.vx = vx
        self.vy = vy
        if abs(vy) > abs(vx):
            self.image = self.y_image
        else:
            self.image = self.x_image
    def should_exist(self):
        if self.x < 0 or self.x > WIN.map_size:
            return False
        if self.y < 0 or self.y > WIN.map_size:
            return False
        return True
    def collide(self):
        for e in WIN.enemies:
            ex, ey, er = e.x, e.y, e.rad
            x, y, r = self.x, self.y, self.r
            if (math.sqrt((ex-x)**2+(ey-y)**2)<=er+r):
                WIN.enemies.remove(e)
                if self in WIN.projectiles:
                    WIN.projectiles.remove(self)
class Enemy(Creature):
    height = 24
    rad = 32
    left = pygame.image.load(os.path.join("Assets", "enemy.png"))
    right = pygame.transform.smoothscale(left, (28, 32))
    right = pygame.transform.flip(left, True, False)
    def move_to_player(self):
        if True:
            dif_x = PLAYER.x - self.x
            dif_y = PLAYER.y - self.y
            if dif_x != 0:
                mx = dif_x // abs(dif_x) * 2
                if mx < 0:
                    self.direction = 1
                    self.x += mx
                elif mx > 0:
                    self.direction = -1
                    self.x += mx
            if dif_y != 0:
                my =  dif_y // abs(dif_y) * 2
                if my < 0 or my > 0:
                    self.y += my
        px, py, pr = PLAYER.x, PLAYER.y, PLAYER.w
        x, y, r = self.x, self.y, self.rad
        if (math.sqrt((px-x)**2+(py-y)**2)<=pr+r):
            WIN.enemies.remove(self)
            PLAYER.hp -= 1
def make_text_button(text, font_type, fontsize, colour, x, y):
    font = pygame.font.Font(os.path.join("Assets", font_type+".ttf"), fontsize)
    #w, h = fontsize * 2, fontsize*2
    text = font.render(text, 1, colour)
    w, h = text.get_size()
    rect = pygame.Rect(x - w//2, y - h//2, w, h)
    return text, rect
def meow():
    print("woof")
class Island(pygame.sprite.Sprite):
    def __init__(self, x, y, colour, background, foreground, collision):
        self.colour = colour
        self.x = x
        self.y = y
        pygame.sprite.Sprite.__init__(self)
        self.background = background
        self.foreground = foreground
        self.collision = collision
        w, h = self.collision.get_size()
        self.rect = pygame.Rect(x, y, w, h)
        self.mask = pygame.mask.from_surface(self.collision)

def load_map():
    global PLAYER
    with open("map1.txt", "r") as File:
        string = File.read()
    match = re.findall(r"(-?\d+), (-?\d+)\): (\d)", string)
    #my_map = {}
    WIN.islands = []
    for e in match:
        x, y, index = e
        x, y, index = int(x) * 3, int(y) * 3, int(index)
        #my_map[int(x), int(y)] = int(index)
        back, fore, coll = WIN.images[index]
        WIN.islands.append(Island(x, y, (0, 0, 0), back, fore, coll))
    
    match = re.findall(r"(\d+), (\d+)\): p", string)
    x, y = match[0]
    PLAYER = Player(int(x) * 3, int(y) * 3)
    match = re.findall(r"(\d+), (\d+)\): c", string)
    WIN.kittens = []
    for e in match:
        x, y = e
        WIN.kittens.append(pygame.Rect(int(x) * 3, int(y) * 3, 24, 36))

def restart_game():
    WIN.enemies = []
    main()
def main():
    global WIN
    WIN = Window()
    load_map()
    #enemy = Enemy(PLAYER.x, PLAYER.y)
    #WIN.enemies.append(enemy)
    WIN.run_game()

main()