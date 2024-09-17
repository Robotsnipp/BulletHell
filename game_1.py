import random
import subprocess
import sys

import pygame

LASER_SPAWN = pygame.USEREVENT + 1
DELETE_LASER = pygame.USEREVENT + 2

FLOOR_HEIGHT = 480


def spawn_program_and_die(program, exit_code=0):
    """
    Start an external program and exit the script
    with the specified return code.

    Takes the parameter program, which is a list
    that corresponds to the argv of your command.
    """
    # Start the external program
    subprocess.Popen(program)
    # We have started the program, and can suspend this interpreter
    sys.exit(exit_code)


class Map():
    def __init__(self, map):
        self.map = []
        self.units = []
        with open('maps\\' + map, 'r', encoding='utf-8') as file:
            map = file.read()
            map = map.split('\n')
            for i in map:
                self.map.append(i)
        self.kill_blocks = []
        self.floor = []
        self.enemies = []
        self.walls = []
        self.height = len(self.map) * 50
        self.width = max([len(i) for i in map]) * 50
        self.screen = pygame.display.set_mode(
            (self.width if self.width <= 1000 else 1000, self.height if self.height <= 900 else 900))
        self.player = SpaceGuy(self.screen, 0, 0)
        self.spikes = []
        self.text = InfoText()
        for i in range(len(self.map)):
            for j in range(len(self.map[i])):
                if self.map[i][j] == '#':
                    self.floor.append(FloorBrick(j * 50, i * 50))
                    self.units.append(self.floor[-1])
                elif self.map[i][j] == '@':
                    self.player = SpaceGuy(self.screen, j * 50, i * 50)
                    self.units.append(Wall(j * 50, i * 50))
                elif self.map[i][j] == ' ':
                    self.walls.append(Wall(j * 50, i * 50))
                    self.units.append(self.walls[-1])
                elif self.map[i][j] == '*':
                    self.kill_blocks.append(KillBlock(j * 50, i * 50))
                    self.units.append(self.kill_blocks[-1])
                elif self.map[i][j] == 'e':
                    self.enemies.append(Enemy(self.screen, j * 50, i * 50 + 10, 10, 1, 'enemy.png'))
                    self.walls.append(Wall(j * 50, i * 50))
                    self.units.append(self.walls[-1])
                elif self.map[i][j] == 's':
                    self.spikes.append(Spike(self.screen, j * 50, i * 50))
                    self.walls.append(Wall(j * 50, i * 50))
                    self.units.append(self.walls[-1])
                elif self.map[i][j] == 'D':
                    self.portal = Exit(j * 50, i * 50)
                elif self.map[i][j] == 'T':
                    self.ship = Ship(j * 50, i * 50)
                    self.walls.append(Wall(j * 50, i * 50))
                    self.units.append(self.walls[-1])


class Exit():
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)
        self.entity = pygame.sprite.Group(self)

    def render(self, screen):
        self.entity.draw(screen)


class FloorBrick(pygame.sprite.Sprite):
    image = pygame.image.load('images/floor.jpg')

    def __init__(self, x, y):
        super().__init__()
        self.image = FloorBrick.image
        self.floors = []
        self.walls = []
        self.walls.append(pygame.Rect(x, y + 4, 20, 42))
        self.walls.append(pygame.Rect(x + 30, y + 4, 20, 42))
        self.floors.append(pygame.Rect(x, y, 50, 20))
        self.floors.append(pygame.Rect(x, y + 30, 50, 20))
        self.entinty = pygame.sprite.Group(self)
        self.rect = self.image.get_rect().move(x, y)

    def render(self, screen):
        self.entinty.draw(screen)


class KillBlock(pygame.sprite.Sprite):
    image = pygame.image.load('images/floor.jpg')

    def __init__(self, x, y):
        super().__init__()
        self.image = KillBlock.image
        self.rect = self.image.get_rect().move(x, y)
        self.entity = pygame.sprite.Group(self)

    def render(self, screen):
        self.entity.draw(screen)


class InfoText():
    def __init__(self):
        self.f_text = lambda x, y: f'SCORE: {x}; HP: {y}'

    def render(self, screen: pygame.Surface, score, hp):
        screen.blit(pygame.font.SysFont('couriernew', 40).render(self.f_text(score, hp), True, 'black'), (50, 50))


class Wall(pygame.sprite.Sprite):
    image = pygame.image.load('images/wall.png')

    def __init__(self, x, y):
        super().__init__()
        self.image = Wall.image
        self.entity = pygame.sprite.Group(self)
        self.rect = self.image.get_rect().move(x, y)

    def render(self, screen):
        self.entity.draw(screen)


