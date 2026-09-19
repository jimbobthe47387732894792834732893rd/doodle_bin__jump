# Example file showing a basic pygame "game loop"
import pygame
import random
import math
pygame.init()

# configuration
SCREEN_WIDTH = 470
SCREEN_HEIGHT = 720
BG_COLOR = "#fdf1e7"

RESTART_FONT = pygame.font.SysFont("Lobster", 25)
SCORE_FONT = pygame.font.SysFont("Arial", 30)

LEFT_BIN_IMAGE = pygame.image.load("images/bin_1.png")
RIGHT_BIN_IMAGE = pygame.image.load("images/bin_2.png")
SHOOTING_LEFT_BIN_IMAGE = pygame.image.load("images/shooting_left_bin.png")
SHOOTING_RIGHT_BIN_IMAGE = pygame.image.load("images/shooting_right_bin.png")
SHOOTING_BIN_IMAGE = pygame.image.load("images/shooting_bin.png")
LEFT_BIN_BALLIN_IMAGE = pygame.image.load("images/BIN_BALLIN!.png")
RIGHT_BIN_BALLIN_IMAGE = pygame.image.load("images/BIN_BALLIN 2!.png")
BOUNCY_PLATFORM_IMAGE = pygame.image.load("images/bouncy_platform.png")
BREAKABLE_PLATFORM_IMAGE = pygame.image.load("images/breakable_platform.png")
KITCAT_IMAGE = pygame.image.load("images/kitcat.png")
MAIN_MENU_IMAGE = pygame.image.load("images/main_menu.png")
TRY_AGAIN_IMAGE = pygame.image.load("images/try_again.png")
SUPER_BIN_IMAGE = pygame.image.load("images/super_bin!!!!!.png")
PARROT_IMAGE = pygame.image.load("images/5k parrot.png")
LOGO_IMAGE = pygame.image.load("images/logo.png")

CURRENT_BIN_IMAGE = LEFT_BIN_IMAGE

BIN_WIDTH = 50
BIN_HEIGHT = 64
PLATFORM_WIDTH = 60
PLATFORM_THICKNESS = 10

# pygame setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True

bin_x = SCREEN_WIDTH/2
bin_y = SCREEN_HEIGHT * .3
bin_shooting = 0
bin_moving_right = False
starting_bin_y = bin_y
highest_bin_y = bin_y
camera_y = 0
flying_by_rocket = False

platforms_to_hide = 0
hidden_platforms = 0

game_still_going = False

alive = True

# platform_x = 75
# platform_y = bin_y + BIN_HEIGHT
bin_y_speed = 0

# helper functions
def game_x_to_screen(game_x):
    return game_x

def game_y_to_screen(game_y):
    return -game_y + SCREEN_HEIGHT + camera_y

def screen_y_to_game(screen_y):
    return -screen_y + SCREEN_HEIGHT + camera_y

def game_coordinate_to_screen(game_x, game_y):
    return (game_x_to_screen(game_x), game_y_to_screen(game_y))

# classes
class Rocket:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self):
        pygame.draw.rect(screen, "brown", (game_x_to_screen(self.x), game_y_to_screen(self.y), 15, 23))

    def detect_player(self):
        global bin_y_speed, flying_by_rocket
        if (
            bin_x >= self.x - BIN_WIDTH / 2 and
            bin_x <= self.x + 15 + BIN_WIDTH / 2 and
            bin_y >= self.y - 23 and
            bin_y <= self.y
        ):
            bin_y_speed = 20
            flying_by_rocket = True

