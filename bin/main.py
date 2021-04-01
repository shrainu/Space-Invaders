import os
import sys
import enum
import json
import random
import pygame
from levelgenerator import generate_level

pygame.init()
pygame.mixer.music.set_volume(0.5)

# Sprites
INVADER_BASIC = pygame.image.load(os.path.join('assets', 'space_invader_basic.png'))
INVADER_BASIC = pygame.transform.scale(INVADER_BASIC, (48, 48))
INVADER_BASIC_W = pygame.image.load(os.path.join('assets', 'space_invader_basic_w.png'))
INVADER_BASIC_W = pygame.transform.scale(INVADER_BASIC_W, (48, 48))
INVADER_RANGER = pygame.image.load(os.path.join('assets', 'space_invader_ranger.png'))
INVADER_RANGER = pygame.transform.scale(INVADER_RANGER, (48, 48))
INVADER_RANGER_W = pygame.image.load(os.path.join('assets', 'space_invader_ranger_w.png'))
INVADER_RANGER_W = pygame.transform.scale(INVADER_RANGER_W, (48, 48))
INVADER_RANGER_S = pygame.image.load(os.path.join('assets', 'space_invader_ranger.png'))
INVADER_TANK = pygame.image.load(os.path.join('assets', 'space_invader_tank.png'))
INVADER_TANK = pygame.transform.scale(INVADER_TANK, (48, 48))
INVADER_TANK_W = pygame.image.load(os.path.join('assets', 'space_invader_tank_w.png'))
INVADER_TANK_W = pygame.transform.scale(INVADER_TANK_W, (48, 48))
PLAYER_SPRITE = pygame.image.load(os.path.join('assets', 'player_sprite.png'))
PLAYER_SPRITE = pygame.transform.scale(PLAYER_SPRITE, (48, 48))
PLAYER_SPRITE_G = pygame.image.load(os.path.join('assets', 'player_sprite_g.png'))
PLAYER_SPRITE_G = pygame.transform.scale(PLAYER_SPRITE_G, (48, 48))
PLAYER_SPRITE_S = pygame.image.load(os.path.join('assets', 'player_sprite.png'))
PLAYER_SPRITE_SG = pygame.image.load(os.path.join('assets', 'player_sprite_g.png'))
DEATH_SPRITE = pygame.image.load(os.path.join('assets', 'blast.png'))
DEATH_SPRITE = pygame.transform.scale(DEATH_SPRITE, (48, 48))
DEATH_SPRITE_W = pygame.image.load(os.path.join('assets', 'blast_w.png'))
DEATH_SPRITE_W = pygame.transform.scale(DEATH_SPRITE_W, (48, 48))

# Sound effects
SPACESHIP_FIRE = pygame.mixer.Sound(os.path.join('sfx', 'spaceship_fire.mp3'))
SPACESHIP_FIRE.set_volume(0.25)
SPACESHIP_EXPLODE = pygame.mixer.Sound(os.path.join('sfx', 'spaceship_explode.mp3'))
SPACESHIP_EXPLODE.set_volume(0.25)
SPACESHIP_HIT = pygame.mixer.Sound(os.path.join('sfx', 'spaceship_hit.mp3'))
SPACESHIP_HIT.set_volume(0.5)
BUTTON_CLICK = pygame.mixer.Sound(os.path.join('sfx', 'button_click.mp3'))

# Screen variables
WIDTH, HEIGHT = 450, 450
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('SPACE INVADERS')
pygame.display.set_icon(INVADER_RANGER_S)
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Fonts
MAIN_FONT = pygame.font.Font(os.path.join('assets', 'font', 're-do', 're-do.ttf'), 10)
BIGGER_FONT = pygame.font.Font(os.path.join('assets', 'font', 're-do', 're-do.ttf'), 18)

# Map '#' = Common, '@' = Ranger, '$' = Tank
level0 = [[".", ".", ".", ".", ".", ".", ".", ".", ".", "0"],
          [".", ".", "@", "@", "@", "@", "@", ".", ".", "1"],
          [".", ".", "#", "#", "#", "#", "#", ".", ".", "2"],
          [".", ".", "#", "#", "#", "#", "#", ".", ".", "3"],
          [".", ".", "$", "$", "$", "$", "$", ".", ".", "4"],
          [".", ".", ".", ".", ".", ".", ".", ".", ".", "5"],
          [".", ".", ".", ".", ".", ".", ".", ".", ".", "6"],
          [".", ".", ".", ".", ".", ".", ".", ".", ".", "7"],
          [".", ".", ".", ".", ".", ".", ".", ".", ".", "8"]
          ]

