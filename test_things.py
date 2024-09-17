import random
import sys

import pygame

LASER_SPAWN = pygame.USEREVENT + 1
DELETE_LASER = pygame.USEREVENT + 2


def generate_object_cord():
    """Функция для создания координат вне экрана"""
    sides = ["left", "right", "up", "down"]
    res = []

    side1 = random.choice(sides)
    side2 = random.choice(sides)
    while side2 == side1:
        side2 = random.choice(sides)

    for side in (side1, side2):
        if side == 'left':
            res.append((-5, random.randint(-10, 550)))
        elif side == 'right':
            res.append((965, random.randint(-10, 550)))
        elif side == 'up':
            res.append((random.randint(-10, 960), -5))
        elif side == 'down':
            res.append((random.randint(-10, 960), 555))

    return res


class SpaceGuy:

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.rect = pygame.Rect(*screen.get_rect().center, 30, 50)
        self.health = 3
        self.acceleration = 20
        self.max_velosity = 30
        self.current_velosity = 0
        self.moves = {pygame.K_a: -1, pygame.K_d: 1}
        self.jump_speed = 0
        self.jump_acceleration = 9.8
        self.jump_pulce = -600

    def render(self):
        """Отрисовка"""
        pygame.draw.rect(screen, pygame.Color("black"), self.rect)

    def move(self, key, time):
        if key[pygame.K_a] or key[pygame.K_d] or key[pygame.K_HOME] or key[pygame.K_END]:
            self.current_velosity += self.acceleration * (self.moves[pygame.K_a] *
                                                          (key[pygame.K_a] or key[pygame.K_HOME]) +
                                                          self.moves[pygame.K_d] *
                                                          (key[pygame.K_d] or key[pygame.K_END])) * time
            if abs(self.current_velosity) > self.max_velosity:
                self.current_velosity = self.max_velosity
        else:
            if self.current_velosity < 0:
                self.current_velosity += 20 * time
                if self.current_velosity > 0:
                    self.current_velosity = 0
            elif self.current_velosity > 0:
                self.current_velosity -= 20 * time
                if self.current_velosity < 0:
                    self.current_velosity = 0

        self.rect = self.rect.move(self.current_velosity, 0)
        if key[pygame.K_SPACE]:
            if self.rect.y == 460:
                self.jump_speed += self.jump_pulce
                print(self.jump_speed, self.jump_acceleration)
        if self.rect.y < 460:
            self.jump_speed += self.jump_acceleration * time * 100
        self.rect = self.rect.move(0, self.jump_speed * time)
        if self.rect.y > 460:
            self.rect.y = 460
            self.jump_speed = 0

    def take_damage(self, damage):
        self.health += damage


class Floor:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.rect = pygame.Rect(0, 900, 540, 60)


if __name__ == '__main__':
    pygame.init()

    size = height, width = 960, 540
    screen = pygame.display.set_mode(size)

    guy = SpaceGuy(screen)

    bullets = []

    fps = 100
    running = True
    clock = pygame.time.Clock()

    taken_hit_tick = 0

    while running:

        screen.fill((255, 255, 255))

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        clock.tick(fps)

        guy.move(pygame.key.get_pressed(), 1 / fps)
        guy.render()

        if guy.health <= 0:
            sys.exit()

        pygame.display.flip()
