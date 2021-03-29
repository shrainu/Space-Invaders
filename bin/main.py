import os
import sys
import enum
import random
import pygame
pygame.init()

# Sprites
INVADER_BASIC = pygame.image.load(os.path.join('bin', 'assets', 'space_invader_basic.png'))
INVADER_BASIC = pygame.transform.scale(INVADER_BASIC, (48, 48))
INVADER_RANGER = pygame.image.load(os.path.join('bin', 'assets', 'space_invader_ranger.png'))
INVADER_RANGER = pygame.transform.scale(INVADER_RANGER, (48, 48))
PLAYER_SPRITE = pygame.image.load(os.path.join('bin', 'assets', 'player_sprite.png'))
PLAYER_SPRITE = pygame.transform.scale(PLAYER_SPRITE, (48, 48))


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

# Map
level0 = [[".", ".", ".", ".", ".", ".", ".", ".", ".", "0"],
          [".", ".", "@", "@", "@", "@", "@", ".", ".", "1"],
          [".", ".", "#", "#", "#", "#", "#", ".", ".", "2"],
          [".", ".", "#", "#", "#", "#", "#", ".", ".", "3"],
          [".", ".", "#", "#", "#", "#", "#", ".", ".", "4"],
          [".", ".", ".", ".", ".", ".", ".", ".", ".", "5"],
          [".", ".", ".", ".", ".", ".", ".", ".", ".", "6"],
          [".", ".", ".", ".", ".", ".", ".", ".", ".", "7"],
          [".", ".", ".", ".", ".", ".", ".", ".", ".", "8"]
         ]

# Player variables
VELOCITY = 5
PLAYER_SHOT = pygame.USEREVENT + 1


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

    def __init__(self, pos, size, sprite, can_shoot=False):
        self.rect = pygame.Rect(pos, size)
        self.sprite = sprite
        self.move_speed = 25
        self.next_move_time = 0
        self.rand = 0
        self.can_shoot = can_shoot
        self.next_shoot_time = 0
        self.has_shoot = False

    def draw(self):
        WIN.blit(self.sprite, self.rect)

    def shoot(self, enemy_projectiles):
        if pygame.time.get_ticks() >= self.next_shoot_time:
            if not self.has_shoot:
                self.rand = random.randint(1, 20)
                if self.rand > 15:
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

    def update(self, enemy_projectiles):
        self.change_move_dir()
        self.move()
        if self.can_shoot:
            self.shoot(enemy_projectiles)


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
def handle_player_input(keys_pressed, player, player_projectiles, next_shoot_time):
    if keys_pressed[pygame.K_a] and player.x - VELOCITY > 0:
        player.x -= VELOCITY
    elif keys_pressed[pygame.K_d] and player.x + VELOCITY + player.width < WIDTH:
        player.x += VELOCITY
    if keys_pressed[pygame.K_SPACE]:
        if pygame.time.get_ticks() >= next_shoot_time:
            temp = pygame.Rect(player.center, (5, 10))
            player_projectiles.append(temp)
            pygame.event.post(pygame.event.Event(PLAYER_SHOT))


# To handle the collision and projectile movement --------------------
def handle_projectiles(player, enemies, player_projectiles, enemy_projectiles):
    for projectile in player_projectiles:
        projectile.y -= 8
        for enemy in enemies:
            if enemy.rect.colliderect(projectile):
                enemies.remove(enemy)
                player_projectiles.remove(projectile)
        if projectile.y + projectile.height < 0:
            player_projectiles.remove(projectile)
    for projectile in enemy_projectiles:
        projectile.y += 8
        if player.colliderect(projectile):
            enemy_projectiles.remove(projectile)
            print("PLAYER HIT!")
        if projectile.y > HEIGHT:
            enemy_projectiles.remove(projectile)


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
def update_display_1(player, enemies, player_projectiles, enemy_projectiles):
    # Always at the top
    WIN.fill(BLACK)

    # Display enemy related stuff
    for enemy in enemies:
        enemy.draw()
    for projectile in enemy_projectiles:
        pygame.draw.rect(WIN, RED, projectile)

    # Display player related stuff
    WIN.blit(PLAYER_SPRITE, player)
    for projectile in player_projectiles:
        pygame.draw.rect(WIN, WHITE, projectile)

    # Always at the bottom
    pygame.display.update()


# Main game loop -----------------------------------------------------
def main():

    clock = pygame.time.Clock()

    # Player Variables
    player = pygame.Rect((225, 400), (50, 50))
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

    # To add all the enemies to the game from list
    for line in level0:
        for i in range(len(line)-1):
            if line[i] == "#":
                temp = Enemies((i*50, level0.index(line)*50), (50, 50), INVADER_BASIC)
                enemies.append(temp)
            elif line[i] == "@":
                temp = Enemies((i * 50, level0.index(line) * 50), (50, 50), INVADER_RANGER, True)
                enemies.append(temp)

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
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

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
            handle_player_input(keys_pressed, player, player_projectiles, next_shoot_time)
            # Player Update
            handle_projectiles(player, enemies, player_projectiles, enemy_projectiles)

            # Enemies Update
            for enemy in enemies:
                enemy.update(enemy_projectiles)

            # Always at the bottom
            update_display_1(player, enemies, player_projectiles, enemy_projectiles)


if __name__ == '__main__':
    main()