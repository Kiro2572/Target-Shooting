import pygame
from pygame.locals import *
from pygame.sprite import Group

from math import sqrt
from random import choice, choices, random

import objects as obj
import settings as st

# === STATISTICS =================
with open("assets/statistics.txt") as f:
    stats = (i[i.find("=") + 1:].strip() for i in f.readlines())

stat_highscore = int(next(stats))
stat_accuracy = float(next(stats))
stat_shoot_number = int(next(stats))
stat_target_hit = int(next(stats))
# ================================

# === DYNAMIC VARS ===============
highscore = stat_highscore
accuracy = 0
shoot_number = 0
target_hit = 0

level = 1
score = 0

target_spawn = 2500
target_lost = 0
# ================================

# === WEAPONS ====================
weapons = []
weapons.append(obj.Weapon(*st.revolver))
# weapons.append(obj.Weapon(*st.handgun))
# weapons.append(obj.Weapon(*st.rifle))
# weapons.append(obj.Weapon(*st.machine_gun))
weapon_index = 0
current_weapon = weapons[weapon_index]


def change_weapon(i):
    global weapon_index, current_weapon

    if current_weapon.reloading:
        current_weapon.reloading = False
    if current_weapon.shooting:
        current_weapon.shooting = False

    weapon_index = weapon_index + i if len(weapons) > 1 else 0
    try:
        current_weapon = weapons[weapon_index]
        st.change_weapon_sfx.play()
    except IndexError:
        weapon_index -= len(weapons) * i
        current_weapon = weapons[weapon_index]
        st.change_weapon_sfx.play()


def add_weapon():
    weapon_names = [i.name for i in weapons]
    new_weapon = obj.Weapon(*choices(st.weapons, weights=st.weapon_weights)[0])

    try:
        index = weapon_names.index(new_weapon.name)
        owned_weapon = weapons[index]
        owned_weapon.side_bullets += int(new_weapon.side_bullets / 2)
    except ValueError:
        weapons.append(new_weapon)


def check_weapon():
    global weapon_index

    if not current_weapon.bullets and not current_weapon.side_bullets:
        weapons.remove(current_weapon)
        try:
            change_weapon(1)
            change_weapon(-1)
        except IndexError:
            pass
# ================================


# === FUNCTIONS ==================
def new_game(screen, clock):
    global highscore, accuracy, shoot_number, target_hit
    global level, score, target_spawn, target_lost
    global weapons, weapon_index, current_weapon

    highscore = stat_highscore
    accuracy = 0
    shoot_number = 0
    target_hit = 0

    level = 1
    score = 10000

    target_spawn = 2500
    target_lost = 0

    weapons = []
    weapons.append(obj.Weapon(*st.revolver))
    weapon_index = 0
    current_weapon = weapons[weapon_index]

    gameloop(screen, clock)


def check_lose(screen, clock):
    if score < 0:
        game_over(screen, clock)
    if not weapons:
        game_over(screen, clock)
    if target_lost == 20:
        game_over(screen, clock)


def save_stats():
    with open("assets/statistics.txt", "w") as f:
        f.write(f"highscore = {highscore}\n")
        f.write(f"accuracy = {accuracy if accuracy > stat_accuracy else stat_accuracy}\n")
        f.write(f"shoot_number = {shoot_number}\n")
        f.write(f"target_hit = {target_hit}")


def quit_game():
    pygame.quit()
    quit()


def draw_score(screen):
    score_srf = st.font_bold120.render(f"{score}", True, st.GRAY)
    score_rect = score_srf.get_rect()
    score_rect.center = (st.screen_width / 2, st.screen_height / 2)

    highscore_srf = st.font_normal30.render(f"Highscore: {highscore}", True, st.GRAY)
    highscore_rect = highscore_srf.get_rect()
    highscore_rect.center = (st.screen_width / 2, st.screen_height / 2 - 50)

    accuracy_srf = st.font_normal30.render(f"Accuracy: {accuracy}%", True, st.GRAY)
    accuracy_rect = accuracy_srf.get_rect()
    accuracy_rect.center = (st.screen_width / 2, st.screen_height / 2 + 50)

    screen.blit(score_srf, score_rect)
    screen.blit(highscore_srf, highscore_rect)
    screen.blit(accuracy_srf, accuracy_rect)