# Player variables
VELOCITY = 5
PLAYER_SHOT = pygame.USEREVENT + 1
PLAYER_HIT = pygame.USEREVENT + 2
PLAYER_KILL = pygame.USEREVENT + 3


# Scenes
class Scenes(enum.Enum):
    main_scene = 0
    game_scene = 1
    high_score_scene = 2
    death_scene = 3


# Scene manager class ------------------------------------------------
class SceneManager:

    def __init__(self, main_scene):
        self.scene = main_scene

    def change_scene(self, scene):
        self.scene = scene

    def get_scene(self):
        return self.scene


# Enemies class to make spawning enemies here ------------------------
class Enemies:
    move_dir = -1
    all_enemies = []
    called = False

    def __init__(self, pos, size, sprite, sprite_c, can_shoot=False, health=1, score=50):
        self.rect = pygame.Rect(pos, size)
        self.sprite = sprite
        self.sprite_c = sprite_c
        self.health = health
        self.death = False
        self.score = score
        self._rdm = 0
        self.destroy_time = 0
        self.decent_timer = 0
        self.move_speed = 25
        self.next_move_time = pygame.time.get_ticks() + 1000
        self.can_shoot = can_shoot
        self.next_shoot_time = pygame.time.get_ticks() + 1000
        self.has_shoot = False
        Enemies.all_enemies.append(self)

    def draw(self):
        WIN.blit(self.sprite_c, self.rect)
        WIN.blit(self.sprite, (self.rect.x + 2, self.rect.y))

    def shoot(self, enemy_projectiles):
        if pygame.time.get_ticks() >= self.next_shoot_time:
            if not self.has_shoot:
                self._rdm = random.randint(1, 20)
                if self._rdm > 14:
                    projectile = pygame.Rect(self.rect.center, (5, 10))
                    enemy_projectiles.append(projectile)
                    SPACESHIP_FIRE.play()
                self.next_shoot_time = pygame.time.get_ticks() + 1000.

    def change_move_dir(self):
        if self.rect.x == 0:
            Enemies.move_dir = 1
        elif self.rect.x + 50 == WIDTH:
            Enemies.move_dir = -1

    def move(self):
        if pygame.time.get_ticks() >= self.next_move_time:
            self.rect.x += self.move_speed * Enemies.move_dir
            self.next_move_time = pygame.time.get_ticks() + 1000

    def decent(self):
        if pygame.time.get_ticks() >= self.decent_timer:
            self.decent_timer = 0
        if self.decent_timer == 0:
            self.rect.y += 25
            self.decent_timer = pygame.time.get_ticks() + 2500

    def take_damage(self):
        self.health -= 1
        SPACESHIP_HIT.play()
        if self.health <= 0:
            self.self_destruct()

    def self_destruct(self):
        self.sprite = DEATH_SPRITE
        self.sprite_c = DEATH_SPRITE_W
        self.death = True
        SPACESHIP_EXPLODE.play()

    def update(self, enemy_projectiles, enemies, enemies_killed_arr):
        self.change_move_dir()
        self.move()
        if self.can_shoot:
            self.shoot(enemy_projectiles)
        if self.death:
            if self.destroy_time == 0:
                self.destroy_time = pygame.time.get_ticks() + 600
            if pygame.time.get_ticks() >= self.destroy_time:
                enemies_killed_arr.append(1)
                enemies.remove(self)


