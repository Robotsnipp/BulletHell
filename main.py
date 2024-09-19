import sys

from entity import *


if __name__ == '__main__':
    pygame.init()
    pygame.font.init()

    size = height, width = 960, 540
    screen = pygame.display.set_mode(size)
    despawn_area = pygame.Rect(-100, -100, 1300, 1300)

    game_font = pygame.font.SysFont('Franklin Gothic', 70)
    debugger_font = pygame.font.SysFont('Franklin Gothic', 20)

    taken_hit_tick = 0
    lifetime = 0
    death_screen_time = 1.0 # seconds

    bullets = []
    ship = SpaceShip(screen)
    ship.rect.center = (480, 270)
    endgame_phase = None

    fps = 100
    running = True
    clock = pygame.time.Clock()

    heart_image = pygame.image.load('images/heart.png')
    heart_image.set_colorkey((0, 0, 0))

    # ---- SPAWNER ----
    pygame.time.set_timer(LASER_SPAWN, 100)
    pygame.time.set_timer(BULLET_SPAWN, 100)
    pygame.time.set_timer(STOMP_SPAWN, 1000)
    pygame.time.set_timer(LIFE_TIME, 1000)

    # ---- GAME ----
    while running:

        taken_hit_tick -= 0.05 if taken_hit_tick > 0 else 0
        screen.fill((255 * taken_hit_tick, 255 * taken_hit_tick, 255 * taken_hit_tick))

        # ---- EVENT HANDLER ----
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == LIFE_TIME:
                lifetime += 1

            if not endgame_phase:

                if event.type == LASER_SPAWN:
                    bullets.append(Laser(screen))

                if event.type == BULLET_SPAWN:
                    bullets.append(Bullet(screen, despawn_area))

                if event.type == STOMP_SPAWN:
                    bullets.append(Stomp(screen))

        # ---- BULLETS MOMENT ----
        if endgame_phase not in [WIN, LOSE]:
            for i, bullet in enumerate(bullets[::-1]):

                damage = bullet.damage_player(ship)

                if damage and ship.invisibility <= 0:
                    ship.take_damage(damage)
                    taken_hit_tick = damage

                if bullet.is_phase_end():
                    del bullets[bullets.index(bullet)]

                bullet.update()
                bullet.render()

        # ---- SHIP MOMENT ----
        ship.move_ip(pygame.key.get_pressed())
        ship.update()
        ship.render()

        ship.invisibility -= 0.01
        if ship.health == 0:
            death_screen_time -= 0.01

        # ---- UI MOMENT ----
        hp_text = game_font.render(str(ship.health), False, pygame.Color('red'))
        timer_text = game_font.render(str(lifetime), False, pygame.Color('red'))
        entity_count_text = debugger_font.render(f"entity count: {len(bullets)}", False, pygame.Color("purple"))

        screen.blit(hp_text, (520, 10))
        screen.blit(timer_text, (400, 10))
        screen.blit(entity_count_text, (10, 520))
        screen.blit(pygame.transform.scale(heart_image, (70, 70)), (460, -3))

        # ---- ENDGAME PHASE ----
        if endgame_phase is None:
            if lifetime >= 30 and ship.health != 0:
                endgame_phase = WIN

            if ship.health == 0:
                endgame_phase = LOSE

        if endgame_phase == WIN:
            bullets = []
            win_text = game_font.render('YOU HAVE WON', False, pygame.Color('red'))
            screen.blit(win_text, (275, 250))

        if endgame_phase == LOSE:
            bullets = []
            sys.exit()

        # ---- FPS ----
        clock.tick(fps)
        pygame.display.flip()
