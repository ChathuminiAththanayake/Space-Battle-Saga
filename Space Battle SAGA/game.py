import pygame
import os
from PIL import Image

# --- Initialize Pygame mixer for optimized sound playback ---
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.font.init()

# --- Game window setup ---
WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Battle SAGA")

# --- Colors used---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BUTTON_BASE = (0, 200, 255)
BUTTON_HOVER = (0, 255, 255)

# --- Game constants ---
BORDER = pygame.Rect(WIDTH // 2 - 5, 0, 10, HEIGHT)
FPS = 60
VEL = 5
BULLET_VEL = 7
MAX_BULLETS = 3
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 115, 110

# --- Events ---
YELLOW_HIT = pygame.USEREVENT + 1
RED_HIT = pygame.USEREVENT + 2

# --- Fonts ---
HEALTH_FONT = pygame.font.SysFont('comicsans', 40)
WINNER_FONT = pygame.font.SysFont('comicsans', 100)
BUTTON_FONT = pygame.font.SysFont('comicsans', 50)

# --- Load spaceship assets ---
YELLOW_SPACESHIP_IMAGE = pygame.image.load(os.path.join('Assets', 'spaceship_yellow.png'))
YELLOW_SPACESHIP = pygame.transform.rotate(
    pygame.transform.scale(YELLOW_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90)

RED_SPACESHIP_IMAGE = pygame.image.load(os.path.join('Assets', 'spaceship_red.png'))
RED_SPACESHIP = pygame.transform.rotate(
    pygame.transform.scale(RED_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 270)

# Menu background
MENU_BG = pygame.image.load(os.path.join('Assets', 'menu.jpg'))
MENU_BG = pygame.transform.scale(MENU_BG, (WIDTH, HEIGHT))

# --- Load intro screen GIF (space.gif) ---
intro_screen_gif = Image.open(os.path.join('Assets', 'space.gif'))
INTRO_FRAMES = []
try:
    while True:
        frame = intro_screen_gif.convert('RGBA')
        mode = frame.mode
        size = frame.size
        data = frame.tobytes()
        py_image = pygame.image.fromstring(data, size, mode)
        py_image = pygame.transform.scale(py_image, (WIDTH, HEIGHT))
        INTRO_FRAMES.append(py_image)
        intro_screen_gif.seek(intro_screen_gif.tell() + 1)
except EOFError:
    pass

# --- Load gameplay background GIF (intro.gif) ---
game_bg_gif = Image.open(os.path.join('Assets', 'intro.gif'))
SPACE_FRAMES = []
try:
    while True:
        frame = game_bg_gif.convert('RGBA')
        mode = frame.mode
        size = frame.size
        data = frame.tobytes()
        py_image = pygame.image.fromstring(data, size, mode)
        py_image = pygame.transform.scale(py_image, (WIDTH, HEIGHT))
        SPACE_FRAMES.append(py_image)
        game_bg_gif.seek(game_bg_gif.tell() + 1)
except EOFError:
    pass

# --- Load the end screen GIF (end.gif) ---
end_gif = Image.open(os.path.join('Assets', 'end.gif'))
END_FRAMES = []
try:
    while True:
        frame = end_gif.convert('RGBA')
        mode = frame.mode
        size = frame.size
        data = frame.tobytes()
        py_image = pygame.image.fromstring(data, size, mode)
        py_image = pygame.transform.scale(py_image, (WIDTH, HEIGHT))
        END_FRAMES.append(py_image)
        end_gif.seek(end_gif.tell() + 1)
except EOFError:
    pass

# Frame control
frame_index = 0
FRAME_DELAY = 100
last_update = pygame.time.get_ticks()

# --- audios used ---
pygame.mixer.music.load(os.path.join('Assets', 'music.mp3'))
pygame.mixer.music.set_volume(0.3)

BULLET_FIRE_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'fire.mp3'))
BULLET_HIT_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'hit.mp3'))
GAME_OVER_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'over.mp3'))


# --- Draw window ---
def draw_window(red, yellow, red_bullets, yellow_bullets, red_health, yellow_health, current_frame):
    WIN.blit(current_frame, (0, 0))
    pygame.draw.rect(WIN, BLACK, BORDER)

    red_health_text = HEALTH_FONT.render(f"Health: {red_health}", 1, WHITE)
    yellow_health_text = HEALTH_FONT.render(f"Health: {yellow_health}", 1, WHITE)
    WIN.blit(red_health_text, (WIDTH - red_health_text.get_width() - 10, 10))
    WIN.blit(yellow_health_text, (10, 10))

    WIN.blit(YELLOW_SPACESHIP, (yellow.x, yellow.y))
    WIN.blit(RED_SPACESHIP, (red.x, red.y))

    for bullet in red_bullets:
        pygame.draw.rect(WIN, RED, bullet)
    for bullet in yellow_bullets:
        pygame.draw.rect(WIN, YELLOW, bullet)

    pygame.display.update()