class Platform:
    # types of platforms:
    # 0: normal
    # 1: bouncy
    def __init__(self, starting_y):
        self.x = random.randint(0, int(SCREEN_WIDTH - PLATFORM_WIDTH))
        self.y = starting_y
        self.active = True
        self.pick_settings()

    def pick_settings(self):
        self.bouncy = random.randint(1,8) == 1
        self.breaks = random.randint(1,7) == 1
        if random.randint(1, 10) == 1:
            self.x_speed = 3
        else:
            self.x_speed = 0
        rocket_chance = random.randint(1,12)
        if rocket_chance == 1:
            self.rocket = Rocket(self.x, self.y + 20)
        else:
            self.rocket = None

    def make_platform_move(self):
        if self.active:
            self.x += self.x_speed
            if self.rocket is not None:
                self.rocket.x += self.x_speed
            if self.x >= SCREEN_WIDTH - 10 - PLATFORM_WIDTH:
                self.x_speed *= -1
            if self.x <= 10:
                self.x_speed *= -1
    
    def reset_platform(self):
        self.y += SCREEN_HEIGHT
        self.x = random.randint(0, int(SCREEN_WIDTH - PLATFORM_WIDTH))
        self.pick_settings()
    
    def draw(self):
        global platforms_to_hide
        global hidden_platforms
        if self.active:
            if game_y_to_screen(self.y) > SCREEN_HEIGHT:
                if hidden_platforms < platforms_to_hide and random.randint(1,5) == 1:
                    hidden_platforms += 1
                    self.active = False
                else:
                    self.reset_platform()
            if self.breaks:
                #pygame.draw.rect(screen, "#e76349", (game_x_to_screen(self.x), game_y_to_screen(self.y), PLATFORM_WIDTH, PLATFORM_THICKNESS))
                screen.blit(BREAKABLE_PLATFORM_IMAGE, game_coordinate_to_screen(self.x, self.y))
            elif self.bouncy:
                screen.blit(BOUNCY_PLATFORM_IMAGE, game_coordinate_to_screen(self.x, self.y))
                # pygame.draw.rect(screen, "#a3ce49", (game_x_to_screen(self.x), game_y_to_screen(self.y), PLATFORM_WIDTH, PLATFORM_THICKNESS))
            else:
                pygame.draw.rect(screen, "#393939", (game_x_to_screen(self.x), game_y_to_screen(self.y), PLATFORM_WIDTH, PLATFORM_THICKNESS))
        if self.rocket is not None:
            self.rocket.draw()

    def bounce_player(self):
        global bin_y_speed
        if self.active:
            if (
                bin_x >= self.x - BIN_WIDTH / 2 and
                bin_x <= self.x + PLATFORM_WIDTH + BIN_WIDTH / 2 and
                bin_y >= self.y - PLATFORM_THICKNESS and
                bin_y <= self.y and
                bin_y_speed < 0 and
                alive
            ):
                if self.breaks:
                    self.reset_platform()
                    bin_y_speed = 10
                elif self.bouncy:
                    bin_y_speed = 17
                else:
                    bin_y_speed = 10
            if self.rocket is not None:
                self.rocket.detect_player()

class Bullet:
    def __init__(self, starting_x, starting_y):
        self.x = starting_x
        self.y = starting_y

    def draw(self):
        pygame.draw.circle(screen, "#93c47d", game_coordinate_to_screen(self.x, self.y), 5)

    def move_up(self):
        self.y += 30

    def kill_touching_monsters(self, monsters):
        for monster in monsters:
            if math.sqrt((self.x - monster.x) ** 2 + (self.y - monster.y) ** 2) <= 35:
                monster.y = monster.y + 1500
                monster.x = random.randint(30, SCREEN_WIDTH - 30)

class Monster:
    def __init__(self, starting_y):
        self.x = random.randint(30, SCREEN_WIDTH - 30)
        self.y = starting_y

    def draw(self):
        if game_y_to_screen(self.y) > SCREEN_HEIGHT + 30:
            self.y = self.y + 1500
            monster.x = random.randint(30, SCREEN_WIDTH - 30)
        pygame.draw.circle(screen, "black", game_coordinate_to_screen(self.x, self.y), 30)

    def kill_touching_player(self):
        global alive, bin_y_speed
        if (
            bin_x + BIN_WIDTH > self.x - 30 and
            bin_x < self.x - 30 + 60 and
            bin_y + BIN_HEIGHT > self.y - 30 and
            bin_y < self.y - 30 + 60 and
            flying_by_rocket == False
        ):
            bin_y_speed = -2
            alive = False

platforms = []
bullets = []
monsters = []

def main_menu_game_stuff():
    global bin_x, platforms, game_still_going, BG_COLOR

    setup_game_stuff()
    # Main menu "game" setup
    bin_x = BIN_WIDTH * 2
    platforms = [
        Platform(120)
    ]
    platforms[0].x = bin_x - PLATFORM_WIDTH/2
    platforms[0].bouncy = False
    platforms[0].breaks = False
    platforms[0].x_speed = 0

    game_still_going = False # now on the main menu
    BG_COLOR = "#fdf1e7"