class SpaceGuy(pygame.sprite.Sprite):
    image = pygame.image.load('images/man1.png')

    def __init__(self, screen: pygame.Surface, x, y):
        super().__init__()
        self.looking_left = True
        self.image = SpaceGuy.image
        self.rect = self.image.get_rect().move(x, y)
        self.entity = pygame.sprite.Group(self)
        self.mask = pygame.mask.from_surface(self.image)
        self.screen = screen
        self.health = 11
        self.acceleration = 10
        self.max_velosity = 10
        self.current_velosity = 0
        self.moves = {pygame.K_a: -1, pygame.K_d: 1}
        self.jump_speed = 0
        self.jump_acceleration = 9.8
        self.jump_pulce = -5
        self.damage = Attack(self, screen)
        self.dmg = 1
        self.immortal_time = 0
        self.cooldown = 0

    def render(self, screen):
        """Отрисовка"""
        self.entity.draw(screen)

    def move(self, key, time, collide_floor, collide_wall):
        if key[pygame.K_a] or key[pygame.K_d]:
            self.current_velosity += self.acceleration * (
                    self.moves[pygame.K_a] * key[pygame.K_a] * time + self.moves[pygame.K_d] * key[pygame.K_d] * time)
            if abs(self.current_velosity) > self.max_velosity:
                self.current_velosity = self.max_velosity
        else:
            if self.current_velosity < 0:
                self.current_velosity += self.acceleration * time
                if self.current_velosity > 0:
                    self.current_velosity = 0
            elif self.current_velosity > 0:
                self.current_velosity -= self.acceleration * time
                if self.current_velosity < 0:
                    self.current_velosity = 0
        if collide_wall:
            self.current_velosity = 0

        self.rect = self.rect.move(self.current_velosity, 0)

        self.jump_speed += 9.8 * time
        if collide_floor:
            self.jump_speed = 0
        if key[pygame.K_SPACE]:
            if collide_floor:
                self.jump_speed += self.jump_pulce if self.jump_speed == 0 else 0
        self.rect = self.rect.move(0, self.jump_speed)

        if self.looking_left and key[pygame.K_a]:
            self.image = pygame.transform.flip(self.image, True, False)
            self.looking_left = not self.looking_left
        elif not self.looking_left and key[pygame.K_d]:
            self.image = pygame.transform.flip(self.image, True, False)
            self.looking_left = not self.looking_left

        if self.immortal_time > 0:
            self.immortal_time -= time

        if self.cooldown > 0:
            self.cooldown -= time

        self.damage.check(time)

    def get_damage(self, damage):
        if self.immortal_time <= 0:
            self.health -= damage
            self.immortal_time = 1

    def attack(self, pressed_keys):
        if pressed_keys[pygame.K_r]:
            if self.cooldown <= 0:
                self.cooldown = 0.5
                self.damage.time += 0.3
                self.damage.attack()


class Attack(pygame.sprite.Sprite):
    image = pygame.image.load('images\damage.png')

    def __init__(self, player: SpaceGuy, surface):
        super().__init__()
        self.image = Attack.image
        self.rect = self.image.get_rect()
        self.player = player
        self.entity = pygame.sprite.Group(self)
        self.time = 0
        self.looking_left = True

    def check(self, time):
        if self.time > 0:
            self.time -= time

    def attack(self):
        if self.looking_left != self.player.looking_left:
            self.looking_left = self.player.looking_left
            self.image = pygame.transform.flip(self.image, True, False)
        if not self.looking_left:
            self.rect.x, self.rect.y = self.player.rect.x - 12, self.player.rect.y - 18
        else:
            self.rect.x, self.rect.y = self.player.rect.x + 12, self.player.rect.y - 18

    def render(self, screen):
        if self.time > 0:
            print(self.rect.center)
            self.attack()
            self.entity.draw(screen)


class Enemy(pygame.sprite.Sprite):

    def __init__(self, screen, x, y, hp, damage, image):
        super().__init__()
        self.image = pygame.image.load('images/' + image)
        self.rect = self.image.get_rect().move(x, y)
        self.entity = pygame.sprite.Group(self)

        self.hp = hp
        self.damage = damage

        self.velosity = random.choice([-1, 1])
        if self.velosity == -1:
            self.image = pygame.transform.flip(self.image, True, False)
            self.rect = self.image.get_rect().move(self.rect.x, self.rect.y)

    def render(self, screen):
        if self.hp > 0:
            self.entity.draw(screen)

    def move(self, time):
        self.rect = self.rect.move(self.velosity * time, 0)

    def collided(self):
        self.velosity *= -1
        self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect().move(self.rect.x, self.rect.y)

    def get_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.damage = 0
            self.velosity = 0


class Spike(Enemy):
    def __init__(self, screen, x, y):
        super().__init__(screen, x, y, 10000000, 2, 'spike.png')


class Ship(pygame.sprite.Sprite):
    image = pygame.image.load('images/ship.png')

    def __init__(self, x, y):
        super().__init__()
        self.image = Ship.image
        self.group = pygame.sprite.Group(self)
        self.rect = self.image.get_rect().move(x, y)

    def render(self, screen):
        self.group.draw(screen)

    def collided(self):
        pass