def event_handler(screen, target_group, clock):
    global highscore, accuracy, shoot_number, target_hit, score, level, target_spawn, target_lost

    for event in pygame.event.get():
        if event.type == QUIT:
            save_stats()
            quit_game()

        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                pause(screen, clock)

        if event.type == MOUSEWHEEL and len(weapons) > 1:
            change_weapon(event.y)

        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                current_weapon.shooting = True
                current_weapon.shoot(target_group)
            if event.button == 3:
                if current_weapon.bullets < current_weapon.mag_cap and not current_weapon.reloading and current_weapon.side_bullets:
                    current_weapon.reloading = True
                    current_weapon.reload()

        if event.type == MOUSEBUTTONUP:
            if event.button == 1:
                if not current_weapon.full_auto:
                    current_weapon.shooting = False
                    current_weapon.bullet_shot = 0

        if event.type == USEREVENT:
            current_weapon.shoot(target_group)
        if event.type == USEREVENT + 1:
            current_weapon.reload()
        if event.type == USEREVENT + 2:
            new_target = obj.Target(screen, target_group)
            target_group.add(new_target)
        if event.type == USEREVENT + 3:
            shoot_number += 1
        if event.type == USEREVENT + 4:
            target_hit += event.target_hit

            score += event.score_increment
            current_weapon.side_bullets += event.bullet_increment

            accuracy = round((accuracy + event.accuracy) / 2, 2) if accuracy else event.accuracy
            highscore = score if score >= highscore else highscore
            if score >= level * st.level_mult:
                level += 1
                target_spawn = int(target_spawn * st.target_spawn_mult)
                pygame.time.set_timer(USEREVENT + 2, target_spawn)

        if event.type == USEREVENT + 5:
            add_weapon()
        if event.type == USEREVENT + 6 and target_hit:
            target_lost += 1
            score -= target_lost * st.target_lost_penalty
# ================================


# === LOOPS ======================
def home():
    pygame.init()
    clock = pygame.time.Clock()

    pygame.display.set_caption("Target")
    pygame.display.set_icon(st.icon)
    screen = pygame.display.set_mode((st.screen_width, st.screen_height))

    pygame.mouse.set_cursor((16, 16), (8, 8), *st.crosshair)

    logo_srf = st.logo
    logo_rect = logo_srf.get_rect()
    logo_rect.center = (225, 180)

    text_srf = st.font_corbel_bold85.render("TARGET", True, st.DARK_GRAY)
    text_rect = text_srf.get_rect()
    text_rect.bottomleft = (80, st.screen_height / 2 + 100)

    play_srf = st.font_corbel_bold50.render("Play", True, st.MED_GRAY)
    play_rect = play_srf.get_rect()
    play_rect.bottomleft = (130, st.screen_height / 2 + 170)

    quit_srf = st.font_corbel_bold50.render("Quit", True, st.MED_RED)
    quit_rect = quit_srf.get_rect()
    quit_rect.bottomleft = (130, st.screen_height / 2 + 230)

    bullet_holes = []

    with open("assets/instruction.txt") as f:
        instructions = [i.rstrip() for i in f.readlines()[::-1]]

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                quit_game()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    st.shoot_sfx.play()
                    if play_rect.collidepoint(pygame.mouse.get_pos()):
                        new_game(screen, clock)
                    if quit_rect.collidepoint(pygame.mouse.get_pos()):
                        pygame.quit()
                        quit()
                    if logo_rect.collidepoint(mouse_pos := pygame.mouse.get_pos()):
                        distance_x = abs(logo_rect.center[0] - mouse_pos[0])
                        distance_y = abs(logo_rect.center[1] - mouse_pos[1])
                        distance = sqrt(distance_x ** 2 + distance_y ** 2)

                        if distance <= 100:
                            bullet_holes.append(mouse_pos)

                if event.button == 3:
                    st.full_reload_sfx.play()
                    bullet_holes = []

        screen.fill(st.bg_color)

        screen.blit(logo_srf, logo_rect)
        for coord in bullet_holes:
            pygame.draw.circle(screen, st.BLACK, coord, 5)

        screen.blit(text_srf, text_rect)
        screen.blit(play_srf, play_rect)
        screen.blit(quit_srf, quit_rect)

        for i in range(len(instructions)):
            instruction_srf = st.font_consolas_normal18.render(instructions[i], True, st.DARK_GRAY)
            instruction_rect = instruction_srf.get_rect()
            instruction_rect.bottomleft = (st.screen_width / 2 - 60, st.screen_height - (25 * i + 70))
            screen.blit(instruction_srf, instruction_rect)

        pygame.display.update()


def gameloop(screen, clock):
    target_group = Group()
    pygame.time.set_timer(USEREVENT + 2, target_spawn)

    while True:
        event_handler(screen, target_group, clock)

        screen.fill(st.bg_color)
        draw_score(screen)
        for target in target_group:
            target.draw()
        current_weapon.draw_bullets(screen)

        check_weapon()
        check_lose(screen, clock)
        target_group.update()

        pygame.display.update()
        clock.tick(60)