# --- Handle spaceship movements ---
def yellow_handle_movement(keys, yellow):
    if keys[pygame.K_a] and yellow.x - VEL > 0:
        yellow.x -= VEL
    if keys[pygame.K_d] and yellow.x + VEL + yellow.width < BORDER.x:
        yellow.x += VEL
    if keys[pygame.K_w] and yellow.y - VEL > 0:
        yellow.y -= VEL
    if keys[pygame.K_s] and yellow.y + VEL + yellow.height < HEIGHT:
        yellow.y += VEL


def red_handle_movement(keys, red):
    if keys[pygame.K_LEFT] and red.x - VEL > BORDER.x + BORDER.width:
        red.x -= VEL
    if keys[pygame.K_RIGHT] and red.x + VEL + red.width < WIDTH:
        red.x += VEL
    if keys[pygame.K_UP] and red.y - VEL > 0:
        red.y -= VEL
    if keys[pygame.K_DOWN] and red.y + VEL + red.height < HEIGHT:
        red.y += VEL


# --- Bullets handling for both spaceships---
def handle_bullets(yellow_bullets, red_bullets, yellow, red):
    for bullet in yellow_bullets[:]:
        bullet.x += BULLET_VEL
        if red.colliderect(bullet):
            pygame.event.post(pygame.event.Event(RED_HIT))
            yellow_bullets.remove(bullet)
            BULLET_HIT_SOUND.play()
        elif bullet.x > WIDTH:
            yellow_bullets.remove(bullet)

    for bullet in red_bullets[:]:
        bullet.x -= BULLET_VEL
        if yellow.colliderect(bullet):
            pygame.event.post(pygame.event.Event(YELLOW_HIT))
            red_bullets.remove(bullet)
            BULLET_HIT_SOUND.play()
        elif bullet.x < 0:
            red_bullets.remove(bullet)


# --- Graphical Button --
def draw_button(surface, text, center, width=300, height=70, base_color=BUTTON_BASE, hover_color=BUTTON_HOVER):
    mouse_pos = pygame.mouse.get_pos()
    rect = pygame.Rect(0, 0, width, height)
    rect.center = center

    # Shadows
    shadow_rect = rect.copy()
    shadow_rect.move_ip(5, 5)
    pygame.draw.rect(surface, BLACK, shadow_rect, border_radius=15)

    # Hover effect
    color = hover_color if rect.collidepoint(mouse_pos) else base_color
    pygame.draw.rect(surface, color, rect, border_radius=15)

    # Text
    text_surf = BUTTON_FONT.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=center)
    surface.blit(text_surf, text_rect)

    return rect


