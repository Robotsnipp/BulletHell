from game_1 import *

if __name__ == '__main__':
    pygame.init()

    map = Map('test.txt')

    guy = map.player
    enemies = map.enemies
    fps = 100
    running = True
    clock = pygame.time.Clock()

    taken_hit_tick = 0

    score = 0

    while running:
        c_w = False
        c_f = False
        map.screen.fill((255, 255, 255))

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        for unit in map.units:
            unit.render(map.screen)

        for spike in map.spikes:
            spike.render(map.screen)
            if spike.rect.colliderect(guy.rect):
                guy.get_damage(spike.damage)

        for en in enemies:
            if guy.rect.colliderect(en.rect):
                guy.get_damage(en.damage)
            if guy.damage.rect.colliderect(en.rect):
                en.get_damage(guy.dmg)
                if en.hp <= 0:
                    score += 100
            en.render(map.screen)
            en.move(1)

            for floor_block in map.floor:
                if en.rect.collidelist(floor_block.walls):
                    en.collided()

        map.ship.render(map.screen)
        if guy.rect.colliderect(map.ship.rect):
            spawn_program_and_die('main.py')

        map.portal.render()
        if guy.rect.colliderect(map.portal.rect):
            spawn_program_and_die('main.py')

        guy.render(map.screen)
        guy.damage.render(map.screen)
        clock.tick(fps)

        if any([guy.rect.collidelist(i.floors) != -1 for i in map.floor]):
            c_f = True
        if any([guy.rect.collidelist(i.walls) != -1 for i in map.floor]):
            c_w = True

        guy.move(pygame.key.get_pressed(), 1 / fps, c_f, c_w)
        guy.attack(pygame.key.get_pressed())

        if map.width > 1000:

            if not 100 < guy.rect.centerx < 900:
                if guy.rect.centerx > 200:
                    dir = -1
                else:
                    dir = 1
                dir *= guy.max_velosity
                guy.rect = guy.rect.move(dir, 0)
                for en in enemies:
                    en.rect = en.rect.move(dir, 0)
                for unit in map.units:
                    unit.rect = unit.rect.move(dir, 0)
                for spike in map.spikes:
                    spike.rect = spike.rect.move(dir, 0)

        else:
            while not 100 < guy.rect.centerx < map.width - 100:
                if not 100 < guy.rect.centerx < map.width - 100:
                    dir = -1
                else:
                    dir = 1
                dir *= guy.max_velosity
                for en in enemies:
                    en.rect = en.rect.move(dir, 0)
                for unit in map.units:
                    unit.rect = unit.rect.move(dir, 0)
                for spike in map.spikes:
                    spike.rect = spike.rect.move(dir, 0)

        map.text.render(map.screen, score, guy.health)

        if guy.health <= 0:
            sys.exit()

        pygame.display.flip()