def setup_game_stuff():
    global platforms, bullets, monsters, bin_y_speed, bin_y, bin_x, alive, camera_y, highest_bin_y, starting_bin_y, BG_COLOR

    bin_y_speed = 0
    bin_x = SCREEN_WIDTH/2
    bin_y = SCREEN_HEIGHT * .3
    alive = True
    camera_y = 0
    starting_bin_y = bin_y
    highest_bin_y = bin_y
    BG_COLOR = "#fdf1e7"

    platforms = [
        Platform(30), # starting platform
        Platform(30 + bin_y - BIN_HEIGHT),
        Platform(30 + bin_y - BIN_HEIGHT + 100),
        Platform(30 + bin_y - BIN_HEIGHT + 200),
        Platform(30 + bin_y - BIN_HEIGHT + 300),
        Platform(30 + bin_y - BIN_HEIGHT + 400),
        Platform(30 + bin_y - BIN_HEIGHT + 450),
        Platform(30 + bin_y - BIN_HEIGHT + 500),
        Platform(30 + bin_y - BIN_HEIGHT + 600),
        Platform(30 + bin_y - BIN_HEIGHT + 650),
        Platform(30 + bin_y - BIN_HEIGHT + 700),
        Platform(30 + bin_y - BIN_HEIGHT + 800),
        Platform(30 + bin_y - BIN_HEIGHT + 850)
    ]
    platforms[0].x = SCREEN_WIDTH / 2 - PLATFORM_WIDTH

    bullets = []
    monsters = [Monster(1000)]

    
def restart_ui():
    pygame.draw.rect(screen, "red", (SCREEN_WIDTH - 100, 5, 80, 25))
    restart_text = RESTART_FONT.render("Restart", True, "black")
    screen.blit(restart_text, (SCREEN_WIDTH - 60 - restart_text.get_width()/2, 18 - restart_text.get_height()/2))

    mouse_pos = pygame.mouse.get_pos() # [x, y]
    mouse_pressed = pygame.mouse.get_pressed()[0]

    if (
        mouse_pos[0] > SCREEN_WIDTH - 100 and
        mouse_pos[0] < SCREEN_WIDTH - 100 + 80 and
        mouse_pos[1] > 5 and
        mouse_pos[1] < 5 + 25 and
        mouse_pressed
    ):
        setup_game_stuff()

# ui
def main_menu_ui():
    global game_still_going

    # mouse detection
    mouse_clicked = pygame.mouse.get_pressed()[0]
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Title Card
    # pygame.draw.rect(screen, "black", (40, 30, SCREEN_WIDTH - 80, 130))
    screen.blit(LOGO_IMAGE, (40,30))

    # Play
    pygame.draw.rect(screen, "black", (235, game_y_to_screen(170), 175, 75))
    if (
        mouse_clicked and
        mouse_x > 235 and
        mouse_x < 235 + 175 and
        mouse_y > game_y_to_screen(170) and
        mouse_y < game_y_to_screen(170) + 75
    ):
        game_still_going = True
        setup_game_stuff()

    # Settings, to be added later

def dead_ui():
    global game_still_going, BG_COLOR, platforms, bin_x

    # mouse detection
    mouse_clicked = pygame.mouse.get_pressed()[0]
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Try Again
    #pygame.draw.rect(screen, "red", (SCREEN_WIDTH/2 - 75, SCREEN_HEIGHT/2 - 35, 150, 70))
    screen.blit(TRY_AGAIN_IMAGE, (SCREEN_WIDTH/2 - 75, SCREEN_HEIGHT/2 - 35))
    if (
        mouse_clicked and
        mouse_x > SCREEN_WIDTH/2 - 75 and
        mouse_x < SCREEN_WIDTH/2 - 75 + 150 and
        mouse_y > SCREEN_HEIGHT/2 - 35 and
        mouse_y < SCREEN_HEIGHT/2 - 35 + 70
    ):
        setup_game_stuff()
    
    # Main Menu
    #pygame.draw.rect(screen, "red", (SCREEN_WIDTH/2 - 75, SCREEN_HEIGHT/2 + 52, 150, 70))
    screen.blit(MAIN_MENU_IMAGE, (SCREEN_WIDTH/2 - 75, SCREEN_HEIGHT/2 + 52))
    if (
        mouse_clicked and
        mouse_x > SCREEN_WIDTH/2 - 75 and
        mouse_x < SCREEN_WIDTH/2 - 75 + 150 and
        mouse_y > SCREEN_HEIGHT/2 + 52 and
        mouse_y < SCREEN_HEIGHT/2 + 52 + 70
    ):
        main_menu_game_stuff()

    # KITCAT!!!!!!!!!!!! =)
    screen.blit(KITCAT_IMAGE, (145, 50))

