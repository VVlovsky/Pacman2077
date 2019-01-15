import pygame
from pygame.locals import *
import pyganim
import random
import os.path


BACKGROUND_COLOR = '#120e1f'
BACKGROUND_IMAGE = pygame.image.load('data/final_maze_background.jpg')
MENU_PLAY = pygame.image.load('data/menu/Play.jpg')
MENU_RESET_STORE = pygame.image.load('data/menu/Reset_Store.jpg')
MENU_EXIT = pygame.image.load('data/menu/Exit.jpg')
MENU_CLASSIC = pygame.image.load('data/menu/menu_classic.jpg')
MENU_IR = pygame.image.load('data/menu/menu_ir_b.jpg')
ICON_IMAGE = pygame.image.load('data/pacman.png')

all_images = []
all_images = pyganim.getImagesFromSpriteSheet('data/sprite_sheet.png', cols=16, rows=16, rects=all_images)
for i in range(len(all_images)):
    all_images[i] = pygame.transform.rotate(all_images[i], -90)
frames = list(zip(all_images, [150 if i < 60 else 120 for i in range(256)]))

maze_image = []
maze_image = pyganim.getImagesFromSpriteSheet('data/maze_res.png', cols=24, rows=24, rects=maze_image)

maze_image_add = []
maze_image_add = pyganim.getImagesFromSpriteSheet('data/maze_res_2_1.jpg', cols=24, rows=24, rects=maze_image_add)

animObj = pyganim.PygAnimation(frames)

WIN_WIDTH = 960
WIN_HEIGHT = 1054

pygame.init()
pygame.font.init()
font = pygame.font.Font('data/True Lies.ttf', 30)
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Pacman2077")
pygame.display.set_icon(ICON_IMAGE)
clock = pygame.time.Clock()
SWITCH_SOUND = pygame.mixer.Sound('data/sound_effects/DM-CGS-21.wav')
ENTER_SOUND = pygame.mixer.Sound('data/sound_effects/DM-CGS-48.wav')
SUPER_DOT_SOUND = pygame.mixer.Sound('data/sound_effects/DM-CGS-33.wav')
FRUIT_SOUND = pygame.mixer.Sound('data/sound_effects/DM-CGS-27.wav')
DEATH_SOUND = pygame.mixer.Sound('data/sound_effects/DM-CGS-06.wav')
WIN_SOUND = pygame.mixer.Sound('data/sound_effects/DM-CGS-26.wav')
EAT_ENEMY_SOUND = pygame.mixer.Sound('data/sound_effects/DM-CGS-07.wav')

maze_map = start_map = ["------------------------",
                        "-          --          -",
                        "-X--- ---- -- ---- ---X-",
                        "- --- ---- -- ---- --- -",
                        "-                      -",
                        "- --- - -------- - --- -",
                        "-     -   ----   -     -",
                        "----- --- ---- --- -----",
                        "****- ---*----*--- -****",
                        "****- -**********- -****",
                        "----- -*---__---*- -----",
                        "***** **-******-** *****",
                        "----- -*-******-*- -----",
                        "****- -*--------*- -****",
                        "****- -**********- -****",
                        "----- -*--------*- -----",
                        "-         ----         -",
                        "- --- --- ---- --- --- -",
                        "-X --      **      -- X-",
                        "-- -- - -------- - -- --",
                        "-     -   ----   -     -",
                        "- ------- ---- ------- -",
                        "-                      -",
                        "------------------------"]

x = 460
y = 765
width = 400
height = 20
speed = 10


class Camera(object):
    def __init__(self, camera_func, cls_width, cls_height, maze_left):
        self.camera_func = camera_func
        self.state = Rect(maze_left, 0, cls_width, cls_height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)


def camera_configure(func_camera, target_rect):
    l_of_cam, t_of_cam, _, _ = target_rect
    l_of_cam += 20
    _, _, w_of_cam, h_of_cam = func_camera
    l_of_cam, t_of_cam = -l_of_cam + WIN_WIDTH / 2, -t_of_cam + WIN_HEIGHT / 2

    if not infinity_run:
        l_of_cam = min(0, l_of_cam)
        l_of_cam = max(-(func_camera.width - WIN_WIDTH), l_of_cam)
    t_of_cam = max(-(func_camera.height - WIN_HEIGHT), t_of_cam)
    t_of_cam = min(0, t_of_cam)

    return Rect(l_of_cam, t_of_cam, w_of_cam, h_of_cam)


class Maze(pygame.sprite.Sprite):
    def __init__(self, maze_x, maze_y, cls_image):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((40, 40))

        self.image = cls_image
        self.rect = Rect(maze_x, maze_y, 40, 40)
        self.tag = "Maze"


class MazeRoad(pygame.sprite.Sprite):
    def __init__(self, maze_x, maze_y, cls_image):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((40, 40))

        self.image = cls_image
        self.rect = Rect(maze_x, maze_y, 40, 40)