def pause(screen, clock):
    text_srf = st.font_corbel_bold85.render("PAUSED", True, st.DARK_GRAY)
    text_rect = text_srf.get_rect()
    text_rect.bottomleft = (80, st.screen_height / 2 - 20)

    continue_srf = st.font_corbel_bold50.render("Continue", True, st.MED_GRAY)
    continue_rect = continue_srf.get_rect()
    continue_rect.bottomleft = (130, st.screen_height / 2 + 50)

    replay_srf = st.font_corbel_bold50.render("Replay", True, st.MED_GRAY)
    replay_rect = replay_srf.get_rect()
    replay_rect.bottomleft = (130, st.screen_height / 2 + 110)

    home_srf = st.font_corbel_bold50.render("Home", True, st.MED_GRAY)
    home_rect = home_srf.get_rect()
    home_rect.bottomleft = (130, st.screen_height / 2 + 170)

    quit_srf = st.font_corbel_bold50.render("Quit", True, st.MED_RED)
    quit_rect = quit_srf.get_rect()
    quit_rect.bottomleft = (130, st.screen_height / 2 + 230)

    command_srf = pygame.Surface((st.screen_width, 30))
    command_srf.fill(st.MED_GRAY)
    command_srf.set_alpha(32)
    command_rect = command_srf.get_rect()


    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == QUIT:
                save_stats()
                quit_game()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    st.shoot_sfx.play()
                    if continue_rect.collidepoint(pygame.mouse.get_pos()):
                        paused = False
                    if replay_rect.collidepoint(pygame.mouse.get_pos()):
                        save_stats()
                        new_game(screen, clock)
                    if home_rect.collidepoint(pygame.mouse.get_pos()):
                        save_stats()
                        home()
                    if quit_rect.collidepoint(pygame.mouse.get_pos()):
                        save_stats()
                        quit_game()
                    if command_rect.collidepoint(pygame.mouse.get_pos()):
                        print("COMMAND")
                if event.button == 3:
                    st.full_reload_sfx.play()

        screen.fill(st.bg_color)
        screen.blit(command_srf, command_rect)

        screen.blit(text_srf, text_rect)
        screen.blit(continue_srf, continue_rect)
        screen.blit(replay_srf, replay_rect)
        screen.blit(home_srf, home_rect)
        screen.blit(quit_srf, quit_rect)

        pygame.display.update()


def game_over(screen, clock):
    save_stats()

    score_srf = st.font_bold120.render(f"{score}", True, st.MED_GRAY)
    score_rect = score_srf.get_rect()
    score_rect.bottomright = (st.screen_width * 3 / 4 + 120, st.screen_height / 2 - 130)

    highscore_srf = st.font_normal30.render(f"Highscore: {highscore}", True, st.MED_GRAY)
    highscore_rect = highscore_srf.get_rect()
    highscore_rect.midbottom = (st.screen_width * 3 / 4, st.screen_height / 2 + 110)

    accuracy_srf = st.font_normal30.render(f"Accuracy: {accuracy}%", True, st.MED_GRAY)
    accuracy_rect = accuracy_srf.get_rect()
    accuracy_rect.midbottom = (st.screen_width * 3 / 4, st.screen_height / 2 + 150)

    shoot_number_srf = st.font_normal30.render(f"Shoots: {shoot_number}", True, st.MED_GRAY)
    shoot_number_rect = shoot_number_srf.get_rect()
    shoot_number_rect.midbottom = (st.screen_width * 3 / 4, st.screen_height / 2 + 190)

    target_hit_srf = st.font_normal30.render(f"Target hit: {target_hit}", True, st.MED_GRAY)
    target_hit_rect = target_hit_srf.get_rect()
    target_hit_rect.midbottom = (st.screen_width * 3 / 4, st.screen_height / 2 + 230)

    text_srf = st.font_corbel_bold85.render("GAMEOVER", True, st.DARK_RED)
    text_rect = text_srf.get_rect()
    text_rect.bottomleft = (80, st.screen_height / 2 + 40)

    replay_srf = st.font_corbel_bold50.render("Replay", True, st.MED_GRAY)
    replay_rect = replay_srf.get_rect()
    replay_rect.bottomleft = (130, st.screen_height / 2 + 110)

    home_srf = st.font_corbel_bold50.render("Home", True, st.MED_GRAY)
    home_rect = home_srf.get_rect()
    home_rect.bottomleft = (130, st.screen_height / 2 + 170)

    quit_srf = st.font_corbel_bold50.render("Quit", True, st.MED_RED)
    quit_rect = quit_srf.get_rect()
    quit_rect.bottomleft = (130, st.screen_height / 2 + 230)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                save_stats()
                quit_game()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    st.shoot_sfx.play()
                    if replay_rect.collidepoint(pygame.mouse.get_pos()):
                        save_stats()
                        new_game(screen, clock)
                    if home_rect.collidepoint(pygame.mouse.get_pos()):
                        save_stats()
                        home()
                    if quit_rect.collidepoint(pygame.mouse.get_pos()):
                        save_stats()
                        quit_game()
                if event.button == 3:
                    st.full_reload_sfx.play()

        screen.fill(st.bg_color)

        screen.blit(text_srf, text_rect)
        screen.blit(replay_srf, replay_rect)
        screen.blit(home_srf, home_rect)
        screen.blit(quit_srf, quit_rect)

        screen.blit(score_srf, score_rect)
        screen.blit(highscore_srf, highscore_rect)
        screen.blit(accuracy_srf, accuracy_rect)
        screen.blit(shoot_number_srf, shoot_number_rect)
        screen.blit(target_hit_srf, target_hit_rect)

        pygame.display.update()


home()