# Button object class to make creating buttons easier ----------------
class ButtonObject:
    n = 5

    def __init__(self, pos, size, normal_color, focus_color=None, text=None, text_color=None, text_color_var=None):
        self.rect = pygame.Rect(pos, size)
        self.normal_color = normal_color
        self.focus_color = focus_color
        self.text = text
        self.text_color = text_color
        self.text_color_var = text_color_var
        if self.text is not None and self.text_color is not None:
            self.draw_text0 = MAIN_FONT.render(text, True, text_color)
        if self.text is not None and self.text_color_var is not None:
            self.draw_text1 = MAIN_FONT.render(text, True, text_color_var)
        self.b_event = pygame.USEREVENT + ButtonObject.n
        self.in_focus = False
        ButtonObject.n += 1

    def draw_button(self):
        pygame.draw.rect(WIN, BLACK, self.rect, 0)
        if self.text is not None:
            WIN.blit(self.draw_text0, ((self.rect.x + self.rect.x / 10), (self.rect.y + self.rect.y / 20)))
        if self.in_focus:
            pygame.draw.rect(WIN, WHITE, self.rect, 4)
            if self.text is not None:
                WIN.blit(self.draw_text1, ((self.rect.x + self.rect.x / 10 + 2), (self.rect.y + self.rect.y / 20)))

    def update(self, event_list, mouse_collider):
        if self.rect.colliderect(mouse_collider):
            self.in_focus = True
        else:
            self.in_focus = False
        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    pygame.event.post(pygame.event.Event(self.b_event))


# To make managing high scores easier --------------------------------
class HighScore:
    def __init__(self, high_score, pos, number, s_type):
        self.number = number
        self.pos = pos
        self.score = high_score
        self.s_type = s_type
        self.text = self.s_type + " " + str(self.number) + ": " + str(self.score)
        self.text_var = None
        self.text_var_w = None

    def draw(self):
        self.text_var = MAIN_FONT.render(self.text, True, GREEN)
        self.text_var_w = MAIN_FONT.render(self.text, True, WHITE)
        WIN.blit(self.text_var, (self.pos[0] - 1, self.pos[1]))
        WIN.blit(self.text_var_w, (self.pos[0] + 1, self.pos[1]))


# To handle the player input -----------------------------------------
def handle_player_input(keys_pressed, player, player_projectiles, next_shoot_time, player_health):
    if player_health > 0:
        if keys_pressed[pygame.K_a] and player.x - VELOCITY > 0:
            player.x -= VELOCITY
        elif keys_pressed[pygame.K_d] and player.x + VELOCITY + player.width < WIDTH:
            player.x += VELOCITY
        if keys_pressed[pygame.K_SPACE]:
            if pygame.time.get_ticks() >= next_shoot_time:
                temp = pygame.Rect(player.center, (5, 10))
                player_projectiles.append(temp)
                pygame.event.post(pygame.event.Event(PLAYER_SHOT))
                SPACESHIP_FIRE.play()


# To calculate the new score after each enemy killed -----------------
def update_score(scores_arr):
    n = 0
    for x in scores_arr:
        n += x
    return n


# To update the high scores screen -----------------------------------
def update_high_scores(high_scores):
    temp_arr = []
    temp_arr2 = []
    y = 100
    n = 1
    high_scores.clear()
    with open(os.path.join('high_scores.json')) as h_jsn:
        score_data = json.load(h_jsn)
    for score in score_data['endless_mode']:
        temp_arr.append(HighScore(score, (20, y), n, "ENDLESS"))
        y += 40
        n += 1
    high_scores["endless"] = temp_arr
    n = 1
    y += 40
    for score_2 in score_data['normal_mode']:
        temp_arr2.append(HighScore(score_2, (20, y), n, "NORMAL"))
        y += 40
        n += 1
    high_scores["normal"] = temp_arr2
    return high_scores


# To calculate how many enemies have killed --------------------------
def update_enemies_killed(enemies_killed_arr):
    n = 0
    for x in enemies_killed_arr:
        n += x
    return n


# To decent enemies when they reach the end of the screen ------------
def decent_enemies(enemies):
    for enemy in enemies:
        if enemy.rect.x < 25:
            for each in enemies:
                each.decent()
        elif enemy.rect.x + enemy.rect.width > 425:
            for each in enemies:
                each.decent()


# To see if player collided with any enemy
def handle_player_collision(player, player_health, enemies):
    for enemy in enemies:
        if player.colliderect(enemy) and player_health > 0:
            pygame.event.post(pygame.event.Event(PLAYER_KILL))


