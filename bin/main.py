import os
import sys
import enum
import json
import random
import pygame
pygame.init()

# Sprites
INVADER_BASIC = pygame.image.load(os.path.join('bin', 'assets', 'space_invader_basic.png'))
INVADER_BASIC = pygame.transform.scale(INVADER_BASIC, (48, 48))
INVADER_BASIC_W = pygame.image.load(os.path.join('bin', 'assets', 'space_invader_basic_w.png'))
INVADER_BASIC_W = pygame.transform.scale(INVADER_BASIC_W, (48, 48))
INVADER_RANGER = pygame.image.load(os.path.join('bin', 'assets', 'space_invader_ranger.png'))
INVADER_RANGER = pygame.transform.scale(INVADER_RANGER, (48, 48))
INVADER_RANGER_W = pygame.image.load(os.path.join('bin', 'assets', 'space_invader_ranger_w.png'))
INVADER_RANGER_W = pygame.transform.scale(INVADER_RANGER_W, (48, 48))
INVADER_TANK = pygame.image.load(os.path.join('bin', 'assets', 'space_invader_tank.png'))
INVADER_TANK = pygame.transform.scale(INVADER_TANK, (48, 48))
INVADER_TANK_W = pygame.image.load(os.path.join('bin', 'assets', 'space_invader_tank_w.png'))
INVADER_TANK_W = pygame.transform.scale(INVADER_TANK_W, (48, 48))
PLAYER_SPRITE = pygame.image.load(os.path.join('bin', 'assets', 'player_sprite.png'))
PLAYER_SPRITE = pygame.transform.scale(PLAYER_SPRITE, (48, 48))
PLAYER_SPRITE_G = pygame.image.load(os.path.join('bin', 'assets', 'player_sprite_g.png'))
PLAYER_SPRITE_G = pygame.transform.scale(PLAYER_SPRITE_G, (48, 48))
PLAYER_SPRITE_S = pygame.image.load(os.path.join('bin', 'assets', 'player_sprite.png'))
PLAYER_SPRITE_SG = pygame.image.load(os.path.join('bin', 'assets', 'player_sprite_g.png'))
DEATH_SPRITE = pygame.image.load(os.path.join('bin', 'assets', 'blast.png'))
DEATH_SPRITE = pygame.transform.scale(DEATH_SPRITE, (48, 48))
DEATH_SPRITE_W = pygame.image.load(os.path.join('bin', 'assets', 'blast_w.png'))
DEATH_SPRITE_W = pygame.transform.scale(DEATH_SPRITE_W, (48, 48))

# Screen variables
WIDTH, HEIGHT = 450, 450
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Fonts
MAIN_FONT = pygame.font.Font(os.path.join('bin', 'assets', 'font', 're-do', 're-do.ttf'), 10)
BIGGER_FONT = pygame.font.Font(os.path.join('bin', 'assets', 'font', 're-do', 're-do.ttf'), 18)

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
SPRITE_CORRUPT = pygame.USEREVENT + 3


# Scenes
class Scenes(enum.Enum):
    main_scene = 0
    game_scene = 1


# Scene manager class
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

    def __init__(self, pos, size, sprite, sprite_c, can_shoot=False, health=1, score=50):
        self.rect = pygame.Rect(pos, size)
        self.sprite = sprite
        self.sprite_c = sprite_c
        self.health = health
        self.death = False
        self.score = score
        self._rdm = 0
        self.destroy_time = 0
        self.move_speed = 25
        self.next_move_time = 0
        self.can_shoot = can_shoot
        self.next_shoot_time = 1500
        self.has_shoot = False

    def draw(self):
        WIN.blit(self.sprite_c, self.rect)
        WIN.blit(self.sprite, (self.rect.x + 2, self.rect.y))

    def shoot(self, enemy_projectiles):
        if pygame.time.get_ticks() >= self.next_shoot_time:
            if not self.has_shoot:
                self._rdm = random.randint(1, 20)
                if self._rdm > 15:
                    projectile = pygame.Rect(self.rect.center, (5, 10))
                    enemy_projectiles.append(projectile)
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

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            self.self_destruct()

    def self_destruct(self):
        self.sprite = DEATH_SPRITE
        self.sprite_c = DEATH_SPRITE_W
        self.death = True

    def update(self, enemy_projectiles, enemies):
        self.change_move_dir()
        self.move()
        if self.can_shoot:
            self.shoot(enemy_projectiles)
        if self.death:
            if self.destroy_time == 0:
                self.destroy_time = pygame.time.get_ticks() + 600
            if pygame.time.get_ticks() >= self.destroy_time:
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
            WIN.blit(self.draw_text0, ((self.rect.x + self.rect.x/10), (self.rect.y + self.rect.y/20)))
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


