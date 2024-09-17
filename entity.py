import pygame
import random

LASER_SPAWN = pygame.USEREVENT + 1
DELETE_LASER = pygame.USEREVENT + 2
BULLET_SPAWN = pygame.USEREVENT + 3
STOMP_SPAWN = pygame.USEREVENT + 4
LIFE_TIME = pygame.USEREVENT + 5


class SpaceShip(pygame.sprite.Sprite):
    image = pygame.image.load('images/ship.png')

    def __init__(self, screen: pygame.Surface, *groups):
        super().__init__(*groups)
        self.screen = screen
        self.image = SpaceShip.image
        self.rect = self.image.get_rect()
        self.health = 3
        self.velocity = 3
        self.invisibility = 0
        self.color = pygame.Color((255, 255, 255))

        self.entity = pygame.sprite.Group(self)

        self.mask = pygame.mask.from_surface(self.image)

        self.timer = 0
        self.up = True

    def render(self):
        """Отрисовка"""
        self.entity.draw(self.screen)

    def move_ip(self, key):
        """Передвижение персонажа"""
        up = key[pygame.K_w] or key[pygame.K_UP]
        down = key[pygame.K_s] or key[pygame.K_DOWN]
        left = key[pygame.K_a] or key[pygame.K_LEFT]
        right = key[pygame.K_d] or key[pygame.K_RIGHT]

        move = pygame.math.Vector2(right - left, down - up)
        if move.length_squared() > 0:
            move.scale_to_length(self.velocity)
            self.rect.move_ip(round(move.x), round(move.y))

        self.rect.clamp_ip(self.screen.get_rect())

    def take_damage(self, damage):
        if damage:
            self.health -= damage
            self.invisibility = 1

    def update(self):
        self.flashing()

    def flashing(self):
        """Сделать мерцание персонажа при получении урона"""
        if self.invisibility > 0:
            self.timer += 1

            if self.timer == 10:
                self.timer = 0
                self.up = not self.up

            if self.up:
                self.image.set_alpha(0)
            else:
                self.image.set_alpha(255)

        else:
            self.image.set_alpha(255)


class Laser:

    def __init__(self, screen: pygame.Surface):
        self.screen = screen

        self.start_pos = None
        self.end_pos = None
        self.generate_cord()

        self.black_to_red_mult = 0
        self.flash_color = [234, 26, 26]
        self.white_to_black_color = [255, 255, 255]
        self.line_width = 0

        self.color = [234 * self.black_to_red_mult, 26 * self.black_to_red_mult, 26 * self.black_to_red_mult]

        self.phase_end = False

    def render(self):
        """Отрисовка"""
        if self.black_to_red_mult < 1:
            pygame.draw.line(self.screen, self.color, self.start_pos, self.end_pos, int(self.line_width))
        elif self.flash_color[0] <= 253.95:
            pygame.draw.line(self.screen, self.flash_color, self.start_pos, self.end_pos, int(self.line_width))
        else:
            pygame.draw.line(self.screen, self.white_to_black_color, self.start_pos, self.end_pos, int(self.line_width))

    def update(self):
        if self.black_to_red_mult < 1:
            self.fade_black_to_red()
            self.increase_width()

        elif self.flash_color[0] <= 253.95:
            self.fade_red_to_white()

        else:
            self.fade_white_to_black()
            self.decrease_width()

    def fade_red_to_white(self):
        if self.flash_color[0] <= 253.95:
            self.flash_color[0] += 1.05
            self.flash_color[1] += 11.45
            self.flash_color[2] += 11.45

    def fade_white_to_black(self):
        if self.white_to_black_color[0] >= 25.5:
            for i in range(3):
                self.white_to_black_color[i] -= 25.5

        else:
            self.phase_end = True

    def increase_width(self):
        self.line_width += 0.05

    def decrease_width(self):
        self.line_width -= 0.5

    def fade_black_to_red(self):
        """Плавный переход от черного к красному"""
        self.black_to_red_mult += 0.01 if self.black_to_red_mult < 1 else 0
        self.color = [234 * self.black_to_red_mult, 26 * self.black_to_red_mult, 26 * self.black_to_red_mult]

    def is_phase_end(self):
        """Функция для проверки готовности к удалению"""
        return self.phase_end

    def damage_player(self, player_rect):
        if player_rect.rect.clipline(*self.start_pos, *self.end_pos) and self.phase_end:
            return 1
        return 0

    def generate_cord(self):
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

        self.start_pos, self.end_pos = res


class Bullet:

    def __init__(self, screen: pygame.Surface, despawn_area: pygame.Rect):

        self.screen = screen
        self.despawn_area = despawn_area

        self.start_pos = None
        self.direction = None

        self.velocity = 3
        self.radius = 10
        self.rect = pygame.Rect(0, 0, 10, 10)

        self.color = pygame.Color([234, 26, 26])

        self.phase_end = False

        self.generate_cord()

    def render(self):
        pygame.draw.ellipse(self.screen, self.color, self.rect, 0)

    def update(self):
        self.rect.move_ip(self.direction.x, self.direction.y)

        if not self.despawn_area.contains(self.rect):
            self.phase_end = True

    def is_phase_end(self):
        """Функция для проверки готовности к удалению"""
        return self.phase_end

    def damage_player(self, player_rect):
        if player_rect.rect.colliderect(self.rect):
            return 1
        return 0

    def generate_cord(self):
        """Функция для создания координат вне экрана"""
        sides = ["left", "right", "up", "down"]

        side = random.choice(sides)

        if side == 'left':
            self.start_pos = -5, random.randint(-10, 550),
            self.direction = pygame.math.Vector2(random.randint(1, 100) / 100, random.randint(-100, 100) / 100)

        elif side == 'right':
            self.start_pos = 965, random.randint(-10, 550),
            self.direction = pygame.math.Vector2(random.randint(-100, 1) / 100, random.randint(-100, 100) / 100)

        elif side == 'up':
            self.start_pos = random.randint(-10, 960), -5,
            self.direction = pygame.math.Vector2(random.randint(-100, 100) / 100, random.randint(1, 100) / 100)

        elif side == 'down':
            self.start_pos = random.randint(-10, 960), 555
            self.direction = pygame.math.Vector2(random.randint(-100, 100) / 100, random.randint(-100, 1) / 100)

        self.direction.scale_to_length(self.velocity)
        self.rect.center = self.start_pos


class Stomp(pygame.sprite.Sprite):
    image = pygame.image.load('images/circle.png')

    def __init__(self, screen: pygame.Surface, *groups):

        super().__init__(*groups)
        self.screen = screen

        self.pos = None
        self.generate_cord()
        self.radius = 1

        self.mask = pygame.mask.from_surface(self.image)

        self.color = [234, 26, 26]
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.rect.center = self.pos
        self.phase_end = False

    def generate_cord(self):
        self.pos = (random.randint(-100, self.screen.get_width() - 100), random.randint(-100, self.screen.get_height()) - 100)

    def render(self):
        pygame.draw.circle(self.screen, self.color, (self.pos[0] + 100, self.pos[1] + 100), self.radius)

    def update(self):
        if self.radius < 100:
            self.radius += 0.5
        else:
            self.phase_end = True

    def is_phase_end(self):
        return self.phase_end

    def damage_player(self, player_rect):
        if pygame.sprite.collide_mask(self, player_rect) and self.phase_end:
            return 1
        return 0



