import pygame
from pygame.locals import *
from pygame.sprite import Sprite

from math import sqrt
from random import choices, random, randrange

import settings as st

class Weapon:

    def __init__(self, name, bullets, side_bullets, max_bullets_per_shoot, delay_between_bullets, reload_time, magazine, full_auto):
        self.name = name

        self.mag_cap = bullets
        self.bullets = bullets
        self.side_bullets = side_bullets

        self.max_bullets_per_shoot = max_bullets_per_shoot
        self.delay_between_bullets = delay_between_bullets
        self.shooting = False
        self.bullet_shot = 0

        self.max_reload_sfx_rep = int(reload_time / 250)
        self.reload_sfx_rep = 0
        self.reloading = False

        self.bullet_srf = magazine[0]
        self.mag_col = magazine[1]

        self.full_auto = full_auto

    def draw_bullets(self, screen):
        bullet_size = self.bullet_srf.get_size()
        bullet_rect = self.bullet_srf.get_rect()

        bullets_per_col = int(self.mag_cap / self.mag_col)
        if self.mag_cap % self.mag_col:
            bullets_per_col += 1
        temp_bullets = self.bullets

        for col in range(self.mag_col):
            bullets_col = bullets_per_col if temp_bullets >= bullets_per_col else temp_bullets
            temp_bullets -= bullets_col
            for i in range(bullets_col):
                bullet_rect.bottomleft = (bullet_size[0] * (5 / 4) * col + 10,
                                          st.screen_height - 10 - (bullet_size[1] * (5 / 4) * i))

                screen.blit(self.bullet_srf, bullet_rect)

        name_srf = st.font_normal25.render(f"{self.name}", True, st.DARK_GRAY)
        name_rect = name_srf.get_rect()
        name_rect.bottomleft = (bullet_size[0] * (5 / 4) * self.mag_col + 15,
                                st.screen_height - 10)

        bullets_number_srf = st.font_bold40.render(f"{self.bullets}/{self.side_bullets}", True, st.DARK_GRAY)
        bullets_number_rect = bullets_number_srf.get_rect()
        bullets_number_rect.bottomleft = (bullet_size[0] * (5 / 4) * self.mag_col + 15,
                                          st.screen_height - 30)

        screen.blit(bullets_number_srf, bullets_number_rect)
        screen.blit(name_srf, name_rect)

    def shoot(self, target_group):
        if not self.bullets:
            st.noammo_sfx.play()
        elif self.shooting and not self.reloading:
            st.shoot_sfx.play()

            self.bullets -= 1
            self.bullet_shot += 1
            event = pygame.event.Event(USEREVENT + 3)
            pygame.event.post(event)

            accuracy = 0
            for target in target_group:
                if target.rect.collidepoint(mouse_pos := pygame.mouse.get_pos()):
                    accuracy = 1
                    target.hit(self, mouse_pos)
            if not accuracy:
                event = pygame.event.Event(USEREVENT + 4, target_hit=0, accuracy=0, score_increment=0, bullet_increment=0)
                pygame.event.post(event)

            if self.bullet_shot == self.max_bullets_per_shoot:
                self.bullet_shot = 0
                self.shooting = False

            pygame.time.set_timer(USEREVENT, self.delay_between_bullets, True)

    def reload(self):
        if self.reloading:
            st.reload_sfx.set_volume(random())
            st.reload_sfx.play()

            self.reload_sfx_rep += 1
            if self.reload_sfx_rep == self.max_reload_sfx_rep:
                all_bullets = self.bullets + self.side_bullets
                self.bullets = self.mag_cap if all_bullets >= self.mag_cap else all_bullets
                self.side_bullets = all_bullets - self.bullets

                self.reload_sfx_rep = 0
                self.reloading = False
                st.reload_end_sfx.play()

            pygame.time.set_timer(USEREVENT + 1, 250, True)


class Target(Sprite):

    def __init__(self, screen, group):
        super().__init__()

        self.target_type = choices([1, 2, 3], weights=st.target_weights)[0]

        self.screen = screen
        self.group = group

        if self.target_type == 1:
            self.srf = st.target1_srf
        elif self.target_type == 2:
            self.srf = st.target2_srf
        elif self.target_type == 3:
            self.srf = st.target3_srf

        size = self.srf.get_size()
        self.rect = self.srf.get_rect()

        self.x = randrange(int(size[0] / 2), st.screen_width - int(size[0] / 2))
        self.y = randrange(int(size[1] / 2), st.screen_height - int(size[1] / 2))
        self.rect.center = (self.x, self.y)

        self.life = 300

    def draw(self):
        self.screen.blit(self.srf, self.rect)

    def update(self):
        self.life -= 1
        if self.life <= 0:
            st.target_lost_sfx.play()
            self.group.remove(self)
            event = pygame.event.Event(USEREVENT + 6)
            pygame.event.post(event)

    def hit(self, current_weapon, mouse_pos):
        # global target_hit, score, highscore, level, target_spawn, side_bullets

        distance_x = abs(self.x - mouse_pos[0])
        distance_y = abs(self.y - mouse_pos[1])
        distance = sqrt(distance_x ** 2 + distance_y ** 2)

        accuracy = 0
        score_increment = 0
        bullet_increment = 0

        if distance <= 24:
            self.group.remove(self)

            accuracy = round((24 - distance) / 24 * 100, 2)

            score_increment = round((self.life / 60) * ((25 - distance) if distance <= 24 else 1)) if self.target_type == 1 else 0  # max = 5 * 25 = 125
            bullet_increment = int((25 - distance) / 2) if self.target_type == 2 else 0
            if self.target_type == 3:
                add_weapon_event = pygame.event.Event(USEREVENT + 5)
                pygame.event.post(add_weapon_event)

        event = pygame.event.Event(USEREVENT + 4, target_hit=1, accuracy=accuracy, score_increment=score_increment, bullet_increment=bullet_increment)
        pygame.event.post(event)