# To handle the collision and projectile movement --------------------
def handle_projectiles(player, enemies, player_projectiles, enemy_projectiles, scores_arr, player_health):
    for projectile in player_projectiles:
        projectile.y -= 8
        for enemy in enemies:
            if enemy.rect.colliderect(projectile) and not enemy.death:
                enemy.take_damage()
                if enemy.death:
                    if player_health > 0:
                        scores_arr.append(enemy.score * player_health)
                    else:
                        scores_arr.append(enemy.score)
                if player_projectiles.count(projectile) > 0:
                    player_projectiles.remove(projectile)
        if player_projectiles.count(projectile) > 0:
            if projectile.y + projectile.height < -50:
                player_projectiles.remove(projectile)
    for projectile in enemy_projectiles:
        projectile.y += 8
        if player_health > 0:
            if player.colliderect(projectile):
                enemy_projectiles.remove(projectile)
                if len(enemies) > 0:
                    pygame.event.post(pygame.event.Event(PLAYER_HIT))
        if projectile.y > HEIGHT:
            enemy_projectiles.remove(projectile)


# To save high scores to the high_scores.json ------------------------
def save_high_scores(high_score, endless_mode=False):
    with open(os.path.join('high_scores.json')) as h_jsn:
        score_data = json.load(h_jsn)
    if not endless_mode:
        with open(os.path.join('high_scores.json'), 'w') as h_jsn:
            score_data['normal_mode'].append(high_score)
            score_data['normal_mode'].sort(reverse=True)
            while len(score_data['normal_mode']) > 3:
                score_data['normal_mode'].remove(score_data['normal_mode'][-1])
            json.dump(score_data, h_jsn, indent=2)
    elif endless_mode:
        with open(os.path.join('high_scores.json'), 'w') as h_jsn:
            score_data['endless_mode'].append(high_score)
            score_data['endless_mode'].sort(reverse=True)
            while len(score_data['endless_mode']) > 3:
                score_data['endless_mode'].remove(score_data['endless_mode'][-1])
            json.dump(score_data, h_jsn, indent=2)


# Use this to load level from json file ------------------------------
def load_level(data, enemies, level_number):
    for line in data['levels'][level_number]:
        for i in range(len(line) - 1):
            if line[i] == "#":
                temp = Enemies((i * 50, data['levels'][level_number].index(line) * 50), (50, 50), INVADER_BASIC,
                               INVADER_BASIC_W)
                enemies.append(temp)
            elif line[i] == "@":
                temp = Enemies((i * 50, data['levels'][level_number].index(line) * 50), (50, 50), INVADER_RANGER,
                               INVADER_RANGER_W, True, score=80)
                enemies.append(temp)
            elif line[i] == "$":
                temp = Enemies((i * 50, data['levels'][level_number].index(line) * 50), (50, 50), INVADER_TANK,
                               INVADER_TANK_W, False, 2, 80)
                enemies.append(temp)


# Use this to load level from json file ------------------------------
def load_endless_level(data, enemies):
    for line in data:
        for i in range(len(line) - 1):
            if line[i] == "#":
                temp = Enemies((i * 50, data.index(line) * 50), (50, 50), INVADER_BASIC,
                               INVADER_BASIC_W)
                enemies.append(temp)
            elif line[i] == "@":
                temp = Enemies((i * 50, data.index(line) * 50), (50, 50), INVADER_RANGER,
                               INVADER_RANGER_W, True, score=80)
                enemies.append(temp)
            elif line[i] == "$":
                temp = Enemies((i * 50, data.index(line) * 50), (50, 50), INVADER_TANK,
                               INVADER_TANK_W, False, 2, 80)
                enemies.append(temp)


