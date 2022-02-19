import pygame
import sys
import time
from map import Mapper
import random
from os import startfile, environ


class Player(object):
    def __init__(self):
        self.type = app.playertype

        self.width = 292
        self.height = 244
        self.floor = settings["size"][1] - 200

        self.x = 750
        self.y = self.floor - self.height // 2
        self.dx = 0

        self.direction = "Right"

        self.idling = True
        self.running = False
        self.jumping = False
        self.attacking = False
        self.acceleration = 1

        self.hp = app.playerhp
        self.dmg = app.playerdmg

        # self.idle_animation = {}
        # self.idle_animation["Right"] = []
        # is the same as
        self.idle_animation = {"Right": [], "Left": []}
        for x in range(0, 7):
            image = pygame.transform.scale(
                pygame.image.load(
                    "assets/player_" + self.type + "/_IDLE/frame_" + str(x) + ".png").convert_alpha(),
                (self.width, self.height))
            self.idle_animation["Right"].append(image)
            self.idle_animation["Left"].append(
                pygame.transform.flip(image, True, False)
            )

        self.idle_animation["Left"] = []
        for image in self.idle_animation["Right"]:
            self.idle_animation["Left"].append(
                pygame.transform.flip(image, True, False)
            )

        # animation V2
        self.run_animation = {"Right": [], "Left": []}
        for x in range(0, 7):
            image = pygame.transform.scale(
                pygame.image.load(
                    "assets/player_" + self.type + "/_RUN/frame_" + str(x) + ".png").convert_alpha(),
                (self.width, self.height))
            self.run_animation["Right"].append(image)
            self.run_animation["Left"].append(
                pygame.transform.flip(image, True, False)
            )

        self.jump_animation = {"Right": [], "Left": []}
        for x in range(0, 2):
            image = pygame.transform.scale(
                pygame.image.load(
                    "assets/player_" + self.type + "/_JUMP/frame_" + str(x) + ".png").convert_alpha(),
                (self.width, self.height))
            self.jump_animation["Right"].append(image)
            self.jump_animation["Left"].append(
                pygame.transform.flip(image, True, False)
            )

        self.atk_animation = {"Right": [], "Left": []}
        for x in range(0, 7):
            image = pygame.transform.scale(
                pygame.image.load(
                    "assets/player_" + self.type + "/_ATTACK/frame_" + str(x) + ".png").convert_alpha(),
                (self.width, self.height))
            self.atk_animation["Right"].append(image)
            self.atk_animation["Left"].append(
                pygame.transform.flip(image, True, False)
            )

        self.hp_bar = []
        for x in range(0, 5):
            self.hp_bar.append(pygame.image.load("assets/UI/hp_bar/bar_" + str(x) + ".png").convert_alpha())

        self.anim_start = self.millis()
        self.anim_tick = 100
        self.atk_tick = 0

        self.last_atk = 0
        self.atk_cd = 500

        self.speed_x = 20
        self.speed_y = 0

    def millis(self):
        return int(time.time() * 1000)

    def status_clear(self):
        self.idling = False
        self.running = False
        self.jumping = False
        self.attacking = False

    def hitbox_update(self):
        if self.direction == "Left":
            self.hitbox = pygame.Rect(self.x - app.state.camera_x - self.width // 2, self.y - self.height // 2,
                                      self.width // 2,
                                      self.height)
        else:
            self.hitbox = pygame.Rect(self.x - app.state.camera_x, self.y - self.height // 2,
                                      self.width // 2, self.height)

    def move(self, dx=0, dy=0):
        self.speed_x = 25
        if dx < 0:
            self.direction = "Left"
            if not self.jumping:
                self.status_clear()
                self.running = True

        if dx > 0:
            self.direction = "Right"
            if not self.jumping:
                self.status_clear()
                self.running = True

        if dx == 0:
            if not self.jumping and not self.attacking:
                self.status_clear()
                self.idling = True

        # Left wall collision
        if self.x - self.width / 2 < 0:
            self.x = self.width // 2

        # Right wall collision
        if self.x + self.width / 2 > settings["size"][0] * 2:
            self.x = settings["size"][0] * 2 - self.width // 2

        # Camera movement right (starts st 1/2 of screen width)
        if self.x - app.state.camera_x > settings["size"][0] / 2:
            app.state.camera_x += 25

        # Camera movement left (starts st 1/4 of screen width)
        elif self.x - app.state.camera_x < settings["size"][0] / 4:
            app.state.camera_x -= 25

        if app.state.camera_x > settings["size"][0]:
            app.state.camera_x = settings["size"][0]
        if app.state.camera_x < 0:
            app.state.camera_x = 0

        if self.jumping:
            self.speed_y += self.acceleration
            self.x += self.speed_x * dx
            self.y += self.speed_y

        if self.running:
            self.x += self.speed_x * dx

        if self.y - self.height / 2 < 0:
            self.y = self.height // 2
            self.speed_y = self.speed_y // 2

        if self.y + self.height / 2 > self.floor:
            self.y = self.floor - self.height // 2
            self.status_clear()
            self.idling = True
            self.speed_y = 0

    def jump(self):
        if not self.jumping:
            self.status_clear()
            self.jumping = True
            self.speed_y = -15

    def attack(self):
        if not self.attacking and not self.jumping:
            self.status_clear()
            self.attacking = True
            self.atk_tick = 0

    def draw_hp(self):
        if (self.hp % 25) == 0:
            hp = self.hp_bar[self.hp // 25]
        else:
            hp = self.hp_bar[(self.hp // 25) + 1]

        app.screen.blit(hp, (self.x - app.state.camera_x - self.width // 4, self.y - self.height // 2 - 30))

    def draw(self):
        left_upper_x = round(self.x - self.width / 2)
        left_upper_y = round(self.y - self.height / 2)
        if self.idling:
            image = self.idle_animation[self.direction][
                ((self.millis() - self.anim_start) // self.anim_tick) % len(self.idle_animation[self.direction])
                ]

        elif self.running:
            image = self.run_animation[self.direction][
                ((self.millis() - self.anim_start) // self.anim_tick) % len(self.run_animation[self.direction])
                ]

        elif self.jumping:
            if self.speed_y > 0:
                image = self.jump_animation[self.direction][0]
            else:
                image = self.jump_animation[self.direction][1]

        elif self.attacking:
            image = self.atk_animation[self.direction][self.atk_tick % len(self.atk_animation[self.direction])]
            self.atk_tick += 1
            if self.atk_tick == 9:
                for enemy in app.state.enemies:
                    if self.hitbox.colliderect(enemy.hitbox):
                        enemy.hp -= self.dmg
                        app.screen.blit(enemy.hp_bar[0],
                                        (enemy.x - app.state.camera_x - enemy.width // 4, enemy.y - enemy.height // 2 - 30))
                        # print("blit")
                        # pygame.display.update()

                self.status_clear()
                self.atk_tick = 0

        app.screen.blit(image, (left_upper_x - app.state.camera_x, left_upper_y))
        self.draw_hp()
        self.hitbox_update()

        # hitbox debug
        # pygame.draw.rect(app.screen, (255, 0, 0), self.hitbox)


class Enemy:
    def __init__(self, type, x=2000):
        self.type = type

        if self.type == "creep":
            self.width = 320
            self.height = 280
            self.vision = 800
            self.dmg = 8
            self.hp = 100
            self.anim_tick = 80

        elif self.type == "spirit":
            self.width = 160
            self.height = 160
            self.vision = 1000
            self.dmg = 30
            self.hp = 40
            self.anim_tick = 60

        self.x = x
        self.y = settings["size"][1] - 205 - self.height // 2
        self.direction = "Left"

        self.idling = True
        self.running = False
        self.jumping = False
        self.attacking = False

        self.anim_start = self.millis()
        self.atk_tick = 0

        self.hp_bar = []

        self.speed_x = 20
        self.speed_y = 0

        self.last_atk = 0
        self.atk_cd = 2000

        self.idle_animation = {"Right": [], "Left": []}
        self.run_animation = {"Right": [], "Left": []}
        self.atk_animation = {"Right": [], "Left": []}

        if type == "creep":
            for x in range(0, 4):
                image = pygame.transform.scale(
                    pygame.image.load("assets/enemy_" + type + "/idle/frame_" + str(x) + ".png").convert_alpha(),
                    (self.width, self.height))
                self.idle_animation["Left"].append(image)
                self.idle_animation["Right"].append(pygame.transform.flip(image, True, False))

            for x in range(0, 10):
                image = pygame.transform.scale(
                    pygame.image.load("assets/enemy_" + type + "/run/frame_" + str(x) + ".png").convert_alpha(),
                    (self.width, self.height))
                self.run_animation["Left"].append(image)
                self.run_animation["Right"].append(pygame.transform.flip(image, True, False))

            for x in range(0, 10):
                image = pygame.transform.scale(
                    pygame.image.load("assets/enemy_" + type + "/atk/frame_" + str(x) + ".png").convert_alpha(),
                    (self.width, self.height))
                self.atk_animation["Left"].append(image)
                self.atk_animation["Right"].append(pygame.transform.flip(image, True, False))

        elif type == "spirit":
            for x in range(0, 8):
                image = pygame.transform.scale(
                    pygame.image.load("assets/enemy_" + type + "/idle/frame_" + str(x) + ".png").convert_alpha(),
                    (self.width, self.height))
                self.idle_animation["Left"].append(image)
                self.idle_animation["Right"].append(pygame.transform.flip(image, True, False))

            for x in range(0, 8):
                image = pygame.transform.scale(
                    pygame.image.load("assets/enemy_" + type + "/run/frame_" + str(x) + ".png").convert_alpha(),
                    (self.width, self.height))
                self.run_animation["Left"].append(image)
                self.run_animation["Right"].append(pygame.transform.flip(image, True, False))

            for x in range(0, 24):
                image = pygame.transform.scale(
                    pygame.image.load("assets/enemy_" + type + "/atk/frame_" + str(x) + ".png").convert_alpha(),
                    (self.width, self.height))
                self.atk_animation["Left"].append(image)
                self.atk_animation["Right"].append(pygame.transform.flip(image, True, False))

        self.hp_bar = []
        for x in range(0, 5):
            self.hp_bar.append(pygame.image.load("assets/UI/hp_bar/bar_" + str(x) + ".png").convert_alpha())

    def millis(self):
        return int(time.time() * 1000)

    def status_clear(self):
        self.idling = False
        self.running = False
        self.jumping = False
        self.attacking = False

    def hitbox_update(self):
        if self.type == "creep":
            if self.direction == "Left":
                self.hitbox = pygame.Rect(self.x - app.state.camera_x - self.width // 2, self.y - self.height // 2,
                                          self.width // 2,
                                          self.height)
            else:
                self.hitbox = pygame.Rect(self.x - app.state.camera_x, self.y - self.height // 2,
                                          self.width // 2, self.height)

        else:
            self.hitbox = pygame.Rect(self.x - app.state.camera_x - self.width // 2, self.y - self.height // 2,
                                      self.width * 2,
                                      self.height)

    def draw_hp(self):
        if (self.hp % 25) == 0:
            app.screen.blit(self.hp_bar[self.hp // 25],
                            (self.x - app.state.camera_x - self.width // 4, self.y - self.height // 2 - 30))
        else:
            app.screen.blit(self.hp_bar[(self.hp // 25) + 1],
                            (self.x - app.state.camera_x - self.width // 4, self.y - self.height // 2 - 30))

    def move(self):
        self.speed_x = 15
        dx = 0

        if self.type == "creep":
            atk_range = self.width // 2
        else:
            atk_range = self.width * 2
        if abs(self.x - app.state.player.x) <= atk_range:
            if self.millis() - self.last_atk >= self.atk_cd and not self.attacking:
                self.status_clear()
                self.attacking = True
                self.atk_tick = 0
            elif not self.attacking:
                self.status_clear()
                self.idling = True
                dx = 0

        elif not self.attacking and abs(self.x - app.state.player.x) <= self.vision:
            if self.x > app.state.player.x:
                self.direction = "Left"
                dx = -1
            elif self.x < app.state.player.x:
                self.direction = "Right"
                dx = 1
            self.status_clear()
            self.running = True

        else:
            self.status_clear()
            self.idling = True
            dx = 0

        if self.running:
            self.x += self.speed_x * dx

        # # Left wall collision
        # if self.x - self.width / 2 < 0:
        #     self.x = self.width // 2
        #
        # # Right wall collision
        # if self.x + self.width / 2 > settings["size"][0] * 2:
        #     self.x = settings["size"][0] * 2 - self.width // 2
        #
        # # Camera movement right (starts st 1/2 of screen width)
        # if self.x - app.state.camera_x > settings["size"][0] / 2:
        #     app.state.camera_x += 25
        #
        # # Camera movement left (starts st 1/4 of screen width)
        # elif self.x - app.state.camera_x < settings["size"][0] / 4:
        #     app.state.camera_x -= 25

    def draw(self):
        left_upper_x = round(self.x - self.width / 2)
        left_upper_y = round(self.y - self.height / 2)
        if self.idling:
            image = self.idle_animation[self.direction][
                ((self.millis() - self.anim_start) // self.anim_tick) % len(self.idle_animation[self.direction])
                ]
        elif self.running:
            image = self.run_animation[self.direction][
                ((self.millis() - self.anim_start) // self.anim_tick) % len(self.run_animation[self.direction])
                ]

        elif self.attacking:
            image = self.atk_animation[self.direction][self.atk_tick]
            if self.atk_tick >= len(self.atk_animation[self.direction]) - 1:
                self.atk_tick = 0
                if self.hitbox.colliderect(app.state.player.hitbox):
                    if app.state.player.hp - self.dmg > 0:
                        app.state.player.hp -= self.dmg
                        app.screen.blit(app.state.player.hp_bar[0], (
                            app.state.player.x - app.state.camera_x - app.state.player.width // 4,
                            app.state.player.y - app.state.player.height // 2 - 30))
                    else:
                        app.state.player.hp = 0
                self.status_clear()

                if self.type == "spirit":
                    self.hp = 0
                else:
                    self.last_atk = self.millis()
            else:
                self.atk_tick += 1

        app.screen.blit(image, (left_upper_x - app.state.camera_x, left_upper_y))
        self.draw_hp()
        self.hitbox_update()
        # hitbox debug
        # pygame.draw.rect(app.screen, (255, 0, 0), self.hitbox)


class States(object):
    def __init__(self):
        self.done = False
        self.next = None
        self.quit = False
        self.previous = None


class Menu(States):
    def __init__(self):
        States.__init__(self)
        self.next = 'choice'

        bg = pygame.image.load("assets/title_bg.png").convert()
        self.bg = pygame.transform.scale(bg, settings['size'])
        self.title = pygame.font.Font("assets/UI/Font/kenvector_future.ttf", 192).render("SHIZA", True, (218, 165, 32))
        self.titleRect = self.title.get_rect()
        self.titleRect.center = (settings['size'][0] // 2, settings['size'][1] // 2)

        self.enter = pygame.font.Font("assets/UI/Font/kenvector_future.ttf", 32).render("Press Enter to start...",
                                                                                        True, (180, 180, 190))
        self.enterRect = self.enter.get_rect()
        self.enterRect.center = (settings['size'][0] // 2, (settings['size'][1] // 2) + 200)

        self.help = pygame.font.Font("assets/UI/Font/kenvector_future.ttf", 32).render("Press H to show help...",
                                                                                       True, (180, 180, 190))
        self.helpRect = self.help.get_rect()
        self.helpRect.center = (settings['size'][0] // 2, (settings['size'][1] // 2) + 400)

    def cleanup(self):
        fader = pygame.Surface(settings["size"])
        fader.fill((0, 0, 0))
        for alpha in range(0, 100):
            fader.set_alpha(alpha)
            app.screen.blit(fader, (0, 0))
            pygame.display.update()
            pygame.event.pump()
        app.screen.fill((0, 0, 0))

    def startup(self):
        fader = pygame.Surface(settings["size"])
        fader.fill((0, 0, 0))
        for alpha in range(255, 0, -1):
            fader.set_alpha(alpha)
            app.screen.blit(self.bg, (0, 0))
            app.screen.blit(self.title, self.titleRect)
            app.screen.blit(fader, (0, 0))
            pygame.display.update()
            pygame.event.pump()
        self.draw()

    def get_event(self, pressed):
        if pressed[pygame.K_RETURN]:
            self.done = True
        if pressed[pygame.K_h]:
            startfile('help.txt')

    def update(self):
        self.draw()

    def draw(self):
        app.screen.blit(self.bg, (0, 0))
        app.screen.blit(self.title, self.titleRect)
        app.screen.blit(self.enter, self.enterRect)
        app.screen.blit(self.help, self.helpRect)
        # app.screen.blit(self.fader, (0, 0))


class Classchoice(States):
    def __init__(self):
        States.__init__(self)
        self.next = 'map'

        bg = pygame.image.load("assets/title_bg.png").convert()
        self.bg = pygame.transform.scale(bg, settings['size'])
        self.title = pygame.font.Font("assets/UI/Font/kenvector_future.ttf", 80).render("CHOOSE YOUR CHARACTER", True,
                                                                                        (200, 200, 200))
        self.dark = pygame.Surface(settings["size"])
        self.dark.fill((0, 0, 0))
        self.dark.set_alpha(100)
        self.titleRect = self.title.get_rect()
        self.titleRect.center = (settings['size'][0] // 2, 100)

        self.mouse_img = pygame.image.load("assets/UI/cursor.png").convert_alpha()

        self.btn_width = 292
        self.btn_height = 244

        self.anim_start = self.millis()
        self.anim_tick = 100

        self.btns = [
            {
                "model": [],
                "type": "axe",
                "rect": pygame.Rect((settings["size"][0] // 2) - ((self.btn_width // 2) * 3),
                                    (settings["size"][1] // 2) - (self.btn_width // 2), self.btn_width, self.btn_height)
            },
            {
                "model": [],
                "type": "sword",
                "rect": pygame.Rect((settings["size"][0] // 2) + (self.btn_width // 2),
                                    (settings["size"][1] // 2) - (self.btn_width // 2), self.btn_width, self.btn_height)
            }
        ]

        for x in range(0, 7):
            image = pygame.transform.scale(
                pygame.image.load(
                    "assets/player_axe/_IDLE/frame_" + str(x) + ".png").convert_alpha(),
                (self.btn_width, self.btn_height))
            self.btns[0]["model"].append(image)

        for x in range(0, 7):
            image = pygame.transform.scale(
                pygame.image.load(
                    "assets/player_sword/_IDLE/frame_" + str(x) + ".png").convert_alpha(),
                (self.btn_width, self.btn_height))
            self.btns[1]["model"].append(image)

    def cleanup(self):
        fader = pygame.Surface(settings["size"])
        fader.fill((0, 0, 0))
        for alpha in range(0, 100):
            fader.set_alpha(alpha)
            app.screen.blit(fader, (0, 0))
            pygame.display.update()
            pygame.event.pump()
        app.screen.fill((0, 0, 0))

    def startup(self):
        fader = pygame.Surface(settings["size"])
        fader.fill((0, 0, 0))
        for alpha in range(255, 100, -10):
            fader.set_alpha(alpha)
            app.screen.blit(self.bg, (0, 0))
            app.screen.blit(self.title, self.titleRect)
            app.screen.blit(fader, (0, 0))
            pygame.display.update()
            pygame.event.pump()
        self.draw()

    def get_event(self, pressed):
        for i in range(len(self.btns)):
            if app.LMB_pressed and self.btns[i]['rect'].collidepoint(app.MOUSE_POS):
                app.playertype = self.btns[i]['type']
                self.done = True

    def update(self):
        self.draw()

    def millis(self):
        return int(time.time() * 1000)

    def draw(self):
        app.screen.blit(self.bg, (0, 0))
        app.screen.blit(self.dark, (0, 0))
        app.screen.blit(self.title, self.titleRect)
        for i in range(2):
            pygame.draw.rect(app.screen, (180, 180, 190), self.btns[i]["rect"])
            app.screen.blit(self.btns[i]["model"][
                                ((self.millis() - self.anim_start) // self.anim_tick) % len(self.btns[i]["model"])
                                ], self.btns[i]["rect"])

        app.screen.blit(self.mouse_img, app.MOUSE_POS)


class Loot(States):
    def __init__(self):
        States.__init__(self)
        self.next = 'map'

        self.bg = pygame.transform.scale(pygame.image.load("assets/title_bg.png").convert(), settings['size'])
        self.title = pygame.font.Font("assets/UI/Font/kenvector_future.ttf", 80).render("CHOOSE ACTION", True,
                                                                                        (200, 200, 200))
        self.dark = pygame.Surface(settings["size"])
        self.dark.fill((0, 0, 0))
        self.dark.set_alpha(100)
        self.titleRect = self.title.get_rect()
        self.titleRect.center = (settings['size'][0] // 2, 100)

        self.choice = 0

        self.mouse_img = pygame.image.load("assets/UI/cursor.png").convert_alpha()
        self.font = pygame.font.Font("assets/UI/Font/kenvector_future.ttf", 22)

        self.btns = []
        self.msg = ''

    def cleanup(self):
        fader = pygame.Surface(settings["size"])
        fader.fill((0, 0, 0))
        for alpha in range(0, 100):
            fader.set_alpha(alpha)
            app.screen.blit(fader, (0, 0))
            pygame.display.update()
            pygame.event.pump()
        app.screen.fill((0, 0, 0))

    def startup(self):
        fader = pygame.Surface(settings["size"])
        fader.fill((0, 0, 0))
        for alpha in range(255, 100, -10):
            fader.set_alpha(alpha)
            app.screen.blit(self.bg, (0, 0))
            app.screen.blit(self.title, self.titleRect)
            app.screen.blit(fader, (0, 0))
            pygame.display.update()
            pygame.event.pump()
        self.draw()
        self.choice = None
        self.btns = [
            {
                "model": pygame.transform.scale(
                    pygame.image.load('assets/UI/icons/upg_' + app.playertype + '.png').convert_alpha(),
                    (256, 256)),
                "rect": pygame.Rect((settings['size'][0] // 7), settings['size'][1] // 2 - 128, 256, 256),
                "outline": pygame.Rect((settings['size'][0] // 7) - 2, settings['size'][1] // 2 - 128 - 2, 256 + 4,
                                       256 + 4),
                "text": self.font.render("Sharpen(now: " + str(app.playerdmg) + ")", True, (255, 255, 255))
            },
            {
                "model": pygame.transform.scale(pygame.image.load('assets/UI/icons/potionRed.png').convert_alpha(),
                                                (256, 256)),
                "rect": pygame.Rect((settings['size'][0] // 7) * 3, settings['size'][1] // 2 - 128, 256, 256),
                "outline": pygame.Rect((settings['size'][0] // 7) * 3 - 2, settings['size'][1] // 2 - 128 - 2, 256 + 4,
                                       256 + 4),
                "text": self.font.render("Regen(now: " + str(app.playerhp) + ")", True, (255, 255, 255))
            },
            {
                "model": pygame.transform.scale(pygame.image.load('assets/UI/icons/x.png').convert_alpha(), (256, 256)),
                "rect": pygame.Rect((settings['size'][0] // 7) * 5, settings['size'][1] // 2 - 128, 256, 256),
                "outline": pygame.Rect((settings['size'][0] // 7) * 5 - 2, settings['size'][1] // 2 - 128 - 2, 256 + 4,
                                       256 + 4),
                "text": self.font.render("Abandon", True, (255, 255, 255))
            }
        ]
        self.msg = ''

    def get_event(self, pressed):
        for i in range(len(self.btns)):
            if app.LMB_pressed and self.btns[i]['rect'].collidepoint(app.MOUSE_POS) and self.choice is None:
                self.choice = i
                font = pygame.font.Font("assets/UI/Font/kenvector_future.ttf", 32)
                if self.choice == 0:
                    buff = random.randrange(2, 6)
                    app.playerdmg += buff
                    self.msg = font.render("You gained " + str(buff) + " attack damage! Press Enter to continue", True,
                                           (255, 255, 255), (0, 0, 0))
                    self.msgRect = self.msg.get_rect()
                    self.msgRect.center = (settings['size'][0] // 2, (settings['size'][1] // 2) + 400)
                elif self.choice == 1:
                    buff = random.randrange(10, 20)
                    if app.playerhp + buff > 100:
                        buff = 100 - app.playerhp
                    app.playerhp += buff
                    self.msg = font.render("You gained " + str(buff) + " HP! Press Enter to continue", True,
                                           (255, 255, 255), (0, 0, 0))
                    self.msgRect = self.msg.get_rect()
                    self.msgRect.center = (settings['size'][0] // 2, (settings['size'][1] // 2) + 400)
                elif self.choice == 2:
                    self.next = 'game_over'
                    self.done = True

            if self.choice is not None:
                if pressed[pygame.K_RETURN]:
                    self.done = True

    def update(self):
        self.draw()

    def millis(self):
        return int(time.time() * 1000)

    def draw(self):
        app.screen.blit(self.bg, (0, 0))
        app.screen.blit(self.dark, (0, 0))
        if self.msg:
            app.screen.blit(self.msg, self.msgRect)
        app.screen.blit(self.title, self.titleRect)
        for btn in self.btns:
            pygame.draw.rect(app.screen, (255, 255, 255), btn["outline"])
            pygame.draw.rect(app.screen, (0, 0, 0), btn["rect"])
            app.screen.blit(btn["text"], btn["rect"])
            app.screen.blit(btn["model"], btn["rect"])
        app.screen.blit(self.mouse_img, app.MOUSE_POS)


class Map(States):
    def __init__(self):
        States.__init__(self)
        self.next = ''
        self.game_map = Mapper(app.screen)
        self.game_map.generate()
        self.choicenode = self.game_map.currnode

    def cleanup(self):
        fader = pygame.Surface(settings["size"])
        fader.fill((0, 0, 0))
        for alpha in range(0, 100):
            fader.set_alpha(alpha)
            app.screen.blit(fader, (0, 0))
            pygame.display.update()
            pygame.event.pump()
        app.screen.fill((0, 0, 0))

    def startup(self):
        if app.completed < self.game_map.boss_count:
            self.choicenode = self.game_map.currnode
            self.game_map.drawall()
        else:
            self.next = 'game_over'
            self.done = True

    def get_event(self, pressed):
        if pressed[pygame.K_LEFT] and self.game_map.connection_check(self.game_map.currnode,
                                                                     [self.game_map.currnode[0] - 1,
                                                                      self.game_map.currnode[1]]):  # x-1
            # print("Selected left node")
            self.game_map.drawcircle(self.choicenode[0], self.choicenode[1])
            self.choicenode = [self.game_map.currnode[0] - 1, self.game_map.currnode[1]]

        if pressed[pygame.K_RIGHT] and self.game_map.connection_check(self.game_map.currnode,
                                                                      [self.game_map.currnode[0] + 1,
                                                                       self.game_map.currnode[1]]):  # x+1
            # print("Selected right node")
            self.game_map.drawcircle(self.choicenode[0], self.choicenode[1])
            self.choicenode = [self.game_map.currnode[0] + 1, self.game_map.currnode[1]]

        if pressed[pygame.K_UP] and self.game_map.connection_check(self.game_map.currnode,
                                                                   [self.game_map.currnode[0],
                                                                    self.game_map.currnode[1] - 1]):  # y-1
            # print("Selected up node")
            self.game_map.drawcircle(self.choicenode[0], self.choicenode[1])
            self.choicenode = [self.game_map.currnode[0], self.game_map.currnode[1] - 1]

        if pressed[pygame.K_DOWN] and self.game_map.connection_check(self.game_map.currnode,
                                                                     [self.game_map.currnode[0],
                                                                      self.game_map.currnode[
                                                                          1] + 1]):  # y+1
            # print("Selected down node")
            self.game_map.drawcircle(self.choicenode[0], self.choicenode[1])
            self.choicenode = [self.game_map.currnode[0], self.game_map.currnode[1] + 1]

        if pressed[pygame.K_SPACE]:
            self.game_map.drawcircle(self.choicenode[0], self.choicenode[1])
            self.choicenode = self.game_map.starting_point

        if pressed[pygame.K_RETURN] and self.choicenode != self.game_map.currnode:
            self.game_map.currnode = self.choicenode

            if self.game_map.nodetypes[self.game_map.currnode[0]][self.game_map.currnode[1]] == 3:
                self.next = 'loot'
                self.done = True

            elif self.game_map.nodetypes[self.game_map.currnode[0]][self.game_map.currnode[1]] == 4:
                self.next = 'level'
                self.done = True

            if self.game_map.nodetypes[self.game_map.currnode[0]][self.game_map.currnode[1]] != 2:
                self.game_map.nodetypes[self.game_map.currnode[0]][self.game_map.currnode[1]] = 5

    def update(self):
        self.draw()

    def draw(self):
        self.game_map.drawall()
        self.game_map.drawcircle(self.choicenode[0], self.choicenode[1], ringcol=(0, 100, 0))


class Level(States):
    def __init__(self):
        States.__init__(self)
        self.next = 'map'

    def cleanup(self):
        fader = pygame.Surface(settings["size"])
        fader.fill((0, 0, 0))
        for alpha in range(0, 100):
            fader.set_alpha(alpha)
            app.screen.blit(fader, (0, 0))
            pygame.display.update()
        app.screen.fill((0, 0, 0))
        app.playerhp = self.player.hp
        app.completed += 1

    def enem_randomise(self):
        for i in range(random.randint(3, 6)):
            self.enemies.append(Enemy(random.choice(["creep", "spirit"]), x=random.randrange(1800, 3000)))

    def startup(self):
        # print("Loading")
        self.background = pygame.image.load("assets/background/bg_{}.png".format(random.choice([1, 2, 3])))
        self.player = Player()
        self.enemies = []
        self.enem_randomise()
        self.camera_x = 0

    def get_event(self, pressed):
        if self.player.hp > 0:
            if pressed[pygame.K_LEFT]:
                self.player.dx -= 1
            elif pressed[pygame.K_RIGHT]:
                self.player.dx += 1
            if pressed[pygame.K_UP]:
                self.player.jump()
            if pressed[pygame.K_SPACE]:
                self.player.attack()
            if pressed[pygame.K_KP_ENTER]:
                self.done = True
            if len(self.enemies) == 0:
                self.done = True
            for enemy in self.enemies:
                enemy.move()
        else:
            self.next = 'game_over'
            self.done = True

    def update(self):
        self.player.move(self.player.dx)
        self.player.dx = 0
        self.draw()

    def draw(self):
        app.screen.blit(self.background, (0 - self.camera_x, 0))
        self.player.draw()
        for enemy in self.enemies:
            if not enemy.hp <= 0:
                enemy.draw()
            else:
                app.playerscore += 1
                self.enemies.remove(enemy)


class Endscreen(States):
    def __init__(self):
        States.__init__(self)
        self.next = 'menu'

        bg = pygame.image.load("assets/title_bg.png").convert()
        self.dark = pygame.Surface(settings["size"])
        self.dark.fill((0, 0, 0))
        self.dark.set_alpha(100)
        self.bg = pygame.transform.scale(bg, settings['size'])
        self.title = pygame.font.Font("assets/UI/Font/kenvector_future.ttf", 80).render("GAME OVER!", True,
                                                                                        (218, 165, 32))
        self.titleRect = self.title.get_rect()
        self.titleRect.center = (settings['size'][0] // 2, 200)

        self.enter = pygame.font.Font("assets/UI/Font/kenvector_future.ttf", 32).render("Press Enter to restart...",
                                                                                        True, (180, 180, 190))
        self.enterRect = self.enter.get_rect()
        self.enterRect.center = (settings['size'][0] // 2, (settings['size'][1] // 2) + 200)

        self.esc = pygame.font.Font("assets/UI/Font/kenvector_future.ttf", 32).render("Press ESC to quit...",
                                                                                      True, (180, 180, 190))
        self.escRect = self.esc.get_rect()
        self.escRect.center = (settings['size'][0] // 2, (settings['size'][1] // 2) + 80)

    def cleanup(self):
        fader = pygame.Surface(settings["size"])
        fader.fill((0, 0, 0))
        for alpha in range(0, 100):
            fader.set_alpha(alpha)
            app.screen.blit(fader, (0, 0))
            pygame.display.update()
            pygame.event.pump()
        app.screen.fill((0, 0, 0))

    def startup(self):
        self.score = pygame.font.Font("assets/UI/Font/kenvector_future.ttf", 80).render(
            "You scored " + str(app.playerscore) + " kills!", True,
            (200, 200, 200))
        self.scoreRect = self.score.get_rect()
        self.scoreRect.center = (settings['size'][0] // 2, settings["size"][1] // 2)
        fader = pygame.Surface(settings["size"])
        fader.fill((0, 0, 0))
        for alpha in range(255, 100, -1):
            fader.set_alpha(alpha)
            app.screen.blit(self.bg, (0, 0))
            app.screen.blit(self.title, self.titleRect)
            app.screen.blit(fader, (0, 0))
            pygame.display.update()
            pygame.event.pump()
        self.draw()

    def get_event(self, pressed):
        if pressed[pygame.K_RETURN]:
            app.val_reset()
            for state in app.state_dict.values():
                state.__init__()
            self.done = True
        elif pressed[pygame.K_ESCAPE]:
            self.cleanup()
            app.done = True

    def update(self):
        self.draw()

    def draw(self):
        app.screen.blit(self.bg, (0, 0))
        app.screen.blit(self.dark, (0, 0))
        app.screen.blit(self.title, self.titleRect)
        app.screen.blit(self.score, self.scoreRect)
        app.screen.blit(self.enter, self.enterRect)
        app.screen.blit(self.esc, self.escRect)


class Control:
    def __init__(self, **settings):
        self.__dict__.update(settings)
        self.done = False
        self.val_reset()
        self.MOUSE_POS = (0, 0)
        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()

    def val_reset(self):
        self.playertype = None
        self.playerhp = 100
        self.playerdmg = 30
        self.playerscore = 0
        self.completed = 0

    def setup_states(self, state_dict, start_state):
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]

    def flip_state(self):
        self.state.done = False
        previous, self.state_name = self.state_name, self.state.next
        self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup()
        self.state.previous = previous

    def update(self):
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()
        self.state.update()

    def event_loop(self):
        pressed = pygame.key.get_pressed()
        self.LMB_pressed = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            if event.type == pygame.MOUSEMOTION:
                self.MOUSE_POS = event.pos
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.LMB_pressed = True

        self.state.get_event(pressed)

    def main_game_loop(self):
        self.state.startup()
        while not self.done:
            self.event_loop()
            self.update()
            pygame.display.update()


if __name__ == '__main__':
    settings = {
        'size': (1920, 1080),
        'fps': 60
    }
    environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()
    pygame.display.set_caption("SHIZA")
    pygame.mouse.set_visible(False)
    app = Control(**settings)
    state_dict = {
        'menu': Menu(),
        'choice': Classchoice(),
        'map': Map(),
        'loot': Loot(),
        'level': Level(),
        'game_over': Endscreen()
    }
    app.setup_states(state_dict, 'menu')
    app.main_game_loop()
    pygame.display.quit()
    pygame.quit()
    sys.exit()
