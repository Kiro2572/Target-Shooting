import pygame
from pygame.locals import *

crosshair_string = (
    "       XX       ",
    "       XX       ",
    "       XX       ",
    "     XXXXXX     ",
    "    X  XX  X    ",
    "   X   XX   X   ",
    "   X   XX   X   ",
    "XXXXXXXXXXXXXXXX",
    "XXXXXXXXXXXXXXXX",
    "   X   XX   X   ",
    "   X   XX   X   ",
    "    X  XX  X    ",
    "     XXXXXX     ",
    "       XX       ",
    "       XX       ",
    "       XX       ")
crosshair = pygame.cursors.compile(crosshair_string)


# === SCREEN =====================
screen_width = 1000
screen_height = 600
bg_color = (230, 230, 230)
# ================================

# === COLORS =====================
BLACK = pygame.Color(0, 25, 25)
GRAY = pygame.Color(200, 200, 200)
MED_GRAY = pygame.Color(164, 164, 164)
DARK_GRAY = pygame.Color(128, 128, 128)
MED_RED = pygame.Color(200, 50, 50)
DARK_RED = pygame.Color(150, 0, 0)
# ================================

# === FONTS ======================
pygame.font.init()
font_corbel_bold85 = pygame.font.SysFont("corbel", 85, True)
font_corbel_bold60 = pygame.font.SysFont("corbel", 60, True)
font_corbel_bold50 = pygame.font.SysFont("corbel", 50, True)

font_consolas_normal18 = pygame.font.SysFont("consolas", 18)

font_bold120 = pygame.font.SysFont(None, 120, True)
font_bold40 = pygame.font.SysFont(None, 40, True)

font_normal30 = pygame.font.SysFont(None, 30)
font_normal25 = pygame.font.SysFont(None, 25)
# ================================

# === SPRITES ====================
icon = pygame.image.load("assets/target.ico")
logo = pygame.image.load("assets/logo.png")

bullet1_srf = pygame.image.load("assets/sprites/bullet1.png")
bullet2_srf = pygame.image.load("assets/sprites/bullet2.png")
bullet3_srf = pygame.image.load("assets/sprites/bullet3.png")
bullet4_srf = pygame.image.load("assets/sprites/bullet4.png")

target1_srf = pygame.image.load("assets/sprites/target1.png")
target2_srf = pygame.image.load("assets/sprites/target2.png")
target3_srf = pygame.image.load("assets/sprites/target3.png")
# ================================

# === SFX ========================
pygame.mixer.init()
shoot_sfx = pygame.mixer.Sound("assets/sfx/shoot.wav")
noammo_sfx = pygame.mixer.Sound("assets/sfx/noammo.wav")
reload_sfx = pygame.mixer.Sound("assets/sfx/reload.wav")
reload_end_sfx = pygame.mixer.Sound("assets/sfx/reload_end.wav")
full_reload_sfx = pygame.mixer.Sound("assets/sfx/full_reload.wav")
change_weapon_sfx = pygame.mixer.Sound("assets/sfx/change_weapon.wav")
target_lost_sfx = pygame.mixer.Sound("assets/sfx/target_lost.wav")
# ================================

# === MISC =======================
target_weights = [88, 9, 3]
weapon_weights = [47, 36, 12, 5, 0]

level_mult = 1000
target_spawn_mult = 0.9

target_lost_penalty = 50
# ================================

# === WEAPONS ====================
weapons = []
# (name, bullets, side_bullets, max_bullets_per_shoot, delay_between_bullets, reload_time, (bullet_srf, mag_col))
god_killer_bullet = pygame.Surface((12, 5))
god_killer_bullet.fill(DARK_RED)
revolver = ("Revolver", 6, 18, 1, -1, 1000, (bullet1_srf, 1), False)
handgun = ("Handgun", 8, 16, 1, -1, 750, (bullet2_srf, 1), False)
rifle = ("Rifle", 16, 32, 8, 200, 2000, (bullet3_srf, 1), False)
machine_gun = ("Machine Gun", 50, 50, 50, 100, 5000, (bullet4_srf, 2), False)
god_killer = ("GOD KILLER", 200, 1000, 200, 50, 1000, (god_killer_bullet, 4), True)

weapons.append(revolver)
weapons.append(handgun)
weapons.append(rifle)
weapons.append(machine_gun)
weapons.append(god_killer)
# ================================