# Update the main menu display ---------------------------------------
def update_display_0(buttons, mouse_collider):
    # Always at the top
    WIN.fill(BLACK)

    # Buttons
    for button in buttons:
        button.draw_button()

    # Game title
    title_text1_w = BIGGER_FONT.render("SPACE", True, WHITE)
    title_text1_g = BIGGER_FONT.render("SPACE", True, GREEN)
    title_text2_w = BIGGER_FONT.render("INVADERS", True, WHITE)
    title_text2_r = BIGGER_FONT.render("INVADERS", True, RED)
    WIN.blit(title_text1_w, (139, 30))
    WIN.blit(title_text1_g, (141, 30))
    WIN.blit(title_text2_w, (94, 60))
    WIN.blit(title_text2_r, (96, 60))

    # Mute text
    press_mute_text_r = MAIN_FONT.render("M TO MUTE", True, RED)
    WIN.blit(press_mute_text_r, (125, 370))

    # Shrain text
    shrain_text = MAIN_FONT.render("A GAME BY SHRAIN", True, WHITE)
    WIN.blit(shrain_text, (72, 400))

    # Debugging purposes
    # pygame.draw.rect(WIN, (0, 0, 0, 255), mouse_collider, 0)

    # Always at the bottom
    pygame.display.update()


# Update the game display --------------------------------------------
def update_display_1(player, enemies, player_projectiles, enemy_projectiles, score, player_health, countdown_time):
    # Always at the top
    WIN.fill(BLACK)

    # Display enemy related stuff
    for enemy in enemies:
        enemy.draw()
    for projectile in enemy_projectiles:
        pygame.draw.rect(WIN, WHITE, projectile)
        pygame.draw.rect(WIN, RED, pygame.Rect((projectile.x + 2, projectile.y), (projectile.width, projectile.height)))

    # Display player related stuff
    if player_health > 0:
        WIN.blit(PLAYER_SPRITE, player)
        WIN.blit(PLAYER_SPRITE_G, (player.x + 2, player.y))
    for projectile in player_projectiles:
        pygame.draw.rect(WIN, WHITE, projectile)
        pygame.draw.rect(WIN, GREEN,
                         pygame.Rect((projectile.x + 2, projectile.y), (projectile.width, projectile.height)))
    # Player score UI
    score_text = MAIN_FONT.render("SCORE:" + str(score), True, WHITE)
    score_text_g = MAIN_FONT.render("SCORE:" + str(score), True, GREEN)
    WIN.blit(score_text, (3, 0))
    WIN.blit(score_text_g, (5, 0))
    # Player health UI
    player_health_text = MAIN_FONT.render("X" + str(player_health), True, WHITE)
    player_health_text_g = MAIN_FONT.render("X" + str(player_health), True, GREEN)
    WIN.blit(player_health_text, (413, 0))
    WIN.blit(player_health_text_g, (415, 0))
    WIN.blit(PLAYER_SPRITE_S, (387, 2))
    WIN.blit(PLAYER_SPRITE_SG, (388, 2))

    if pygame.time.get_ticks() < countdown_time and len(enemies) == 0:
        won_text = BIGGER_FONT.render("LEVEL WON!", True, GREEN)
        won_text_w = BIGGER_FONT.render("LEVEL WON!", True, WHITE)
        WIN.blit(won_text_w, (63, 210))
        WIN.blit(won_text, (65, 210))
    elif pygame.time.get_ticks() < countdown_time and player_health <= 0:
        death_text = BIGGER_FONT.render("GAME OVER", True, GREEN)
        death_text_w = BIGGER_FONT.render("GAME OVER", True, WHITE)
        WIN.blit(death_text_w, (63, 210))
        WIN.blit(death_text, (65, 210))

    # Always at the bottom
    pygame.display.update()


# Update the death display -------------------------------------------
def update_display_2(final_scene_buttons, current_level, player_score, enemies_killed):
    # Always at the top
    WIN.fill(BLACK)

    # Buttons
    for button in final_scene_buttons:
        button.draw_button()

    # UI related stuff
    game_over_text = BIGGER_FONT.render("GAME OVER", True, RED)
    game_over_text_w = BIGGER_FONT.render("GAME OVER", True, WHITE)
    WIN.blit(game_over_text_w, (59, 100))
    WIN.blit(game_over_text, (61, 100))
    high_score_text = MAIN_FONT.render("SCORE: " + str(player_score), True, GREEN)
    high_score_text_w = MAIN_FONT.render("SCORE: " + str(player_score), True, WHITE)
    WIN.blit(high_score_text_w, (59, 160))
    WIN.blit(high_score_text, (61, 160))
    level_text = MAIN_FONT.render("LEVEL: " + str(current_level), True, GREEN)
    level_text_w = MAIN_FONT.render("LEVEL: " + str(current_level), True, WHITE)
    WIN.blit(level_text_w, (59, 200))
    WIN.blit(level_text, (61, 200))
    enemies_k_text = MAIN_FONT.render("KILLED: " + str(enemies_killed), True, GREEN)
    enemies_k_text_w = MAIN_FONT.render("KILLED: " + str(enemies_killed), True, WHITE)
    WIN.blit(enemies_k_text_w, (59, 240))
    WIN.blit(enemies_k_text, (61, 240))

    # Always at the bottom
    pygame.display.update()