# --- Start menu ---
def draw_start_menu():
    WIN.blit(MENU_BG, (0, 0))
    single_rect = draw_button(WIN, "Single Player", (WIDTH // 2, 300))
    dual_rect = draw_button(WIN, "Dual Player", (WIDTH // 2, 400))
    pygame.display.update()
    return single_rect, dual_rect


def start_menu():
    run = True
    while run:
        single_rect, dual_rect = draw_start_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if single_rect.collidepoint(mouse_pos):
                    return "single"
                elif dual_rect.collidepoint(mouse_pos):
                    return "dual"


# --- Simple AI ---
def red_ai_movement(red, yellow):
    if red.y + red.height / 2 < yellow.y + yellow.height / 2:
        red.y += VEL
    elif red.y + red.height / 2 > yellow.y + yellow.height / 2:
        red.y -= VEL
    if red.y < 0:
        red.y = 0
    if red.y + red.height > HEIGHT:
        red.y = HEIGHT - red.height


# --- Intro Screen ---
def intro_screen():
    global frame_index, last_update
    intro_running = True
    load_progress = 0
    loading_speed = 0.5
    clock = pygame.time.Clock()

    blink_colors = [(0, 200, 255), (0, 255, 255), (0, 150, 200)]
    color_index = 0
    color_change_time = 200
    last_color_change = pygame.time.get_ticks()

    while intro_running:
        clock.tick(FPS)
        now = pygame.time.get_ticks()
        if now - last_update > FRAME_DELAY:
            frame_index = (frame_index + 1) % len(INTRO_FRAMES)
            last_update = now
        current_frame = INTRO_FRAMES[frame_index]
        WIN.blit(current_frame, (0, 0))

        # Title with shadow
        title_font = pygame.font.SysFont('comicsans', 90)
        title_text = title_font.render("Space Battle SAGA", True, WHITE)
        shadow_text = title_font.render("Space Battle SAGA", True, BLACK)
        title_x = WIDTH // 2 - title_text.get_width() // 2
        title_y = HEIGHT // 4
        WIN.blit(shadow_text, (title_x + 3, title_y + 3))
        WIN.blit(title_text, (title_x, title_y))

        # Blinking colors
        if now - last_color_change > color_change_time:
            color_index = (color_index + 1) % len(blink_colors)
            last_color_change = now
        bar_color = blink_colors[color_index]

        # Loading bar
        bar_width, bar_height = 500, 40
        bar_x, bar_y = WIDTH // 2 - bar_width // 2, HEIGHT // 2
        pygame.draw.rect(WIN, WHITE, (bar_x, bar_y, bar_width, bar_height), 3)
        pygame.draw.rect(WIN, bar_color,
                         (bar_x + 3, bar_y + 3, int((bar_width - 6) * (load_progress / 100)), bar_height - 6))

        if load_progress < 100:
            load_progress += loading_speed
        else:
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                prompt_font = pygame.font.SysFont('comicsans', 40)
                prompt_text = prompt_font.render("Press any key to continue", True, WHITE)
                WIN.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 + 60))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if load_progress >= 100 and event.type == pygame.KEYDOWN:
                intro_running = False
    return True


# --- End screen with Play Again and Quit options ---
def end_screen(winner_text):
    global frame_index, last_update
    clock = pygame.time.Clock()
    run = True
    frame_index = 0
    last_update = pygame.time.get_ticks()

    while run:
        clock.tick(FPS)
        now = pygame.time.get_ticks()
        if now - last_update > FRAME_DELAY:
            frame_index = (frame_index + 1) % len(END_FRAMES)
            last_update = now
        current_frame = END_FRAMES[frame_index]
        WIN.blit(current_frame, (0, 0))

        # Display winner at the top of the screen
        winner_surf = WINNER_FONT.render(winner_text, True, WHITE)
        WIN.blit(winner_surf, (WIDTH // 2 - winner_surf.get_width() // 2, 50))

        # Draw buttons
        play_again_rect = draw_button(WIN, "Play Again", (WIDTH // 2, 300))
        quit_rect = draw_button(WIN, "Quit", (WIDTH // 2, 400))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if play_again_rect.collidepoint(mouse_pos):
                    return "play_again"
                elif quit_rect.collidepoint(mouse_pos):
                    return "quit"


# --- Main function ---
def main():
    global frame_index, last_update
    first_time = True
    pygame.mixer.music.play(-1)

    while True:
        # Only show intro first time
        if first_time:
            if not intro_screen():
                return
            first_time = False

        mode = start_menu()
        if mode is None:
            return

        red = pygame.Rect(700, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
        yellow = pygame.Rect(100, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)

        red_bullets = []
        yellow_bullets = []

        red_health = 10
        yellow_health = 10

        clock = pygame.time.Clock()
        run = True
        last_red_bullet = pygame.time.get_ticks()
        bullet_delay = 800

        while run:
            clock.tick(FPS)
            now = pygame.time.get_ticks()
            if now - last_update > FRAME_DELAY:
                frame_index = (frame_index + 1) % len(SPACE_FRAMES)
                last_update = now
            current_frame = SPACE_FRAMES[frame_index]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LCTRL and len(yellow_bullets) < MAX_BULLETS:
                        bullet = pygame.Rect(yellow.x + yellow.width, yellow.y + yellow.height // 2 - 2, 10, 5)
                        yellow_bullets.append(bullet)
                        BULLET_FIRE_SOUND.stop()
                        BULLET_FIRE_SOUND.play()
                    if mode == "dual" and event.key == pygame.K_RCTRL and len(red_bullets) < MAX_BULLETS:
                        bullet = pygame.Rect(red.x, red.y + red.height // 2 - 2, 10, 5)
                        red_bullets.append(bullet)
                        BULLET_FIRE_SOUND.stop()
                        BULLET_FIRE_SOUND.play()
                if event.type == RED_HIT:
                    red_health -= 1
                if event.type == YELLOW_HIT:
                    yellow_health -= 1

            winner_text = ""
            if red_health <= 0:
                winner_text = "Yellow Wins!"
            if yellow_health <= 0:
                winner_text = "Red Wins!"
            if winner_text != "":
                GAME_OVER_SOUND.play()
                choice = end_screen(winner_text)
                if choice == "play_again":
                    break  # restart the while True loop (jump to menu)
                else:
                    pygame.quit()
                    return

            keys_pressed = pygame.key.get_pressed()
            yellow_handle_movement(keys_pressed, yellow)
            if mode == "single":
                red_ai_movement(red, yellow)
                if len(red_bullets) < MAX_BULLETS and pygame.time.get_ticks() - last_red_bullet > bullet_delay:
                    bullet = pygame.Rect(red.x, red.y + red.height // 2 - 2, 10, 5)
                    red_bullets.append(bullet)
                    BULLET_FIRE_SOUND.stop()
                    BULLET_FIRE_SOUND.play()
                    last_red_bullet = pygame.time.get_ticks()
            else:
                red_handle_movement(keys_pressed, red)

            handle_bullets(yellow_bullets, red_bullets, yellow, red)
            draw_window(red, yellow, red_bullets, yellow_bullets, red_health, yellow_health, current_frame)


if __name__ == "__main__":
    main()