main_menu_game_stuff()

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # shooting
        if event.type == pygame.KEYDOWN and event.key == pygame.K_UP and game_still_going:
            bin_shooting = 25
            bullets.append(Bullet(bin_x, bin_y + BIN_HEIGHT + 5))

    # score
    score = camera_y/3

    # move down and jumping
    bin_y = bin_y + bin_y_speed
    bin_y_speed = bin_y_speed - .20
    if flying_by_rocket == True and bin_y_speed <= 0:
        flying_by_rocket = False

    for platform in platforms:
        platform.bounce_player()
        platform.make_platform_move()

    if game_still_going:
        # moving the camera
        if bin_y > highest_bin_y:
            highest_bin_y = bin_y
        camera_y = highest_bin_y - starting_bin_y

        # timers
        bin_shooting -= 1

        for i in range(len(bullets)):
            bullet = bullets[-i + len(bullets) - 1]
            bullet.move_up()
            bullet.kill_touching_monsters(monsters)
            if bullet.y > bin_y + SCREEN_HEIGHT * 2:
                bullets.pop(-i + len(bullets) - 1)

        for monster in monsters:
            monster.kill_touching_player()

        # getting back on the screen when going off screen
        if bin_x > SCREEN_WIDTH + BIN_WIDTH/2:
            bin_x = -BIN_WIDTH/2
        if bin_x < -BIN_WIDTH/2:
            bin_x = SCREEN_WIDTH + BIN_WIDTH/2

        # moving
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_LEFT]:
            bin_x = bin_x - 5.67
            bin_moving_right = False
        if pressed_keys[pygame.K_RIGHT]:
            bin_x = bin_x + 5.67
            bin_moving_right = True

        if flying_by_rocket:
            CURRENT_BIN_IMAGE = SUPER_BIN_IMAGE
        elif bin_shooting > 0:
            CURRENT_BIN_IMAGE = SHOOTING_BIN_IMAGE
        elif score < 2000:
            if bin_moving_right:
                CURRENT_BIN_IMAGE = RIGHT_BIN_IMAGE
            else:
                CURRENT_BIN_IMAGE = LEFT_BIN_IMAGE
        elif score < 5000:
            if bin_moving_right == False:
                CURRENT_BIN_IMAGE = LEFT_BIN_BALLIN_IMAGE
            else:
                CURRENT_BIN_IMAGE = RIGHT_BIN_BALLIN_IMAGE
        else:
            CURRENT_BIN_IMAGE = PARROT_IMAGE

        # losing
        if game_y_to_screen(bin_y) >= SCREEN_HEIGHT + BIN_HEIGHT:
            alive = False

        if alive == False:
            BG_COLOR = ("#FFDCDC")

    # fill the screen with a color to wipe away anything from last frame
    screen.fill(BG_COLOR)

    screen.blit(CURRENT_BIN_IMAGE, (game_x_to_screen(bin_x -(BIN_WIDTH/2)), game_y_to_screen(bin_y+BIN_HEIGHT)))
    for platform in platforms:
        platform.draw()

    for bullet in bullets:
        bullet.draw()

    for monster in monsters:
        monster.draw()

    # score
    if game_still_going:
        SCORE_IMAGE = SCORE_FONT.render(str(int(score)), True, "black")
        screen.blit(SCORE_IMAGE, (10, 10))
        restart_ui()

    # ui
    if not alive:
        dead_ui()

    if not game_still_going:
        main_menu_ui()

    # changing overtime
    if score >= 1000:
        platforms_to_hide = 2
    if score >= 2000:
        platforms_to_hide = 4

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