# Update the death display -------------------------------------------
def update_display_3(return_menu_button2, high_scores):
    # Always at the top
    WIN.fill(BLACK)

    # High Scores
    for score in high_scores['endless']:
        score.draw()
    for score in high_scores['normal']:
        score.draw()

    # Buttons
    return_menu_button2.draw_button()

    # UI related stuff
    game_over_text = BIGGER_FONT.render("HIGH SCORES", True, GREEN)
    game_over_text_w = BIGGER_FONT.render("HIGH SCORES", True, WHITE)
    WIN.blit(game_over_text_w, (29.5, 40))
    WIN.blit(game_over_text, (31, 40))

    # Always at the bottom
    pygame.display.update()


# Main game loop -----------------------------------------------------
def main(is_mute=False):
    clock = pygame.time.Clock()

    # Music variables
    pygame.mixer.music.load('music/soundtrack.wav')
    pygame.mixer.music.play(-1)
    mute = is_mute

    # Player Variables
    player = pygame.Rect((225, 400), (50, 50))
    player_max_health = 3
    player_health = player_max_health
    scores_arr = []
    next_shoot_time = 0
    player_projectiles = []

    # Mouse
    mouse_collider = pygame.Rect((0, 0), (1, 1))

    # Scene Management
    scene_manager = SceneManager(Scenes.main_scene)
    current_scene = None

    # Buttons
    play_button = ButtonObject((25, 150), (400, 34), BLACK, BLACK, "CLICK TO START GAME", WHITE, GREEN)
    endless_mode_button = ButtonObject((95, 200), (255, 34), BLACK, BLACK, "ENDLESS MODE", WHITE, GREEN)
    high_scores_button = ButtonObject((105, 250), (240, 34), BLACK, BLACK, "HIGH SCORES", WHITE, GREEN)
    exit_button = ButtonObject((175, 300), (100, 40), BLACK, BLACK, "EXIT", WHITE, RED)
    buttons = [play_button, endless_mode_button, high_scores_button, exit_button]
    # Final Scene Buttons
    return_menu_button = ButtonObject((70, 350), (300, 40), BLACK, BLACK, "RETURN TO MENU", WHITE, GREEN)
    high_scores_button2 = ButtonObject((105, 300), (240, 40), BLACK, BLACK, "HIGH SCORES", WHITE, GREEN)
    final_scene_buttons = [return_menu_button, high_scores_button2]
    # High Score Scene Buttons
    return_menu_button2 = ButtonObject((70, 370), (300, 40), BLACK, BLACK, "RETURN TO MENU", WHITE, BLUE)

    # Enemies
    enemies = []
    enemies_killed_arr = []
    enemies_killed = 0
    enemy_projectiles = []

    # Level variables
    countdown_timer = 0
    current_level = 0
    endless_mode = False
    high_scores = {}

    # Open levels.json
    with open(os.path.join('levels.json')) as jsn:
        data = json.load(jsn)

    run = True

    while run:

        clock.tick(FPS)

        mouse_collider.center = pygame.mouse.get_pos()

        event_list = pygame.event.get()
        # Manage the events here ------------------------------
        for event in event_list:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    mute = not mute
            if event.type == play_button.b_event:
                BUTTON_CLICK.play()
                scene_manager.change_scene(Scenes.game_scene)
            elif event.type == exit_button.b_event:
                BUTTON_CLICK.play()
                run = False
                pygame.quit()
                sys.exit()
            elif event.type == high_scores_button.b_event:
                BUTTON_CLICK.play()
                high_scores = update_high_scores(high_scores)
                scene_manager.change_scene(Scenes.high_score_scene)
            elif event.type == endless_mode_button.b_event:
                BUTTON_CLICK.play()
                scene_manager.change_scene(Scenes.game_scene)
                endless_mode = True
            if event.type == return_menu_button2.b_event:
                BUTTON_CLICK.play()
                main(mute)
                run = False
                return
            if event.type == return_menu_button.b_event:
                BUTTON_CLICK.play()
                main(mute)
                run = False
                return
            elif event.type == high_scores_button2.b_event:
                BUTTON_CLICK.play()
                high_scores = update_high_scores(high_scores)
                scene_manager.change_scene(Scenes.high_score_scene)
            if event.type == PLAYER_SHOT:
                next_shoot_time = pygame.time.get_ticks() + 1000
            if event.type == PLAYER_HIT:
                player_health -= 1
                SPACESHIP_HIT.play()
            if event.type == PLAYER_KILL:
                player_health -= 100
                if player_health < 0:
                    player_health = 0
                SPACESHIP_HIT.play()
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

        # To store key input from player
        keys_pressed = pygame.key.get_pressed()

        if mute:
            pygame.mixer.music.set_volume(0)
        elif not mute:
            pygame.mixer.music.set_volume(0.75)

        # Arrange and sets the scenes here --------------------
        current_scene = scene_manager.get_scene()
        if current_scene == Scenes.main_scene:

            # Buttons Update
            for button in buttons:
                button.update(event_list, mouse_collider)

            # Always at the bottom
            update_display_0(buttons, mouse_collider)
        elif current_scene == Scenes.game_scene:

            if current_level == 0 and not endless_mode:
                level_string = 'level' + str(current_level)
                load_level(data, enemies, level_string)
                current_level += 1
            elif current_level == 0 and endless_mode:
                load_endless_level(generate_level(), enemies)
                current_level += 1

            # Handle Player Input
            handle_player_input(keys_pressed, player, player_projectiles, next_shoot_time, player_health)
            # Player Update
            handle_projectiles(player, enemies, player_projectiles, enemy_projectiles, scores_arr, player_health)
            handle_player_collision(player, player_health, enemies)
            player_score = update_score(scores_arr)

            # print(endless_mode) - for debugging purposes

            if endless_mode:
                if len(enemies) == 0 and player_health > 0:
                    if countdown_timer == 0:
                        countdown_timer = pygame.time.get_ticks() + 2500
                    if pygame.time.get_ticks() >= countdown_timer:
                        countdown_timer = 0
                        current_level += 1
                        load_endless_level(generate_level(), enemies)
            else:
                if len(enemies) == 0 and player_health > 0:
                    if countdown_timer == 0:
                        countdown_timer = pygame.time.get_ticks() + 2500
                    if pygame.time.get_ticks() >= countdown_timer:
                        if current_level == 9:
                            scene_manager.change_scene(Scenes.main_scene)
                        countdown_timer = 0
                        level_string = 'level' + str(current_level)
                        load_level(data, enemies, level_string)
                        current_level += 1
            if player_health <= 0:
                if countdown_timer == 0:
                    countdown_timer = pygame.time.get_ticks() + 2500
                if pygame.time.get_ticks() >= countdown_timer:
                    countdown_timer = 0
                    if player_health <= 0:
                        enemies_killed = update_enemies_killed(enemies_killed_arr)
                        scene_manager.change_scene(Scenes.death_scene)
                        if not endless_mode:
                            save_high_scores(player_score)
                        else:
                            save_high_scores(player_score, True)

            # Enemies Update
            decent_enemies(enemies)
            for enemy in enemies:
                enemy.update(enemy_projectiles, enemies, enemies_killed_arr)

            # Always at the bottom
            update_display_1(player, enemies, player_projectiles, enemy_projectiles, player_score, player_health,
                             countdown_timer)
        elif current_scene == Scenes.high_score_scene:

            # Buttons Update
            return_menu_button2.update(event_list, mouse_collider)

            # Always at the bottom
            update_display_3(return_menu_button2, high_scores)
        elif current_scene == Scenes.death_scene:

            # Buttons Update
            for button in final_scene_buttons:
                button.update(event_list, mouse_collider)

            # Always at the bottom
            update_display_2(final_scene_buttons, current_level, player_score, enemies_killed)


if __name__ == '__main__':
    main()