# To calculate the new score after each enemy killed
def update_score(scores_arr):
    n = 0
    for x in scores_arr:
        n += x
    return n


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
                player_projectiles.remove(projectile)
        if projectile.y + projectile.height < 0:
            player_projectiles.remove(projectile)
    for projectile in enemy_projectiles:
        projectile.y += 8
        if player.colliderect(projectile):
            enemy_projectiles.remove(projectile)
            pygame.event.post(pygame.event.Event(PLAYER_HIT))
        if projectile.y > HEIGHT:
            enemy_projectiles.remove(projectile)


# Use this to load level from json file
def load_level(data, enemies, level_number):
    for line in data['levels'][level_number]:
        for i in range(len(line)-1):
            if line[i] == "#":
                temp = Enemies((i*50, data['levels'][level_number].index(line)*50), (50, 50), INVADER_BASIC, INVADER_BASIC_W)
                enemies.append(temp)
            elif line[i] == "@":
                temp = Enemies((i * 50, data['levels'][level_number].index(line) * 50), (50, 50), INVADER_RANGER, INVADER_RANGER_W, True, score=80)
                enemies.append(temp)
            elif line[i] == "$":
                temp = Enemies((i * 50, data['levels'][level_number].index(line) * 50), (50, 50), INVADER_TANK, INVADER_TANK_W, True, 2, 80)
                enemies.append(temp)


# Update the main menu display ---------------------------------------
def update_display_0(buttons, mouse_collider):
    # Always at the top
    WIN.fill(BLACK)

    for button in buttons:
        button.draw_button()

    pygame.draw.rect(WIN, (0, 0, 0, 255), mouse_collider, 0)

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
        pygame.draw.rect(WIN, GREEN, pygame.Rect((projectile.x+2, projectile.y), (projectile.width, projectile.height)))
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

    if pygame.time.get_ticks() < countdown_time:
        won_text = BIGGER_FONT.render("LEVEL WON!", True, GREEN)
        won_text_w = BIGGER_FONT.render("LEVEL WON!", True, WHITE)
        WIN.blit(won_text_w, (63, 210))
        WIN.blit(won_text, (65, 210))

    # Always at the bottom
    pygame.display.update()


# Main game loop -----------------------------------------------------
def main():

    clock = pygame.time.Clock()

    # Player Variables
    player = pygame.Rect((225, 400), (50, 50))
    player_max_health = 3
    player_health = player_max_health
    player_score = 0
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
    exit_button = ButtonObject((175, 200), (100, 40), BLACK, BLACK, "EXIT", WHITE, RED)
    buttons = [play_button, exit_button]

    # Enemies
    enemies = []
    enemy_projectiles = []

    # Level variables
    countdown_timer = 0
    current_level = 0

    # Open levels.json
    with open(os.path.join('bin', 'levels.json')) as jsn:
        data = json.load(jsn)

    # To load level 0 from json file
    load_level(data, enemies, 'level0')

    run = True

    while run:

        clock.tick(FPS)

        mouse_collider.center = pygame.mouse.get_pos()

        event_list = pygame.event.get()
        # Manage the events here ------------------------------
        for event in event_list:
            if event.type == play_button.b_event:
                scene_manager.change_scene(Scenes.game_scene)
            elif event.type == exit_button.b_event:
                run = False
                pygame.quit()
                sys.exit()
            if event.type == PLAYER_SHOT:
                next_shoot_time = pygame.time.get_ticks() + 1000
            if event.type == PLAYER_HIT:
                player_health -= 1
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

        # To store key input from player
        keys_pressed = pygame.key.get_pressed()

        # Arrange and sets the scenes here --------------------
        current_scene = scene_manager.get_scene()
        if current_scene == Scenes.main_scene:

            # Buttons Update
            for button in buttons:
                button.update(event_list, mouse_collider)

            # Always at the bottom
            update_display_0(buttons, mouse_collider)
        elif current_scene == Scenes.game_scene:

            # Handle Player Input
            handle_player_input(keys_pressed, player, player_projectiles, next_shoot_time, player_health)
            # Player Update
            handle_projectiles(player, enemies, player_projectiles, enemy_projectiles, scores_arr, player_health)
            player_score = update_score(scores_arr)

            if len(enemies) == 0:
                if countdown_timer == 0:
                    countdown_timer = pygame.time.get_ticks() + 3000
                if pygame.time.get_ticks() >= countdown_timer:
                    countdown_timer = 0
                    current_level += 1
                    level_string = 'level' + str(current_level)
                    load_level(data, enemies, level_string)

            # Enemies Update
            for enemy in enemies:
                enemy.update(enemy_projectiles, enemies)

            # Always at the bottom
            update_display_1(player, enemies, player_projectiles, enemy_projectiles, player_score, player_health, countdown_timer)


if __name__ == '__main__':
    main()