class Wall(pygame.sprite.Sprite):
    def __init__(self, maze_x, maze_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((40, 40))

        self.image = all_images[213]

        self.rect = Rect(maze_x, maze_y, 40, 40)
        self.tag = "Wall"


class Points:
    def __init__(self, maze_x, maze_y, cls_points):
        self.cls_x = maze_x
        self.cls_y = maze_y - 30
        self.text = font.render(str(cls_points), False, Color("#ffff00"))

    def update(self):
        screen.blit(self.text, (self.cls_x, self.cls_y))


class Pacman(pygame.sprite.Sprite):
    x_speed = 0
    y_speed = 0

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = all_images[251]
        self.rect = all_images[251].get_rect()
        self.anim_right = pyganim.PygAnimation(frames[80:83])
        self.anim_right.play()
        self.anim_left = pyganim.PygAnimation(frames[96:99])
        self.anim_left.play()
        self.anim_bottom = pyganim.PygAnimation(frames[83:86])
        self.anim_bottom.play()
        self.anim_top = pyganim.PygAnimation(frames[99:102])
        self.anim_top.play()
        self.anim_death = pyganim.PygAnimation(frames[112:120] + frames[128:133])
        self.rect.top = y
        self.rect.left = x
        self.move_direction = []
        self.death_check = False
        self.points = 0
        self.life = 3
        self.can_eat_enemies = False
        self.main_speed = 4
        self.collide_right_old = False
        self.collide_left_old = False
        self.collide_up_old = False
        self.collide_down_old = False
        self.eaten_enemies = 0
        self.fruit_number = 0

    def collide(self, func_x, func_y, platforms, func_dots, func_enemies, func_super_dots):
        global points
        global points_time
        global fruits
        global fruits_level
        global fruit_timer
        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                if func_x > 0:
                    self.rect.right = p.rect.left
                    if len(self.move_direction) > 1:
                        self.move_direction.remove('right')
                if func_x < 0:
                    self.rect.left = p.rect.right
                    if len(self.move_direction) > 1:
                        self.move_direction.remove('left')
                if func_y > 0:
                    self.rect.bottom = p.rect.top
                    if len(self.move_direction) > 1:
                        self.move_direction.remove('down')
                if func_y < 0:
                    self.rect.top = p.rect.bottom
                    if len(self.move_direction) > 1:
                        self.move_direction.remove('up')
        for d in func_dots:
            if pygame.sprite.collide_rect(self, d):
                all_sprites.remove(d)
                dots.remove(d)
                self.points += 10
                global play_timer
                play_timer = pygame.time.get_ticks()
                if len(dots) == 90 or len(dots) == 45:
                    fr = Fruit(460, 605, len(fruits) % 6)
                    FRUIT_SOUND.play()
                    all_sprites.add(fr)
                    fruits.append(fr)
                    fruits_level.append(level)
                    fruit_timer.append(pygame.time.get_ticks())
                    self.fruit_number += 1
                    if self.fruit_number == 6:
                        self.fruit_number = 0
                break
        for ens in func_enemies:
            if pygame.sprite.collide_rect(self, ens):
                if not ens.fear and not ens.spirit:
                    self.death_check = True
                    self.anim_death.play()
                    pygame.time.wait(800)
                    DEATH_SOUND.play()
                    break
                else:
                    if not ens.spirit:
                        ens.spirit = True
                        ens.fear = False
                        self.points += 200 * 2 ** self.eaten_enemies
                        points_text = Points(ens.rect.left, ens.rect.top, 200 * 2 ** self.eaten_enemies)
                        points.append(points_text)
                        points_time.append(pygame.time.get_ticks())
                        self.eaten_enemies += 1
                        EAT_ENEMY_SOUND.play()

        for fsd in func_super_dots:
            if pygame.sprite.collide_rect(self, fsd):
                all_sprites.remove(fsd)
                super_dots.remove(fsd)
                self.points += 50

                points_text = Points(fsd.rect.left, fsd.rect.top, 50)
                points.append(points_text)
                points_time.append(pygame.time.get_ticks())
                self.can_eat_enemies = True
                SUPER_DOT_SOUND.play()
                break

        for fr in fruits:
            if pygame.sprite.collide_rect(self, fr):
                fr_points = (100 + 100 * (level - 1)) if (100 + 100 * (level - 1)) < 5000 else 5000
                self.points += fr_points
                FRUIT_SOUND.play()

                points_text = Points(fr.rect.left, fr.rect.top, fr_points)
                points.append(points_text)
                points_time.append(pygame.time.get_ticks())
                fr.rect.top = 1010
                fr.rect.left = 940 - 40 * len(fruits)
                fruit_timer[len(fruits) - 1] = 0

    def check_maze(self, func_maze, func_speed_x, func_speed_y):

        func_collide_y = False
        func_collide_x = False

        self.rect.top += func_speed_y
        for fm in func_maze:
            if pygame.sprite.collide_rect(self, fm):
                func_collide_y = True
                break
        self.rect.top -= func_speed_y

        self.rect.left += func_speed_x
        for fm in func_maze:
            if pygame.sprite.collide_rect(self, fm):
                func_collide_x = True
        self.rect.left -= func_speed_x

        return func_collide_x, func_collide_y

    def update(self, platform, func_enemies):
        self.x_speed = 0
        self.y_speed = 0

        if not self.death_check:

            if len(self.move_direction) > 1:
                if self.move_direction[0] == 'right' and self.move_direction[1] == 'left':
                    self.move_direction.pop(0)
                elif self.move_direction[0] == 'left' and self.move_direction[1] == 'right':
                    self.move_direction.pop(0)
                elif self.move_direction[0] == 'up' and self.move_direction[1] == 'down':
                    self.move_direction.pop(0)
                elif self.move_direction[0] == 'down' and self.move_direction[1] == 'up':
                    self.move_direction.pop(0)

            collide_right, collide_down = self.check_maze(platform, self.main_speed, self.main_speed)
            collide_left, collide_up = self.check_maze(platform, self.main_speed * -1, self.main_speed * -1)

            if self.collide_down_old != collide_down or self.collide_up_old != collide_up \
                    or self.collide_left_old != collide_left or self.collide_right_old != collide_right:
                if len(self.move_direction) > 1:

                    if self.move_direction[1] == 'right' and not collide_right:
                        self.move_direction.pop(0)

                    elif self.move_direction[1] == 'left' and not collide_left:
                        self.move_direction.pop(0)

                    elif self.move_direction[1] == 'down' and not collide_down:
                        self.move_direction.pop(0)

                    elif self.move_direction[1] == 'up' and not collide_up:
                        self.move_direction.pop(0)

                self.collide_up_old = collide_up
                self.collide_down_old = collide_down
                self.collide_left_old = collide_left
                self.collide_right_old = collide_right

            if len(self.move_direction) != 0:
                if self.move_direction[0] == 'right':
                    self.x_speed = self.main_speed
                elif self.move_direction[0] == 'left':
                    self.x_speed = self.main_speed * -1
                elif self.move_direction[0] == 'down':
                    self.y_speed = self.main_speed
                elif self.move_direction[0] == 'up':
                    self.y_speed = self.main_speed * -1

            x_old = self.rect.left
            y_old = self.rect.top
            x_new = x_old + self.x_speed
            y_new = y_old + self.y_speed
            self.rect.left = x_new
            self.collide(self.x_speed, 0, platform, dots, func_enemies, super_dots)
            self.rect.top = y_new
            self.collide(0, self.y_speed, platform, dots, func_enemies, super_dots)

            if self.rect.left >= 960 and not infinity_run:
                self.rect.right = self.main_speed
                self.rect.top = 485

            if self.rect.right <= 0 and not infinity_run:
                self.rect.left = 960 - self.main_speed
                self.rect.top = 485

            if len(self.move_direction) == 0:
                self.image.blit(all_images[87], (0, 0))
                self.anim_right.blit(self.image, (0, 0))

            elif 'right' == self.move_direction[0]:
                self.image.blit(all_images[87], (0, 0))
                self.anim_right.blit(self.image, (0, 0))
            elif 'left' == self.move_direction[0]:
                self.image.blit(all_images[87], (0, 0))

                self.anim_left.blit(self.image, (0, 0))
            elif 'down' == self.move_direction[0]:
                self.image.blit(all_images[87], (0, 0))

                self.anim_bottom.blit(self.image, (0, 0))
            elif 'up' == self.move_direction[0]:
                self.image.blit(all_images[87], (0, 0))

                self.anim_top.blit(self.image, (0, 0))

        else:
            self.image.fill(Color(BACKGROUND_COLOR))

            self.anim_death.blit(self.image, (0, 0))


class Dots(pygame.sprite.Sprite):

    def __init__(self, func_x, func_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = all_images[68]
        self.rect = Rect(func_x, func_y, 40, 40)


class SuperDots(pygame.sprite.Sprite):

    def __init__(self, func_x, func_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = all_images[230]
        self.rect = Rect(func_x, func_y, 40, 40)
        self.anim = pyganim.PygAnimation(frames[86:87] + frames[102:103])
        self.anim.play()

    def update(self, func_maze, func_enemies):
        self.image.blit(all_images[103], (0, 0))
        self.anim.blit(self.image, (0, 0))


class Fruit(pygame.sprite.Sprite):
    def __init__(self, func_x, func_y, number):
        pygame.sprite.Sprite.__init__(self)
        self.image = all_images[144 + number]
        self.rect = Rect(func_x, func_y, 40, 40)


class Red(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = all_images[226]
        self.rect = all_images[226].get_rect()

        self.anim_right = pyganim.PygAnimation(frames[0:2])
        self.anim_right.play()
        self.anim_left = pyganim.PygAnimation(frames[4:6])
        self.anim_left.play()
        self.anim_bottom = pyganim.PygAnimation(frames[2:4])
        self.anim_bottom.play()
        self.anim_top = pyganim.PygAnimation(frames[6:8])
        self.anim_top.play()
        self.anim_fear = pyganim.PygAnimation(frames[194:196])
        self.anim_fear.play()
        self.anim_end_fear = pyganim.PygAnimation(frames[194:198])
        self.anim_end_fear.play()
        self.fear_timer = 0
        self.speed_x = 0
        self.speed_y = 0
        self.rect.left = 460
        self.rect.top = 405
        self.count_collide_x = 0
        self.count_collide_y = 0
        self.collide_right_old = False
        self.collide_left_old = False
        self.collide_up_old = False
        self.collide_down_old = False
        self.start_speed = 2
        self.stop_game = False
        self.fear = False
        self.scatter = False
        self.spirit = False
        self.in_game = True

    def move(self, func_maze, target_x, target_y, func_fear):

        collide_right, collide_down = self.check_maze(func_maze, self.start_speed, self.start_speed)
        collide_left, collide_up = self.check_maze(func_maze, self.start_speed * -1, self.start_speed * -1)

        if self.speed_x != 0:
            if self.speed_x < 0:
                collide_right = True
                self.collide_right_old = True
            else:
                collide_left = True
                self.collide_left_old = True
        if self.speed_y != 0:
            if self.speed_y < 0:
                collide_down = True
                self.collide_down_old = True
            else:
                collide_up = True
                self.collide_up_old = True

        if not self.spirit:
            if not func_fear:
                if not collide_left:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_left.blit(self.image, (0, 0))
                elif not collide_right:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_right.blit(self.image, (0, 0))
                elif not collide_up:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_top.blit(self.image, (0, 0))
                elif not collide_down:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_bottom.blit(self.image, (0, 0))
            else:

                if (pygame.time.get_ticks() - self.fear_timer) / 1000 > 6:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_end_fear.blit(self.image, (0, 0))
                else:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_fear.blit(self.image, (0, 0))

        else:
            self.image.blit(all_images[69], (0, 0))
            if not collide_left:
                self.image.blit(all_images[66], (0, 0))
            elif not collide_right:
                self.image.blit(all_images[64], (0, 0))
            elif not collide_up:
                self.image.blit(all_images[67], (0, 0))
            elif not collide_down:
                self.image.blit(all_images[65], (0, 0))

        if self.collide_down_old != collide_down or self.collide_up_old != collide_up \
                or self.collide_left_old != collide_left or self.collide_right_old != collide_right:
            sides = self.make_prior(target_x, target_y)

            for s in sides:
                if s == 'right' and not collide_right:
                    self.speed_x = self.start_speed
                    self.speed_y = 0

                    break
                if s == 'left' and not collide_left:
                    self.speed_x = self.start_speed * -1
                    self.speed_y = 0

                    break
                if s == 'down' and not collide_down:
                    self.speed_y = self.start_speed
                    self.speed_x = 0

                    break
                if s == 'up' and not collide_up:
                    self.speed_y = self.start_speed * -1
                    self.speed_x = 0

                    break

            self.collide_up_old = collide_up
            self.collide_down_old = collide_down
            self.collide_left_old = collide_left
            self.collide_right_old = collide_right

    def collide_bug_fix(self, func_maze, func_speed_x, func_speed_y):
        for fm in func_maze:
            if pygame.sprite.collide_rect(self, fm) and fm.tag == 'Maze':
                if func_speed_x > 0:
                    self.rect.right = fm.rect.left
                if func_speed_x < 0:
                    self.rect.left = fm.rect.right
                if func_speed_y > 0:
                    self.rect.bottom = fm.rect.top
                if func_speed_y < 0:
                    self.rect.top = fm.rect.bottom

    def update(self, func_maze, target_x, target_y, target_direction):

        if not self.stop_game:
            if not self.in_game:
                self.start_speed = 1
                if infinity_run:
                    self.start_speed = 10
                if self.rect.top != 405:
                    self.speed_y = self.start_speed * -1
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_top.blit(self.image, (0, 0))
                else:
                    self.speed_x = 0
                    self.speed_y = 0
                    self.in_game = True
                    self.start_speed = 2
                    if infinity_run:
                        self.start_speed = 8
            else:
                if not self.spirit:
                    if self.fear:
                        self.move(func_maze, random.randint(0, 960), random.randint(0, 1048), self.fear)
                    elif self.scatter:
                        self.move(func_maze, 940, 0, self.fear)
                    else:
                        self.move(func_maze, target_x, target_y, self.fear)
                else:

                    self.start_speed = 5
                    self.move(func_maze, 460, 405, False)
                    if 505 > self.rect.top >= 405 and self.rect.left == 460:
                        self.speed_x = 0
                        self.speed_y = 5
                    if self.rect.top == 505 and self.rect.left == 460:
                        self.start_speed = 2
                        self.speed_y = 0
                        self.speed_x = 0
                        self.spirit = False
                        self.fear = False
                        self.in_game = False

        else:
            self.speed_x = 0
            self.speed_y = 0

        self.rect.left += self.speed_x
        self.rect.top += self.speed_y

        self.collide_bug_fix(func_maze, self.speed_x, self.speed_y)

        if not infinity_run:
            if self.rect.left >= 960:
                self.rect.right = self.start_speed
                self.rect.top = 485

            if self.rect.right <= 0:
                self.rect.left = 960 - self.start_speed
                self.rect.top = 485

    def make_prior(self, func_target_x, func_target_y):
        side_prior = ['left', 'right', 'down', 'up']
        if abs(self.rect.top - func_target_y) < abs(self.rect.left - func_target_x):
            if self.rect.left - func_target_x < 0:
                if self.rect.top - func_target_y < 0:
                    side_prior[0] = 'right'
                    side_prior[1] = 'down'
                    side_prior[2] = 'left'
                    side_prior[3] = 'up'
                else:
                    side_prior[0] = 'right'
                    side_prior[1] = 'up'
                    side_prior[2] = 'left'
                    side_prior[3] = 'down'

            else:
                if self.rect.top - func_target_y < 0:
                    side_prior[0] = 'left'
                    side_prior[1] = 'down'
                    side_prior[2] = 'right'
                    side_prior[3] = 'up'
                else:
                    side_prior[0] = 'left'
                    side_prior[1] = 'up'
                    side_prior[2] = 'right'
                    side_prior[3] = 'down'
        else:
            if self.rect.left - func_target_x < 0:
                if self.rect.top - func_target_y < 0:
                    side_prior[0] = 'down'
                    side_prior[1] = 'right'
                    side_prior[2] = 'left'
                    side_prior[3] = 'up'
                else:
                    side_prior[0] = 'up'
                    side_prior[1] = 'right'
                    side_prior[2] = 'down'
                    side_prior[3] = 'left'

            else:
                if self.rect.top - func_target_y < 0:
                    side_prior[0] = 'down'
                    side_prior[1] = 'left'
                    side_prior[2] = 'right'
                    side_prior[3] = 'up'
                else:
                    side_prior[0] = 'up'
                    side_prior[1] = 'left'
                    side_prior[2] = 'down'
                    side_prior[3] = 'right'
        return side_prior

    def check_maze(self, func_maze, func_speed_x, func_speed_y):

        func_collide_y = False
        func_collide_x = False

        self.rect.top += func_speed_y
        for fm in func_maze:
            if pygame.sprite.collide_rect(self, fm):
                func_collide_y = True
                break
        self.rect.top -= func_speed_y

        self.rect.left += func_speed_x
        for fm in func_maze:
            if pygame.sprite.collide_rect(self, fm):
                func_collide_x = True
        self.rect.left -= func_speed_x

        return func_collide_x, func_collide_y


class Pink(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = all_images[255]
        self.rect = all_images[255].get_rect()

        self.anim_right = pyganim.PygAnimation(frames[32:34])
        self.anim_right.play()
        self.anim_left = pyganim.PygAnimation(frames[36:38])
        self.anim_left.play()
        self.anim_bottom = pyganim.PygAnimation(frames[34:36])
        self.anim_bottom.play()
        self.anim_top = pyganim.PygAnimation(frames[38:40])
        self.anim_top.play()
        self.anim_fear = pyganim.PygAnimation(frames[194:196])
        self.anim_fear.play()
        self.anim_end_fear = pyganim.PygAnimation(frames[194:198])
        self.anim_end_fear.play()
        self.fear_timer = 0
        self.speed_x = 0
        self.speed_y = 0
        self.rect.left = 460
        self.rect.top = 505
        self.count_collide_x = 0
        self.count_collide_y = 0
        self.collide_right_old = False
        self.collide_left_old = False
        self.collide_up_old = False
        self.collide_down_old = False
        self.in_game = False
        self.start_speed = 2
        self.stop_game = True
        self.fear = False
        self.scatter = True
        self.spirit = False

    def move(self, func_maze, target_x, target_y, func_fear):
        collide_right, collide_down = self.check_maze(func_maze, self.start_speed, self.start_speed)
        collide_left, collide_up = self.check_maze(func_maze, self.start_speed * -1, self.start_speed * -1)
        if self.speed_x != 0:
            if self.speed_x < 0:
                collide_right = True
                self.collide_right_old = True
            else:
                collide_left = True
                self.collide_left_old = True
        if self.speed_y != 0:
            if self.speed_y < 0:
                collide_down = True
                self.collide_down_old = True
            else:
                collide_up = True
                self.collide_up_old = True
        if not self.spirit:
            if not func_fear:
                if not collide_left:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_left.blit(self.image, (0, 0))
                elif not collide_right:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_right.blit(self.image, (0, 0))
                elif not collide_up:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_top.blit(self.image, (0, 0))
                elif not collide_down:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_bottom.blit(self.image, (0, 0))
            else:
                if (pygame.time.get_ticks() - self.fear_timer) / 1000 > 6:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_end_fear.blit(self.image, (0, 0))
                else:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_fear.blit(self.image, (0, 0))
        else:
            self.image.blit(all_images[69], (0, 0))
            if not collide_left:
                self.image.blit(all_images[66], (0, 0))
            elif not collide_right:
                self.image.blit(all_images[64], (0, 0))
            elif not collide_up:
                self.image.blit(all_images[67], (0, 0))
            elif not collide_down:
                self.image.blit(all_images[65], (0, 0))

        if self.collide_down_old != collide_down or self.collide_up_old != collide_up \
                or self.collide_left_old != collide_left or self.collide_right_old != collide_right:
            sides = self.make_prior(target_x, target_y)

            for s in sides:
                if s == 'right' and not collide_right:
                    self.speed_x = self.start_speed
                    self.speed_y = 0

                    break
                if s == 'left' and not collide_left:
                    self.speed_x = self.start_speed * -1
                    self.speed_y = 0

                    break
                if s == 'down' and not collide_down:
                    self.speed_y = self.start_speed
                    self.speed_x = 0

                    break
                if s == 'up' and not collide_up:
                    self.speed_y = self.start_speed * -1
                    self.speed_x = 0

                    break

            self.collide_up_old = collide_up
            self.collide_down_old = collide_down
            self.collide_left_old = collide_left
            self.collide_right_old = collide_right

    def collide_bug_fix(self, func_maze, func_speed_x, func_speed_y):
        for fm in func_maze:
            if pygame.sprite.collide_rect(self, fm) and fm.tag == 'Maze':
                if func_speed_x > 0:
                    self.rect.right = fm.rect.left
                if func_speed_x < 0:
                    self.rect.left = fm.rect.right
                if func_speed_y > 0:
                    self.rect.bottom = fm.rect.top
                if func_speed_y < 0:
                    self.rect.top = fm.rect.bottom

    def update(self, func_maze, target_x, target_y, target_direction):

        if not self.stop_game:
            if not self.in_game:
                self.start_speed = 1
                if infinity_run:
                    self.start_speed = 10
                if self.rect.top != 405:
                    self.speed_y = self.start_speed * -1
                    if not self.fear:
                        self.image.blit(all_images[69], (0, 0))
                        self.anim_top.blit(self.image, (0, 0))
                    else:
                        if (pygame.time.get_ticks() - self.fear_timer) / 1000 > 6:
                            self.image.blit(all_images[69], (0, 0))
                            self.anim_end_fear.blit(self.image, (0, 0))
                        else:
                            self.image.blit(all_images[69], (0, 0))
                            self.anim_fear.blit(self.image, (0, 0))
                else:
                    self.speed_x = 0
                    self.speed_y = 0
                    self.in_game = True
                    self.start_speed = 2
                    if infinity_run:
                        self.start_speed = 8
            else:

                if target_direction == 'up':
                    target_y -= 160
                elif target_direction == 'down':
                    target_y += 160
                elif target_direction == 'left':
                    target_x -= 160
                else:
                    target_x += 160

                if not self.spirit:
                    if self.fear:
                        self.move(func_maze, random.randint(0, 960), random.randint(0, 1048), self.fear)
                    elif self.scatter:
                        self.move(func_maze, 0, 0, self.fear)
                    else:
                        self.move(func_maze, target_x, target_y, self.fear)
                else:

                    self.start_speed = 5
                    self.move(func_maze, 460, 405, False)
                    if 505 > self.rect.top >= 405 and self.rect.left == 460:
                        self.speed_x = 0
                        self.speed_y = 5
                    if self.rect.top == 505 and self.rect.left == 460:
                        self.start_speed = 1
                        self.speed_y = 0
                        self.speed_x = 0
                        self.spirit = False
                        self.fear = False
                        self.in_game = False

            self.rect.left += self.speed_x
            self.rect.top += self.speed_y

            self.collide_bug_fix(func_maze, self.speed_x, self.speed_y)

            if not infinity_run:
                if self.rect.left >= 960:
                    self.rect.right = self.start_speed
                    self.rect.top = 485

                if self.rect.right <= 0:
                    self.rect.left = 960 - self.start_speed
                    self.rect.top = 485
        else:
            self.speed_x = 0
            self.speed_y = 0
            if not self.fear:
                self.image.blit(all_images[69], (0, 0))
                self.anim_right.blit(self.image, (0, 0))
            else:
                if (pygame.time.get_ticks() - self.fear_timer) / 1000 > 6:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_end_fear.blit(self.image, (0, 0))
                else:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_fear.blit(self.image, (0, 0))

    def make_prior(self, func_target_x, func_target_y):
        side_prior = ['left', 'right', 'down', 'up']
        if abs(self.rect.top - func_target_y) < abs(self.rect.left - func_target_x):
            if self.rect.left - func_target_x < 0:
                if self.rect.top - func_target_y < 0:
                    side_prior[0] = 'right'
                    side_prior[1] = 'down'
                    side_prior[2] = 'left'
                    side_prior[3] = 'up'
                else:
                    side_prior[0] = 'right'
                    side_prior[1] = 'up'
                    side_prior[2] = 'left'
                    side_prior[3] = 'down'

            else:
                if self.rect.top - func_target_y < 0:
                    side_prior[0] = 'left'
                    side_prior[1] = 'down'
                    side_prior[2] = 'right'
                    side_prior[3] = 'up'
                else:
                    side_prior[0] = 'left'
                    side_prior[1] = 'up'
                    side_prior[2] = 'right'
                    side_prior[3] = 'down'
        else:
            if self.rect.left - func_target_x < 0:
                if self.rect.top - func_target_y < 0:
                    side_prior[0] = 'down'
                    side_prior[1] = 'right'
                    side_prior[2] = 'left'
                    side_prior[3] = 'up'
                else:
                    side_prior[0] = 'up'
                    side_prior[1] = 'right'
                    side_prior[2] = 'down'
                    side_prior[3] = 'left'

            else:
                if self.rect.top - func_target_y < 0:
                    side_prior[0] = 'down'
                    side_prior[1] = 'left'
                    side_prior[2] = 'right'
                    side_prior[3] = 'up'
                else:
                    side_prior[0] = 'up'
                    side_prior[1] = 'left'
                    side_prior[2] = 'down'
                    side_prior[3] = 'right'
        return side_prior

    def check_maze(self, func_maze, func_speed_x, func_speed_y):

        func_collide_y = False
        func_collide_x = False

        self.rect.top += func_speed_y
        for fm in func_maze:
            if pygame.sprite.collide_rect(self, fm):
                func_collide_y = True
                break
        self.rect.top -= func_speed_y

        self.rect.left += func_speed_x
        for fm in func_maze:
            if pygame.sprite.collide_rect(self, fm):
                func_collide_x = True
        self.rect.left -= func_speed_x

        return func_collide_x, func_collide_y


class Cyan(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = all_images[253]
        self.rect = all_images[253].get_rect()

        self.anim_right = pyganim.PygAnimation(frames[16:18])
        self.anim_right.play()
        self.anim_left = pyganim.PygAnimation(frames[20:22])
        self.anim_left.play()
        self.anim_bottom = pyganim.PygAnimation(frames[18:20])
        self.anim_bottom.play()
        self.anim_top = pyganim.PygAnimation(frames[22:24])
        self.anim_top.play()
        self.anim_fear = pyganim.PygAnimation(frames[194:196])
        self.anim_fear.play()
        self.anim_end_fear = pyganim.PygAnimation(frames[194:198])
        self.anim_end_fear.play()
        self.fear_timer = 0
        self.speed_x = 0
        self.speed_y = 0
        self.rect.left = 390
        self.rect.top = 505
        self.count_collide_x = 0
        self.count_collide_y = 0
        self.collide_right_old = False
        self.collide_left_old = False
        self.collide_up_old = False
        self.collide_down_old = False
        self.in_game = False
        self.start_speed = 2
        self.stop_game = True
        self.fear = False
        self.scatter = True
        self.spirit = False

    def move(self, func_maze, target_x, target_y, func_fear):
        collide_right, collide_down = self.check_maze(func_maze, self.start_speed, self.start_speed)
        collide_left, collide_up = self.check_maze(func_maze, self.start_speed * -1, self.start_speed * -1)
        if self.speed_x != 0:
            if self.speed_x < 0:
                collide_right = True
                self.collide_right_old = True
            else:
                collide_left = True
                self.collide_left_old = True
        if self.speed_y != 0:
            if self.speed_y < 0:
                collide_down = True
                self.collide_down_old = True
            else:
                collide_up = True
                self.collide_up_old = True
        if not self.spirit:
            if not func_fear:
                if not collide_left:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_left.blit(self.image, (0, 0))
                elif not collide_right:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_right.blit(self.image, (0, 0))
                elif not collide_up:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_top.blit(self.image, (0, 0))
                elif not collide_down:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_bottom.blit(self.image, (0, 0))
            else:
                if (pygame.time.get_ticks() - self.fear_timer) / 1000 > 6:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_end_fear.blit(self.image, (0, 0))
                else:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_fear.blit(self.image, (0, 0))
        else:
            self.image.blit(all_images[69], (0, 0))
            if not collide_left:
                self.image.blit(all_images[66], (0, 0))
            elif not collide_right:
                self.image.blit(all_images[64], (0, 0))
            elif not collide_up:
                self.image.blit(all_images[67], (0, 0))
            elif not collide_down:
                self.image.blit(all_images[65], (0, 0))

        if self.collide_down_old != collide_down or self.collide_up_old != collide_up \
                or self.collide_left_old != collide_left or self.collide_right_old != collide_right:
            sides = self.make_prior(target_x, target_y)

            for s in sides:
                if s == 'right' and not collide_right:
                    self.speed_x = self.start_speed
                    self.speed_y = 0

                    break
                if s == 'left' and not collide_left:
                    self.speed_x = self.start_speed * -1
                    self.speed_y = 0

                    break
                if s == 'down' and not collide_down:
                    self.speed_y = self.start_speed
                    self.speed_x = 0

                    break
                if s == 'up' and not collide_up:
                    self.speed_y = self.start_speed * -1
                    self.speed_x = 0

                    break

            self.collide_up_old = collide_up
            self.collide_down_old = collide_down
            self.collide_left_old = collide_left
            self.collide_right_old = collide_right

    def collide_bug_fix(self, func_maze, func_speed_x, func_speed_y):
        for fm in func_maze:
            if pygame.sprite.collide_rect(self, fm) and fm.tag == 'Maze':
                if func_speed_x > 0:
                    self.rect.right = fm.rect.left
                if func_speed_x < 0:
                    self.rect.left = fm.rect.right
                if func_speed_y > 0:
                    self.rect.bottom = fm.rect.top
                if func_speed_y < 0:
                    self.rect.top = fm.rect.bottom

    def update(self, func_maze, target_x, target_y, target_direction):

        if not self.stop_game:
            if not self.in_game:
                self.start_speed = 1
                if infinity_run:
                    self.start_speed = 10
                if self.rect.left != 460:
                    self.speed_x = self.start_speed
                    if not self.fear:
                        self.image.blit(all_images[69], (0, 0))
                        self.anim_right.blit(self.image, (0, 0))
                    else:
                        if (pygame.time.get_ticks() - self.fear_timer) / 1000 > 6:
                            self.image.blit(all_images[69], (0, 0))
                            self.anim_end_fear.blit(self.image, (0, 0))
                        else:
                            self.image.blit(all_images[69], (0, 0))
                            self.anim_fear.blit(self.image, (0, 0))
                elif self.rect.top != 405:
                    self.speed_x = 0
                    self.speed_y = self.start_speed * -1
                    if not self.fear:
                        self.image.blit(all_images[69], (0, 0))
                        self.anim_top.blit(self.image, (0, 0))
                    else:
                        if (pygame.time.get_ticks() - self.fear_timer) / 1000 > 6:
                            self.image.blit(all_images[69], (0, 0))
                            self.anim_end_fear.blit(self.image, (0, 0))
                        else:
                            self.image.blit(all_images[69], (0, 0))
                            self.anim_fear.blit(self.image, (0, 0))
                else:
                    self.speed_x = 0
                    self.speed_y = 0
                    self.in_game = True
                    self.start_speed = 2
                    if infinity_run:
                        self.start_speed = 8
            else:

                if target_direction == 'up':
                    target_y -= 80
                elif target_direction == 'down':
                    target_y += 80
                elif target_direction == 'left':
                    target_x -= 80
                else:
                    target_x += 80

                target_x = target_x + (target_x - self.rect.left)
                target_y = target_y + (target_y - self.rect.top)

                if not self.spirit:
                    if self.fear:
                        self.move(func_maze, random.randint(0, 960), random.randint(0, 1048), self.fear)
                    elif self.scatter:
                        self.move(func_maze, 0, 1054, self.fear)
                    else:
                        self.move(func_maze, target_x, target_y, self.fear)
                else:

                    self.start_speed = 5
                    self.move(func_maze, 460, 405, False)
                    if 505 > self.rect.top >= 405 and self.rect.left == 460:
                        self.speed_x = 0
                        self.speed_y = 5
                    if self.rect.top == 505 and self.rect.left == 460:
                        self.start_speed = 2
                        self.speed_y = 0
                        self.speed_x = 0
                        self.spirit = False
                        self.fear = False
                        self.in_game = False

            self.rect.left += self.speed_x
            self.rect.top += self.speed_y

            self.collide_bug_fix(func_maze, self.speed_x, self.speed_y)

            if not infinity_run:

                if self.rect.left >= 960:
                    self.rect.right = self.start_speed
                    self.rect.top = 485

                if self.rect.right <= 0:
                    self.rect.left = 960 - self.start_speed
                    self.rect.top = 485
        else:
            self.speed_y = 0
            self.speed_x = 0
            if not self.fear:
                self.image.blit(all_images[69], (0, 0))
                self.anim_right.blit(self.image, (0, 0))
            else:
                if (pygame.time.get_ticks() - self.fear_timer) / 1000 > 6:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_end_fear.blit(self.image, (0, 0))
                else:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_fear.blit(self.image, (0, 0))

    def make_prior(self, func_target_x, func_target_y):
        side_prior = ['left', 'right', 'down', 'up']
        if abs(self.rect.top - func_target_y) < abs(self.rect.left - func_target_x):
            if self.rect.left - func_target_x < 0:
                if self.rect.top - func_target_y < 0:
                    side_prior[0] = 'right'
                    side_prior[1] = 'down'
                    side_prior[2] = 'left'
                    side_prior[3] = 'up'
                else:
                    side_prior[0] = 'right'
                    side_prior[1] = 'up'
                    side_prior[2] = 'left'
                    side_prior[3] = 'down'

            else:
                if self.rect.top - func_target_y < 0:
                    side_prior[0] = 'left'
                    side_prior[1] = 'down'
                    side_prior[2] = 'right'
                    side_prior[3] = 'up'
                else:
                    side_prior[0] = 'left'
                    side_prior[1] = 'up'
                    side_prior[2] = 'right'
                    side_prior[3] = 'down'
        else:
            if self.rect.left - func_target_x < 0:
                if self.rect.top - func_target_y < 0:
                    side_prior[0] = 'down'
                    side_prior[1] = 'right'
                    side_prior[2] = 'left'
                    side_prior[3] = 'up'
                else:
                    side_prior[0] = 'up'
                    side_prior[1] = 'right'
                    side_prior[2] = 'down'
                    side_prior[3] = 'left'

            else:
                if self.rect.top - func_target_y < 0:
                    side_prior[0] = 'down'
                    side_prior[1] = 'left'
                    side_prior[2] = 'right'
                    side_prior[3] = 'up'
                else:
                    side_prior[0] = 'up'
                    side_prior[1] = 'left'
                    side_prior[2] = 'down'
                    side_prior[3] = 'right'
        return side_prior

    def check_maze(self, func_maze, func_speed_x, func_speed_y):

        func_collide_y = False
        func_collide_x = False

        self.rect.top += func_speed_y
        for fm in func_maze:
            if pygame.sprite.collide_rect(self, fm):
                func_collide_y = True
                break
        self.rect.top -= func_speed_y

        self.rect.left += func_speed_x
        for fm in func_maze:
            if pygame.sprite.collide_rect(self, fm):
                func_collide_x = True
        self.rect.left -= func_speed_x

        return func_collide_x, func_collide_y


class Orange(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = all_images[254]
        self.rect = all_images[254].get_rect()

        self.anim_right = pyganim.PygAnimation(frames[48:50])
        self.anim_right.play()
        self.anim_left = pyganim.PygAnimation(frames[52:54])
        self.anim_left.play()
        self.anim_bottom = pyganim.PygAnimation(frames[50:52])
        self.anim_bottom.play()
        self.anim_top = pyganim.PygAnimation(frames[54:56])
        self.anim_top.play()
        self.anim_fear = pyganim.PygAnimation(frames[194:196])
        self.anim_fear.play()
        self.anim_end_fear = pyganim.PygAnimation(frames[194:198])
        self.anim_end_fear.play()
        self.fear_timer = 0
        self.speed_x = 0
        self.speed_y = 0
        self.rect.left = 530
        self.rect.top = 505
        self.count_collide_x = 0
        self.count_collide_y = 0
        self.collide_right_old = False
        self.collide_left_old = False
        self.collide_up_old = False
        self.collide_down_old = False
        self.in_game = False
        self.start_speed = 2
        self.stop_game = True
        self.fear = False
        self.scatter = True
        self.spirit = False

    def move(self, func_maze, target_x, target_y, func_fear):
        collide_right, collide_down = self.check_maze(func_maze, self.start_speed, self.start_speed)
        collide_left, collide_up = self.check_maze(func_maze, self.start_speed * -1, self.start_speed * -1)
        if self.speed_x != 0:
            if self.speed_x < 0:
                collide_right = True
                self.collide_right_old = True
            else:
                collide_left = True
                self.collide_left_old = True
        if self.speed_y != 0:
            if self.speed_y < 0:
                collide_down = True
                self.collide_down_old = True
            else:
                collide_up = True
                self.collide_up_old = True
        if not self.spirit:
            if not func_fear:
                if not collide_left:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_left.blit(self.image, (0, 0))
                elif not collide_right:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_right.blit(self.image, (0, 0))
                elif not collide_up:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_top.blit(self.image, (0, 0))
                elif not collide_down:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_bottom.blit(self.image, (0, 0))
            else:
                if (pygame.time.get_ticks() - self.fear_timer) / 1000 > 6:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_end_fear.blit(self.image, (0, 0))
                else:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_fear.blit(self.image, (0, 0))
        else:
            self.image.blit(all_images[69], (0, 0))
            if not collide_left:
                self.image.blit(all_images[66], (0, 0))
            elif not collide_right:
                self.image.blit(all_images[64], (0, 0))
            elif not collide_up:
                self.image.blit(all_images[67], (0, 0))
            elif not collide_down:
                self.image.blit(all_images[65], (0, 0))

        if self.collide_down_old != collide_down or self.collide_up_old != collide_up \
                or self.collide_left_old != collide_left or self.collide_right_old != collide_right:
            sides = self.make_prior(target_x, target_y)

            for s in sides:
                if s == 'right' and not collide_right:
                    self.speed_x = self.start_speed
                    self.speed_y = 0

                    break
                if s == 'left' and not collide_left:
                    self.speed_x = self.start_speed * -1
                    self.speed_y = 0

                    break
                if s == 'down' and not collide_down:
                    self.speed_y = self.start_speed
                    self.speed_x = 0

                    break
                if s == 'up' and not collide_up:
                    self.speed_y = self.start_speed * -1
                    self.speed_x = 0

                    break

            self.collide_up_old = collide_up
            self.collide_down_old = collide_down
            self.collide_left_old = collide_left
            self.collide_right_old = collide_right

    def collide_bug_fix(self, func_maze, func_speed_x, func_speed_y):
        for fm in func_maze:
            if pygame.sprite.collide_rect(self, fm) and fm.tag == 'Maze':
                if func_speed_x > 0:
                    self.rect.right = fm.rect.left
                if func_speed_x < 0:
                    self.rect.left = fm.rect.right
                if func_speed_y > 0:
                    self.rect.bottom = fm.rect.top
                if func_speed_y < 0:
                    self.rect.top = fm.rect.bottom

    def update(self, func_maze, target_x, target_y, target_direction):

        if not self.stop_game:
            if not self.in_game:
                self.start_speed = 1
                if infinity_run:
                    self.start_speed = 10
                if self.rect.left != 460:
                    self.speed_x = self.start_speed * -1
                    if not self.fear:
                        self.image.blit(all_images[69], (0, 0))
                        self.anim_left.blit(self.image, (0, 0))
                    else:
                        if (pygame.time.get_ticks() - self.fear_timer) / 1000 > 6:
                            self.image.blit(all_images[69], (0, 0))
                            self.anim_end_fear.blit(self.image, (0, 0))
                        else:
                            self.image.blit(all_images[69], (0, 0))
                            self.anim_fear.blit(self.image, (0, 0))
                elif self.rect.top != 405:
                    self.speed_x = 0
                    self.speed_y = self.start_speed * -1
                    if not self.fear:
                        self.image.blit(all_images[69], (0, 0))
                        self.anim_top.blit(self.image, (0, 0))
                    else:
                        if (pygame.time.get_ticks() - self.fear_timer) / 1000 > 6:
                            self.image.blit(all_images[69], (0, 0))
                            self.anim_end_fear.blit(self.image, (0, 0))
                        else:
                            self.image.blit(all_images[69], (0, 0))
                            self.anim_fear.blit(self.image, (0, 0))
                else:
                    self.speed_x = 0
                    self.speed_y = 0
                    self.in_game = True
                    self.start_speed = 2
                    if infinity_run:
                        self.start_speed = 8
            else:

                if abs(self.rect.left - target_x) + abs(self.rect.top - target_y) < 320:
                    target_x = 0
                    target_y = 1054
                if not self.spirit:
                    if self.fear:
                        self.move(func_maze, random.randint(0, 960), random.randint(0, 1048), self.fear)
                    elif self.scatter:
                        self.move(func_maze, 940, 1054, self.fear)
                    else:
                        self.move(func_maze, target_x, target_y, self.fear)
                else:

                    self.start_speed = 5
                    self.move(func_maze, 460, 405, False)
                    if 505 > self.rect.top >= 405 and self.rect.left == 460:
                        self.speed_x = 0
                        self.speed_y = 5
                    if self.rect.top == 505 and self.rect.left == 460:
                        self.start_speed = 2
                        self.speed_y = 0
                        self.speed_x = 0
                        self.spirit = False
                        self.fear = False
                        self.in_game = False

            self.rect.left += self.speed_x
            self.rect.top += self.speed_y
            if not infinity_run:

                if self.rect.left >= 960:
                    self.rect.right = self.start_speed
                    self.rect.top = 485

                if self.rect.right <= 0:
                    self.rect.left = 960 - self.start_speed
                    self.rect.top = 485

            self.collide_bug_fix(func_maze, self.speed_x, self.speed_y)

        else:
            self.speed_x = 0
            self.speed_y = 0

            if not self.fear:
                self.image.blit(all_images[69], (0, 0))
                self.anim_right.blit(self.image, (0, 0))
            else:
                if (pygame.time.get_ticks() - self.fear_timer) / 1000 > 6:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_end_fear.blit(self.image, (0, 0))
                else:
                    self.image.blit(all_images[69], (0, 0))
                    self.anim_fear.blit(self.image, (0, 0))

    def make_prior(self, func_target_x, func_target_y):
        side_prior = ['left', 'right', 'down', 'up']
        if abs(self.rect.top - func_target_y) < abs(self.rect.left - func_target_x):
            if self.rect.left - func_target_x < 0:
                if self.rect.top - func_target_y < 0:
                    side_prior[0] = 'right'
                    side_prior[1] = 'down'
                    side_prior[2] = 'left'
                    side_prior[3] = 'up'
                else:
                    side_prior[0] = 'right'
                    side_prior[1] = 'up'
                    side_prior[2] = 'left'
                    side_prior[3] = 'down'

            else:
                if self.rect.top - func_target_y < 0:
                    side_prior[0] = 'left'
                    side_prior[1] = 'down'
                    side_prior[2] = 'right'
                    side_prior[3] = 'up'
                else:
                    side_prior[0] = 'left'
                    side_prior[1] = 'up'
                    side_prior[2] = 'right'
                    side_prior[3] = 'down'
        else:
            if self.rect.left - func_target_x < 0:
                if self.rect.top - func_target_y < 0:
                    side_prior[0] = 'down'
                    side_prior[1] = 'right'
                    side_prior[2] = 'left'
                    side_prior[3] = 'up'
                else:
                    side_prior[0] = 'up'
                    side_prior[1] = 'right'
                    side_prior[2] = 'down'
                    side_prior[3] = 'left'

            else:
                if self.rect.top - func_target_y < 0:
                    side_prior[0] = 'down'
                    side_prior[1] = 'left'
                    side_prior[2] = 'right'
                    side_prior[3] = 'up'
                else:
                    side_prior[0] = 'up'
                    side_prior[1] = 'left'
                    side_prior[2] = 'down'
                    side_prior[3] = 'right'
        return side_prior

    def check_maze(self, func_maze, func_speed_x, func_speed_y):

        func_collide_y = False
        func_collide_x = False

        self.rect.top += func_speed_y
        for fm in func_maze:
            if pygame.sprite.collide_rect(self, fm):
                func_collide_y = True
                break
        self.rect.top -= func_speed_y

        self.rect.left += func_speed_x
        for fm in func_maze:
            if pygame.sprite.collide_rect(self, fm):
                func_collide_x = True
        self.rect.left -= func_speed_x

        return func_collide_x, func_collide_y


def maze_gen(func_maze_map):
    start_configuration = []
    new_map = []
    for row in func_maze_map:
        start_configuration.append(row[-1])

    new_map.append(['X' for _ in range(25)])

    for i in range(1, len(start_configuration) - 1):

        new_str = []

        if start_configuration[i] == '-':
            new_str.append('X')
        else:
            new_str.append(' ')

        new_map.append(new_str)

    start_index = 0
    amount_of_blocks = 6
    stop_temp = 0
    for iii in range(4):
        for i in range(1, len(new_map)):
            if new_map[i - 1][start_index + 1] == new_map[i - 1][start_index + 0] == 'X' and new_map[i][
                    start_index + 0] == ' ':
                for temp in range(1, amount_of_blocks + 1):
                    if new_map[i - 1][start_index + temp] == ' ':
                        break
                    stop_temp = temp + 1
                if stop_temp == amount_of_blocks + 1:
                    gen_rand = random.randint(2, amount_of_blocks)
                    for ii in range(gen_rand):
                        new_map[i].append(' ')
                    for ii in range(amount_of_blocks - gen_rand):
                        new_map[i].append('X')
            elif new_map[i - 1][start_index + 1] == new_map[i - 1][start_index + 0] == new_map[i][
                    start_index + 0] == ' ':
                stop_temp = 0
                for temp in range(1, amount_of_blocks + 1):
                    if new_map[i - 1][start_index + temp] == 'X':
                        break
                    stop_temp = temp - 1

                for ii in range(stop_temp):
                    new_map[i].append('X')
                for ii in range(amount_of_blocks - stop_temp):
                    new_map[i].append(' ')
            elif new_map[i - 1][start_index + 0] == new_map[i][start_index + 0] == ' ' and new_map[i - 1][
                    start_index + 1] == 'X':
                for temp in range(1, amount_of_blocks + 1):
                    if new_map[i - 1][start_index + temp] == ' ':
                        break
                    stop_temp = temp
                if stop_temp == 4:
                    for ii in range(amount_of_blocks):
                        new_map[i].append(' ')
                else:
                    gen_rand = random.randint(1, stop_temp)
                    for ii in range(gen_rand):
                        new_map[i].append(' ')
                    for ii in range(amount_of_blocks - gen_rand):
                        new_map[i].append('X')
            elif new_map[i - 1][start_index + 1] == new_map[i - 1][start_index + 0] == new_map[i][
                    start_index + 0] == 'X':
                gen_rand = random.randint(0, amount_of_blocks)
                for ii in range(gen_rand):
                    new_map[i].append(' ')
                for ii in range(amount_of_blocks - gen_rand):
                    new_map[i].append('X')
            elif new_map[i - 1][start_index + 1] == new_map[i - 1][start_index + 0] == 'X' and new_map[i][
                    start_index + 0] == ' ':
                if new_map[i + 1][start_index] == 'X':
                    gen_rand = random.randint(1, amount_of_blocks)
                    for ii in range(gen_rand):
                        new_map[i].append(' ')
                    for ii in range(amount_of_blocks - gen_rand):
                        new_map[i].append('X')
                else:
                    gen_rand = random.randint(0, amount_of_blocks)
                    for ii in range(gen_rand):
                        new_map[i].append(' ')
                    for ii in range(amount_of_blocks - gen_rand):
                        new_map[i].append('X')
            elif new_map[i - 1][start_index + 1] == new_map[i][start_index + 0] == ' ' and new_map[i - 1][
                    start_index + 0] == 'X':
                for temp in range(1, amount_of_blocks + 1):
                    if new_map[i - 1][start_index + temp] == 'X':
                        break
                    stop_temp = temp - 1
                if stop_temp == 0:
                    for temp in range(1, amount_of_blocks + 1):
                        if new_map[i - 1][start_index + temp] == ' ':
                            break
                        stop_temp = temp - 1
                    for ii in range(stop_temp + 2):
                        new_map[i].append(' ')
                    for ii in range(amount_of_blocks - 2 - stop_temp):
                        new_map[i].append('X')

                else:

                    new_map[i].append(' ')
                    if stop_temp - 1 == 0:
                        new_map[i - 1][start_index + 2] = 'X'

                    for ii in range(stop_temp - 1):
                        new_map[i].append('X')
                    for ii in range(amount_of_blocks - stop_temp):
                        new_map[i].append(' ')
            elif new_map[i - 1][start_index + 1] == new_map[i - 1][start_index + 0] == ' ' and new_map[i][
                    start_index + 0] == 'X':
                for temp in range(1, amount_of_blocks + 1):
                    if new_map[i - 1][start_index + temp] == 'X':
                        break
                    stop_temp = temp - 1
                if stop_temp == 0:
                    for temp in range(1, amount_of_blocks + 1):
                        if new_map[i - 1][start_index + temp] == ' ':
                            break
                        stop_temp = temp + 1
                    if stop_temp == amount_of_blocks + 1:
                        gen_rand = random.randint(1, amount_of_blocks)
                        for ii in range(gen_rand):
                            new_map[i].append(' ')
                        for ii in range(amount_of_blocks - gen_rand):
                            new_map[i].append('X')
                    else:
                        for ii in range(stop_temp):
                            new_map[i].append(' ')
                        for ii in range(amount_of_blocks - stop_temp):
                            new_map[i].append('X')

                else:
                    if stop_temp - 1 == 0:
                        new_map[i - 1][start_index + 2] = 'X'
                    new_map[i].append(' ')
                    for ii in range(stop_temp - 1):
                        new_map[i].append('X')
                    for ii in range(amount_of_blocks - 1 - stop_temp + 1):
                        new_map[i].append(' ')
            elif new_map[i - 1][start_index + 0] == ' ' and new_map[i][start_index + 0] == new_map[i - 1][
                    start_index + 1] == 'X':
                for temp in range(1, amount_of_blocks + 1):
                    if new_map[i - 1][start_index + temp] == ' ':
                        break
                    stop_temp = temp
                for ii in range(stop_temp + 1):
                    new_map[i].append(' ')
                for ii in range(amount_of_blocks - stop_temp - 1):
                    new_map[i].append('X')
            elif new_map[i - 1][start_index + 1] == ' ' and new_map[i][start_index + 0] == new_map[i - 1][
                    start_index + 0] == 'X':
                for temp in range(1, amount_of_blocks + 1):
                    if new_map[i - 1][start_index + temp] == 'X':
                        break
                    stop_temp = temp + 1
                if stop_temp == amount_of_blocks + 1:
                    gen_rand = random.randint(0, 1)
                    if gen_rand == 1:
                        for ii in range(1):
                            new_map[i].append(' ')
                        for ii in range(amount_of_blocks - 1):
                            new_map[i].append('X')
                    else:
                        for ii in range(amount_of_blocks):
                            new_map[i].append('X')
                else:
                    new_map[i].append(' ')
                    if stop_temp == 2:
                        gen_rand = random.randint(0, amount_of_blocks - 1)
                        for ii in range(gen_rand):
                            new_map[i].append(' ')
                        for ii in range(amount_of_blocks - 1 - gen_rand):
                            new_map[i].append('X')
                    else:
                        gen_rand = random.randint(0, amount_of_blocks - 1)
                        for ii in range(gen_rand):
                            new_map[i].append('X')
                        for ii in range(amount_of_blocks - 1 - gen_rand):
                            new_map[i].append(' ')

            else:
                for ii in range(6):
                    new_map[i].append('-')

        start_index += amount_of_blocks

    new_map.append(['X' for _ in range(25)])

    is_not_good = True
    while is_not_good:
        is_not_good = False
        for row in range(1, 22):
            for col in range(0, 22):
                if new_map[row][col] == new_map[row][col + 1] == new_map[row + 1][col] == new_map[row + 1][
                        col + 1] == ' ':
                    is_not_good = True
                    new_map[row + 1][col] = 'X'
                    if row != 21:
                        new_map[row + 2][col + 1] = ' '
                        new_map[row + 2][col - 1] = ' '

    is_not_good = True
    while is_not_good:
        is_not_good = False
        for row in range(1, 23):
            for col in range(0, 22):
                if new_map[row][col] == ' ' and new_map[row - 1][col] == new_map[row + 1][col] == new_map[row][
                    col + 1] == new_map[row][
                        col - 1] == 'X':
                    is_not_good = True
                    new_map[row][col] = 'X'

    map_for_return = []
    for row in range(len(new_map)):
        map_for_return.append('')
        for col in range(len(new_map[row]) - 1):
            if new_map[row][col] == 'X':
                map_for_return[row] += '-'
            else:
                map_for_return[row] += ' '

    return map_for_return


def update_all(enemies_exist):
    camera.update(pacman)
    for a_s in all_sprites:
        if a_s == pacman:
            continue
        screen.blit(a_s.image, camera.apply(a_s))
    screen.blit(pacman.image, camera.apply(pacman))

    if enemies_exist:
        if len(pacman.move_direction) != 0:
            enemies.update(maze, pacman.rect.left, pacman.rect.top, pacman.move_direction[0])
        else:
            enemies.update(maze, pacman.rect.left, pacman.rect.top, 'right')

        for e in enemies:
            screen.blit(e.image, camera.apply(e))

    if len(points) > 0:
        for p in points:
            p.update()
        if (pygame.time.get_ticks() - points_time[0]) / 1000 > 2:
            del points[0]
            points_time.pop(0)

    pygame.display.update()


all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
maze = []
dots = []
super_dots = []
points = []
points_time = []
fruits = []
fruits_level = []
fruit_timer = []
maze_road = []


def make_maze(func_maze_map_local, pf_x_zero=0):
    pf_y = 45
    pf_x = pf_x_zero
    element_index_y = 0
    for row in func_maze_map_local:
        element_index_x = 0
        for col in row:
            if col == "-":
                pf = Maze(pf_x, pf_y,
                          texture(func_maze_map_local, element_index_x, element_index_y) if infinity_run else
                          all_images[214])
                all_sprites.add(pf)
                maze.append(pf)
            if col == " ":
                dt = Dots(pf_x, pf_y)
                mr = MazeRoad(pf_x, pf_y,
                              texture(func_maze_map_local, element_index_x, element_index_y) if infinity_run else
                              all_images[214])
                all_sprites.add(mr)
                all_sprites.add(dt)
                dots.append(dt)
                maze_road.append(mr)
            if col == "_":
                wl = Wall(pf_x, pf_y)
                mr = MazeRoad(pf_x, pf_y,
                              texture(func_maze_map_local, element_index_x, element_index_y) if infinity_run else
                              all_images[214])
                all_sprites.add(mr)
                all_sprites.add(wl)
                maze.append(wl)
                maze_road.append(mr)
            if col == 'X':
                sd = SuperDots(pf_x, pf_y)
                mr = MazeRoad(pf_x, pf_y,
                              texture(func_maze_map_local, element_index_x, element_index_y) if infinity_run else
                              all_images[214])
                all_sprites.add(mr)
                all_sprites.add(sd)
                super_dots.append(sd)
                maze_road.append(mr)
            element_index_x += 1
            pf_x += 40
        element_index_y += 1
        pf_y += 40
        pf_x = pf_x_zero


def texture(func_maze_map, element_index_x, element_index_y):
    for line in range(24):
        func_maze_map[line] = func_maze_map[line].replace('*', ' ')
        func_maze_map[line] = func_maze_map[line].replace('X', ' ')

    example_map = ["------------------------",
                   "-          --          -",
                   "- --- ---- -- ---- --- -",
                   "- --- ---- -- ---- --- -",
                   "-                      -",
                   "- --- - -------- - --- -",
                   "-     -   ----   -     -",
                   "----- --- ---- --- -----",
                   "    - --- ---- --- -    ",
                   "    - -          - -    ",
                   "----- - ---__--- - -----",
                   "        -      -        ",
                   "----- - -      - - -----",
                   "    - - -------- - -    ",
                   "    - -          - -    ",
                   "----- - -------- - -----",
                   "-         ----         -",
                   "- --- --- ---- --- --- -",
                   "-  --              --  -",
                   "-- -- - -------- - -- --",
                   "-     -   ----   -     -",
                   "- ------- ---- ------- -",
                   "-                      -",
                   "------------------------"]

    last_el_x = len(func_maze_map[0]) - 1
    last_el_y = len(func_maze_map) - 1

    if func_maze_map[element_index_y][element_index_x] == '_':
        return maze_image[252]

    if (element_index_y == last_el_y and element_index_x != last_el_x and element_index_x != 0) or (
            element_index_y == 0 and element_index_x != last_el_x and element_index_x != 0):
        if element_index_y == 0 and func_maze_map[element_index_y + 1][element_index_x] == ' ':
            return maze_image[3]
        elif element_index_y == 0:
            return maze_image[12]
        if element_index_y == last_el_y and func_maze_map[element_index_y - 1][element_index_x] == ' ':
            return maze_image[3]

    if element_index_x != last_el_x and element_index_y != last_el_y and element_index_x != 0:
        for func_row in range(1, 23):
            for func_col in range(1, 23):
                if example_map[func_row][func_col] == func_maze_map[element_index_y][element_index_x] and \
                        example_map[func_row][
                                func_col + 1] == \
                        func_maze_map[element_index_y][element_index_x + 1] and example_map[func_row + 1][func_col] == \
                        func_maze_map[element_index_y + 1][element_index_x] and \
                        example_map[func_row][
                                func_col - 1] == func_maze_map[element_index_y][element_index_x - 1] and \
                        example_map[func_row - 1][func_col] == func_maze_map[element_index_y - 1][element_index_x] and \
                        example_map[func_row + 1][func_col - 1] == func_maze_map[element_index_y + 1][
                    element_index_x - 1] and example_map[func_row - 1][func_col + 1] == \
                        func_maze_map[element_index_y - 1][element_index_x + 1] and example_map[func_row + 1][
                    func_col + 1] == func_maze_map[element_index_y + 1][element_index_x + 1] and \
                        example_map[func_row - 1][func_col - 1] == func_maze_map[element_index_y - 1][
                        element_index_x - 1]:
                    return maze_image[func_row * 24 + func_col]

        for func_row in range(1, 23):
            for func_col in range(1, 23):
                if example_map[func_row][func_col] == func_maze_map[element_index_y][element_index_x] and \
                        example_map[func_row][
                            func_col + 1] == \
                        func_maze_map[element_index_y][element_index_x + 1] and example_map[func_row + 1][func_col] == \
                        func_maze_map[element_index_y + 1][element_index_x] and \
                        example_map[func_row][
                            func_col - 1] == func_maze_map[element_index_y][element_index_x - 1] and \
                        example_map[func_row - 1][func_col] == func_maze_map[element_index_y - 1][element_index_x]:
                    return maze_image[func_row * 24 + func_col]
        if func_maze_map[element_index_y][element_index_x] == func_maze_map[element_index_y][
            element_index_x - 1] == ' ' and func_maze_map[element_index_y][element_index_x + 1] == \
                func_maze_map[element_index_y - 1][element_index_x] == func_maze_map[element_index_y + 1][
                element_index_x] == '-':
            return maze_image_add[34]
        if func_maze_map[element_index_y][element_index_x] == func_maze_map[element_index_y][
            element_index_x + 1] == ' ' and func_maze_map[element_index_y][element_index_x - 1] == \
                func_maze_map[element_index_y - 1][element_index_x] == func_maze_map[element_index_y + 1][
                element_index_x] == '-':
            return maze_image_add[25]
        if func_maze_map[element_index_y][element_index_x] == func_maze_map[element_index_y + 1][
            element_index_x] == ' ' and func_maze_map[element_index_y][element_index_x + 1] == \
                func_maze_map[element_index_y - 1][element_index_x] == func_maze_map[element_index_y][
                element_index_x - 1] == '-':
            return maze_image_add[28]
        if func_maze_map[element_index_y][element_index_x] == func_maze_map[element_index_y - 1][
            element_index_x] == ' ' and func_maze_map[element_index_y][element_index_x + 1] == \
                func_maze_map[element_index_y][element_index_x - 1] == func_maze_map[element_index_y + 1][
                element_index_x] == '-':
            return maze_image_add[31]
        if func_maze_map[element_index_y][element_index_x] == '-' and func_maze_map[element_index_y + 1][
            element_index_x] == func_maze_map[element_index_y - 1][element_index_x] == func_maze_map[element_index_y][
                element_index_x + 1] == func_maze_map[element_index_y][element_index_x - 1] == ' ':
            return maze_image_add[37]
    elif element_index_x == last_el_x and element_index_y != last_el_y:
        for func_row in range(23):
            for func_col in range(1, 24):
                if example_map[func_row][func_col] == func_maze_map[element_index_y][element_index_x] and \
                        example_map[func_row][
                            func_col - 1] == \
                        func_maze_map[element_index_y][element_index_x - 1] and example_map[func_row + 1][func_col] == \
                        func_maze_map[element_index_y + 1][element_index_x] and example_map[func_row + 1][
                    func_col - 1] == \
                        func_maze_map[element_index_y + 1][element_index_x - 1]:
                    return maze_image[func_row * 24 + func_col]
    elif element_index_x != last_el_x and element_index_y == last_el_y:
        for func_row in range(1, 24):
            for func_col in range(23):
                if example_map[func_row][func_col] == func_maze_map[element_index_y][element_index_x] and \
                        example_map[func_row][
                            func_col + 1] == \
                        func_maze_map[element_index_y][element_index_x + 1] and example_map[func_row - 1][func_col] == \
                        func_maze_map[element_index_y - 1][element_index_x] and example_map[func_row - 1][
                    func_col + 1] == \
                        func_maze_map[element_index_y - 1][element_index_x + 1] and example_map[func_row][
                        func_col - 1] == func_maze_map[element_index_y][element_index_x - 1]:
                    return maze_image[func_row * 24 + func_col]
    elif element_index_x == last_el_x and element_index_y == last_el_y:
        for func_row in range(1, 24):
            for func_col in range(1, 24):
                if example_map[func_row][func_col] == func_maze_map[element_index_y][element_index_x] and \
                        example_map[func_row][
                            func_col - 1] == \
                        func_maze_map[element_index_y][element_index_x - 1] and example_map[func_row - 1][func_col] == \
                        func_maze_map[element_index_y - 1][element_index_x] and example_map[func_row - 1][
                    func_col - 1] == \
                        func_maze_map[element_index_y - 1][element_index_x - 1] and example_map[func_row][
                        func_col - 1] == func_maze_map[element_index_y][element_index_x - 1]:
                    return maze_image[func_row * 24 + func_col]

    return maze_image[0]


def restart_game():
    del pacman, all_sprites, red, pink, cyan, orange, enemies, camera


start_death_ticks = 0
pacman_life = 2
saved_points = 0
level = 1
fear_start_time = 0
pacman_old_rect_left = 0

game_on = True
run = True
play_game = True
infinity_run = False
menu = True
select_game_type_classic = False
select_game_type_ir = False
last_played = ""
switch = 1

make_maze(maze_map)
pacman = Pacman()
all_sprites.add(pacman)
red = Red()
enemies.add(red)
pink = Pink()
enemies.add(pink)
cyan = Cyan()
enemies.add(cyan)
orange = Orange()
enemies.add(orange)

if not os.path.isfile('data/high_score'):
    tmp_file = open('data/high_score', 'w')
    tmp_file.write('0')
    tmp_file.close()

high_score_file = open('data/high_score', 'r')
high_score = int(high_score_file.read())
high_score_file.close()

now_map = []
prev_map = []
next_map = []

camera = Camera(camera_configure, len(maze_map[0]) * 40, len(maze_map) * 40, pacman.rect.left - 460 - 960)

while game_on:
    pygame.mixer.music.load('data/Archive - Bullet.mp3')
    pygame.mixer.music.play(-1)
    while menu:
        if switch == 1:
            screen.blit(MENU_PLAY, (0, 0))
        elif switch == 2:
            screen.blit(MENU_RESET_STORE, (0, 0))
        elif switch == 3:
            screen.blit(MENU_EXIT, (0, 0))
        elif select_game_type_classic:
            screen.blit(MENU_CLASSIC, (0, 0))
        elif select_game_type_ir:
            screen.blit(MENU_IR, (0, 0))

        if not select_game_type_ir and not select_game_type_classic:
            high_score_text = font.render(str(high_score), False, Color("#ffff00"))
            high_score_text_shadow = font.render(str(high_score), False, Color("#000000"))
            screen.blit(high_score_text_shadow, (307, 985))
            screen.blit(high_score_text, (300, 990))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_on = False
                menu = False
                run = False

            if event.type == KEYDOWN:
                if event.key == K_UP or event.key == K_w:
                    if not select_game_type_ir and not select_game_type_classic:
                        switch -= 1
                    elif select_game_type_classic:
                        select_game_type_classic = False
                        select_game_type_ir = True
                    elif select_game_type_ir:
                        select_game_type_ir = False
                        select_game_type_classic = True
                    SWITCH_SOUND.play()
                elif event.key == K_DOWN or event.key == K_s:
                    if not select_game_type_ir and not select_game_type_classic:
                        switch += 1
                    elif select_game_type_classic:
                        select_game_type_classic = False
                        select_game_type_ir = True
                    elif select_game_type_ir:
                        select_game_type_ir = False
                        select_game_type_classic = True
                    SWITCH_SOUND.play()

                elif event.key == K_RETURN:
                    if switch == 1:
                        select_game_type_classic = True
                        select_game_type_ir = False
                        switch = 5
                    elif switch == 2:
                        high_score_file = open('data/high_score', 'w')
                        high_score_file.write('0')
                        high_score_file.close()
                        high_score_file = open('data/high_score', 'r')
                        high_score = int(high_score_file.read())
                        high_score_file.close()
                    elif switch == 3:
                        menu = False
                        game_on = False
                    elif select_game_type_classic:
                        if last_played == "ir":
                            pacman_life = -1
                        last_played = "classic"
                        infinity_run = False
                        menu = False
                        play_game = True
                        run = True
                        if pacman_life < 0:
                            saved_points = 0
                            pacman_life = 2
                            pacman.points = 0
                            level = 1
                            while len(maze) != 0:
                                all_sprites.remove(maze[0])
                                del maze[0]
                            while len(maze_road) != 0:
                                all_sprites.remove(maze_road[0])
                                del maze_road[0]
                            while len(dots) != 0:
                                all_sprites.remove(dots[0])
                                del dots[0]
                            for en in enemies:
                                enemies.remove(en)
                            del red, pink, orange, cyan, enemies
                            update_all(False)
                            enemies = pygame.sprite.Group()
                            red = Red()
                            enemies.add(red)
                            pink = Pink()
                            enemies.add(pink)
                            cyan = Cyan()
                            enemies.add(cyan)
                            orange = Orange()
                            enemies.add(orange)
                            all_sprites.remove(pacman)
                            del pacman
                            all_images = []
                            all_images = pyganim.getImagesFromSpriteSheet('data/sprite_sheet.png', cols=16, rows=16,
                                                                          rects=all_images)
                            for i in range(len(all_images)):
                                all_images[i] = pygame.transform.rotate(all_images[i], -90)
                            frames = list(zip(all_images, [150 if i < 60 else 120 for i in range(256)]))
                            pacman = Pacman()
                            all_sprites.add(pacman)
                            pacman.points = saved_points
                            all_sprites.update(maze, enemies)
                            new_lvl = True
                            make_maze(start_map)
                    elif select_game_type_ir:
                        if last_played == "classic":
                            pacman_life = -1
                        last_played = "ir"
                        infinity_run = True
                        menu = False
                        play_game = True
                        run = True

                        if pacman_life < 0:
                            saved_points = 0
                            pacman_life = 0
                            pacman.points = 0
                            level = 1
                            while len(maze) != 0:
                                all_sprites.remove(maze[0])
                                del maze[0]
                            while len(maze_road) != 0:
                                all_sprites.remove(maze_road[0])
                                del maze_road[0]
                            while len(dots) != 0:
                                all_sprites.remove(dots[0])
                                del dots[0]
                            for en in enemies:
                                enemies.remove(en)
                            del red, pink, orange, cyan, enemies
                            update_all(False)
                            enemies = pygame.sprite.Group()
                            red = Red()
                            enemies.add(red)
                            pink = Pink()
                            enemies.add(pink)
                            cyan = Cyan()
                            enemies.add(cyan)
                            orange = Orange()
                            enemies.add(orange)
                            all_sprites.remove(pacman)
                            del pacman
                            all_images = []
                            all_images = pyganim.getImagesFromSpriteSheet('data/sprite_sheet.png', cols=16, rows=16,
                                                                          rects=all_images)
                            for i in range(len(all_images)):
                                all_images[i] = pygame.transform.rotate(all_images[i], -90)
                            frames = list(zip(all_images, [150 if i < 60 else 120 for i in range(256)]))
                            pacman = Pacman()
                            all_sprites.add(pacman)
                            pacman.points = saved_points
                            all_sprites.update(maze, enemies)
                            new_lvl = True
                            pacman_old_rect_left = pacman.rect.left
                            maze_map = start_map

                    ENTER_SOUND.play()
                if event.key == K_ESCAPE:
                    if select_game_type_classic or select_game_type_ir:
                        select_game_type_classic = False
                        select_game_type_ir = False
                        switch = 1
                    else:
                        game_on = False
                        menu = False
                        run = False

                ENTER_SOUND.play()

            if switch == 4:
                switch = 1
            elif switch == 0:
                switch = 3

        pygame.display.update()

    if play_game:
        pygame.mixer.music.load('data/Hyper - Spoiler.mp3')
        pygame.mixer.music.play(-1)

        red_timer = pygame.time.get_ticks()
        pink_timer = pygame.time.get_ticks()
        cyan_timer = pygame.time.get_ticks()
        orange_timer = pygame.time.get_ticks()
        fear_time = 8
        play_timer = pygame.time.get_ticks()
        new_lvl = True
        if not last_played == "ir" or pacman.points == 0:
            maps_generated = False

        if infinity_run:
            pacman.main_speed = 10
            red.start_speed = 8
            orange.stop_game = False
            cyan.stop_game = False
            pink.stop_game = False
            pacman_life = 0
            need_to_generate_left = True
            need_to_generate_right = True

        while run:

            if infinity_run:

                if red.rect.left - pacman.rect.left > 560:
                    red.rect.left = pacman.rect.left - 560
                    red.rect.top = pacman.rect.top
                    red.speed_x = 0
                    red.speed_y = 8
                if pink.rect.left - pacman.rect.left > 560:
                    pink.rect.left = pacman.rect.left - 560
                    pink.rect.top = 200
                    pink.speed_x = 0
                    pink.speed_y = 8
                if orange.rect.left - pacman.rect.left > 560:
                    orange.rect.left = pacman.rect.left - 560
                    orange.rect.top = 500
                    orange.speed_x = 0
                    orange.speed_y = 8
                if cyan.rect.left - pacman.rect.left > 560:
                    cyan.rect.left = pacman.rect.left - 560
                    cyan.rect.top = 800
                    cyan.speed_x = 0
                    cyan.speed_y = 8

                if red.rect.left - pacman.rect.left < -560:
                    red.rect.left = pacman.rect.left + 560
                    red.rect.top = pacman.rect.top
                    red.speed_x = 0
                    red.speed_y = 8
                if pink.rect.left - pacman.rect.left < - 560:
                    pink.rect.left = pacman.rect.left + 560
                    pink.rect.top = 200
                    pink.speed_x = 0
                    pink.speed_y = 8
                if orange.rect.left - pacman.rect.left < - 560:
                    orange.rect.left = pacman.rect.left + 560
                    orange.rect.top = 500
                    orange.speed_x = 0
                    orange.speed_y = 8
                if cyan.rect.left - pacman.rect.left < - 560:
                    cyan.rect.left = pacman.rect.left + 560
                    cyan.rect.top = 800
                    cyan.speed_x = 0
                    cyan.speed_y = 8

                if abs(pacman.rect.left - pacman_old_rect_left) == 960:
                    if pacman.rect.left - pacman_old_rect_left > 0:
                        prev_map = now_map
                        maze_map = next_map
                        need_to_generate_right = True
                    else:
                        next_map = now_map
                        maze_map = prev_map
                        need_to_generate_left = True
                    maps_generated = False

                if not maps_generated:
                    pacman_old_rect_left = pacman.rect.left
                    now_map = maze_map

                    if need_to_generate_right:
                        next_map = maze_gen(now_map)
                        need_to_generate_right = False

                    if need_to_generate_left:
                        temp_map = []
                        for row in range(len(maze_map)):
                            temp_map.append('')
                            for col in range(len(maze_map[row]) - 1, -1, -1):
                                temp_map[row] += maze_map[row][col]
                        temp_map = maze_gen(temp_map)
                        prev_map = []
                        for row in range(len(temp_map)):
                            prev_map.append('')
                            for col in range(len(temp_map[row]) - 1, -1, -1):
                                prev_map[row] += temp_map[row][col]
                        need_to_generate_left = False

                    full_map = []
                    for row in range(24):
                        full_map.append('')
                        for col in (prev_map[row] + now_map[row] + next_map[row]):
                            full_map[row] += col

                    m = 0
                    while len(maze) != 0:
                        all_sprites.remove(maze[m])
                        maze.pop(0)
                    while len(dots) != 0:
                        all_sprites.remove(dots[m])
                        dots.pop(0)
                    while len(maze_road) != 0:
                        all_sprites.remove(maze_road[m])
                        maze_road.pop(0)

                    make_maze(full_map, pacman.rect.left - 460 - 960)
                    maps_generated = True

            scatter_time = 7 - (1 / 37.5) * (level - 1)
            chase_time = 30 + 3.95 * (level - 1)

            if new_lvl:
                start = Points(450, 640, 'Start!')
                points.append(start)
                points_time.append(pygame.time.get_ticks())
                new_lvl = False

            if len(dots) < 50 and not red.fear:
                red.start_speed = 4

            if len(fruits) > 0:
                if len(fruit_timer) > 0:
                    for i in range(len(fruits)):
                        if (pygame.time.get_ticks() - fruit_timer[i]) / 1000 > 9 and fruit_timer[i] != 0:
                            all_sprites.remove(fruits[i])
                            fruits.pop(i)
                            fruit_timer.pop(i)
                            fruits_level.pop(i)

                if len(fruits_level) > 0:
                    if level - fruits_level[0] > 5:
                        all_sprites.remove(fruits[0])
                        fruits.pop(0)
                        fruit_timer.pop(0)
                        fruits_level.pop(0)

            if not red.fear:
                if not red.scatter and (pygame.time.get_ticks() - red_timer) / 1000 > chase_time:
                    red.scatter = True
                    red_timer = pygame.time.get_ticks()
                if red.scatter and (pygame.time.get_ticks() - red_timer) / 1000 > scatter_time or len(dots) < 50:
                    red.scatter = False
                    red_timer = pygame.time.get_ticks()

            else:
                if (pygame.time.get_ticks() - fear_start_time) / 1000 > fear_time:
                    red.fear = False
                    red.start_speed = 2
                    if red.rect.left % 2 != 0:
                        red.rect.left += 1
                    if red.rect.top % 2 != 1:
                        red.rect.top += 1
                    pacman.eaten_enemies = 0

            if not pink.fear:
                if not pink.scatter and (pygame.time.get_ticks() - pink_timer) / 1000 > chase_time:
                    pink.scatter = True
                    pink_timer = pygame.time.get_ticks()
                if pink.scatter and (pygame.time.get_ticks() - pink_timer) / 1000 > scatter_time:
                    pink.scatter = False
                    pink_timer = pygame.time.get_ticks()

            else:
                if (pygame.time.get_ticks() - fear_start_time) / 1000 > fear_time:
                    pink.fear = False
                    pink.start_speed = 2
                    if pink.rect.left % 2 != 0:
                        pink.rect.left += 1
                    if pink.rect.top % 2 != 1:
                        pink.rect.top += 1
                    pacman.eaten_enemies = 0

            if not cyan.fear:
                if not cyan.scatter and (pygame.time.get_ticks() - cyan_timer) / 1000 > chase_time:
                    cyan.scatter = True
                    cyan_timer = pygame.time.get_ticks()
                if cyan.scatter and (pygame.time.get_ticks() - cyan_timer) / 1000 > scatter_time:
                    cyan.scatter = False
                    cyan_timer = pygame.time.get_ticks()

            else:
                if (pygame.time.get_ticks() - fear_start_time) / 1000 > fear_time:
                    cyan.fear = False
                    cyan.start_speed = 2
                    if cyan.rect.left % 2 != 0:
                        cyan.rect.left += 1
                    if cyan.rect.top % 2 != 1:
                        cyan.rect.top += 1
                    pacman.eaten_enemies = 0

            if not orange.fear:
                if not orange.scatter and (pygame.time.get_ticks() - orange_timer) / 1000 > chase_time:
                    orange.scatter = True
                    orange_timer = pygame.time.get_ticks()
                if orange.scatter and (pygame.time.get_ticks() - orange_timer) / 1000 > scatter_time:
                    orange.scatter = False
                    orange_timer = pygame.time.get_ticks()

            else:
                if (pygame.time.get_ticks() - fear_start_time) / 1000 > fear_time:
                    orange.fear = False
                    orange.start_speed = 2
                    if orange.rect.left % 2 != 0:
                        orange.rect.left += 1
                    if orange.rect.top % 2 != 1:
                        orange.rect.top += 1
                    pacman.eaten_enemies = 0

            if pacman.eaten_enemies == 4:
                pacman.eaten_enemies = 0

            screen.fill(Color(BACKGROUND_COLOR))
            screen.blit(BACKGROUND_IMAGE, (0, 0))
            animObj.play()

            game_score_text = font.render("Game Score: " + str(pacman.points), False, Color("#ffff00"))
            screen.blit(game_score_text, (20, 5))
            if pacman.points > high_score:
                high_score = pacman.points
            high_score_text = font.render("High Score: " + str(high_score), False, Color("#ffff00"))
            screen.blit(high_score_text, (400, 5))
            level_text = font.render("Level : " + str(level), False, Color("#ffff00"))
            screen.blit(level_text, (780, 5))

            if pacman_life > 0:
                screen.blit(all_images[133], (20, 1010))
            if pacman_life > 1:
                screen.blit(all_images[133], (60, 1010))

            if not pacman.death_check:
                if (pink.stop_game and pacman.points / 10 - saved_points / 10 >= 30) or (
                        pink.stop_game and (pygame.time.get_ticks() - play_timer) / 1000 > 4):
                    pink.stop_game = False
                    pink.start_speed = 2
                    play_timer = pygame.time.get_ticks()

                elif (cyan.stop_game and pacman.points / 10 - saved_points / 10 >= 60) or (
                        cyan.stop_game and (pygame.time.get_ticks() - play_timer) / 1000 > 4):
                    cyan.stop_game = False
                    cyan.start_speed = 2
                    play_timer = pygame.time.get_ticks()

                elif (orange.stop_game and pacman.points / 10 - saved_points / 10 >= 90) or (
                        orange.stop_game and (pygame.time.get_ticks() - play_timer) / 1000 > 4):
                    orange.stop_game = False
                    orange.start_speed = 2
                    play_timer = pygame.time.get_ticks()

            if pacman.can_eat_enemies and level < 19:
                if not red.fear:
                    red.fear_timer = pygame.time.get_ticks()
                    red.fear = True
                    red.start_speed = 1
                    red.speed_x *= -1
                    red.speed_y *= -1
                    fear_start_time = pygame.time.get_ticks()
                if not pink.fear:
                    pink.fear_timer = pygame.time.get_ticks()
                    pink.fear = True
                    pink.start_speed = 1
                    pink.speed_x *= -1
                    pink.speed_y *= -1
                    fear_start_time = pygame.time.get_ticks()
                if not cyan.fear:
                    cyan.fear_timer = pygame.time.get_ticks()
                    cyan.fear = True
                    cyan.start_speed = 1
                    cyan.speed_x *= -1
                    cyan.speed_y *= -1
                    fear_start_time = pygame.time.get_ticks()
                if not orange.fear:
                    orange.fear_timer = pygame.time.get_ticks()
                    orange.fear = True
                    orange.start_speed = 1
                    orange.speed_x *= -1
                    orange.speed_y *= -1
                    fear_start_time = pygame.time.get_ticks()
                pacman.can_eat_enemies = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    game_on = False

                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        run = False
                        play_game = False
                        menu = True

                    if event.key == K_LEFT or event.key == K_a:
                        if 'left' not in pacman.move_direction:
                            pacman.move_direction.append('left')
                    elif 'left' in pacman.move_direction:
                        if len(pacman.move_direction) > 2:
                            pacman.move_direction.remove('left')

                    if event.key == K_RIGHT or event.key == K_d:
                        if 'right' not in pacman.move_direction:
                            pacman.move_direction.append('right')
                    elif 'right' in pacman.move_direction:
                        if len(pacman.move_direction) > 2:
                            pacman.move_direction.remove('right')

                    if event.key == K_UP or event.key == K_w:
                        if 'up' not in pacman.move_direction:
                            pacman.move_direction.append('up')
                    elif 'up' in pacman.move_direction:
                        if len(pacman.move_direction) > 2:
                            pacman.move_direction.remove('up')

                    if event.key == K_DOWN or event.key == K_s:
                        if 'down' not in pacman.move_direction:
                            pacman.move_direction.append('down')
                    elif 'down' in pacman.move_direction:
                        if len(pacman.move_direction) > 2:
                            pacman.move_direction.remove('down')

                    if event.key == K_p:
                        dots = []
                        super_dots = []

            all_sprites.update(maze, enemies)

            if pacman.death_check:
                for e in enemies:
                    if not e.stop_game:
                        e.stop_game = True
                        start_death_ticks = pygame.time.get_ticks()

                if pygame.time.get_ticks() - start_death_ticks > 1400 and start_death_ticks != 0:
                    pygame.time.wait(800)
                    if pacman_life > 0:
                        pacman_life -= 1

                        saved_points = pacman.points

                        for en in enemies:
                            enemies.remove(en)

                        del red, pink, orange, cyan, enemies
                        update_all(False)

                        pygame.time.wait(1600)

                        enemies = pygame.sprite.Group()

                        red = Red()
                        enemies.add(red)
                        pink = Pink()
                        enemies.add(pink)
                        cyan = Cyan()
                        enemies.add(cyan)
                        orange = Orange()
                        enemies.add(orange)

                        all_sprites.remove(pacman)
                        del pacman

                        all_images = []
                        all_images = pyganim.getImagesFromSpriteSheet('data/sprite_sheet.png', cols=16, rows=16,
                                                                      rects=all_images)

                        for i in range(len(all_images)):
                            all_images[i] = pygame.transform.rotate(all_images[i], -90)
                        frames = list(zip(all_images, [150 if i < 60 else 120 for i in range(256)]))

                        animObj = pyganim.PygAnimation(frames)

                        pacman = Pacman()
                        all_sprites.add(pacman)
                        pacman.points = saved_points
                        all_sprites.update(maze, enemies)
                        new_lvl = True
                    else:
                        pacman_life -= 1
                        run = False
                        menu = True
                        play_game = False

            if len(dots) == 0 and len(super_dots) == 0:
                WIN_SOUND.play()
                pacman_life += 1
                for m in maze:
                    maze.remove(m)
                    all_sprites.remove(m)
                make_maze(maze_map)
                pacman.death_check = True
                level += 1

            update_all(True)
            clock.tick(120)

high_score_file = open('data/high_score', 'w')
high_score_file.write(str(high_score))
high_score_file.close()
pygame.quit()
exit()
