import pygame
import sys
import random

# --- Game Configuration ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60

# Pixelation
PIXEL_SCALE = 4 # Higher number = more pixelated render target
BUFFER_WIDTH = SCREEN_WIDTH // PIXEL_SCALE
BUFFER_HEIGHT = SCREEN_HEIGHT // PIXEL_SCALE

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GROUND_COLOR = (80, 50, 20)
DINO_COLOR = (0, 150, 0)
OBSTACLE_COLORS = [(150, 75, 0), (200, 100, 0), (100, 50, 0)]
SKY_COLOR = (135, 206, 250) # Light Sky Blue


# Player Properties
GRAVITY = 0.6 / PIXEL_SCALE # Adjusted for buffer scale
JUMP_FORCE = -12 / PIXEL_SCALE # Adjusted for buffer scale

# Game Properties
INITIAL_GAME_SPEED = 6 / PIXEL_SCALE # Adjusted for buffer scale
GAME_SPEED_INCREASE = 0.01 / PIXEL_SCALE
OBSTACLE_INTERVAL = 75 # Frames between potential obstacles
MIN_OBSTACLE_GAP = 150 / PIXEL_SCALE # Min horizontal pixels between obstacles (in buffer)

# --- Pygame Setup ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# Create the low-resolution buffer surface
pixel_buffer = pygame.Surface((BUFFER_WIDTH, BUFFER_HEIGHT))
pygame.display.set_caption("Pixel Dino Runner")
clock = pygame.time.Clock()
font_large = pygame.font.SysFont('monospace', 50, bold=True)
font_medium = pygame.font.SysFont('monospace', 30)
font_small = pygame.font.SysFont('monospace', 20)

# --- Global Game Variables ---
game_speed = INITIAL_GAME_SPEED
score = 0
game_state = 'start' # 'start', 'playing', 'gameOver'
ground_level = BUFFER_HEIGHT * 0.8
frame_count = 0 # Manual frame counter

# --- Helper Functions ---
def draw_text(text, font, color, surface, x, y, center=True):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    if center:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

# Simplified background drawing
def draw_background(surface):
    surface.fill(SKY_COLOR) # Base sky color
    # Draw Ground
    pygame.draw.rect(surface, GROUND_COLOR, (0, ground_level, BUFFER_WIDTH, BUFFER_HEIGHT - ground_level))


# --- Sprite Classes ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = 20 / PIXEL_SCALE
        # Create initial image (will be updated)
        self.image = pygame.Surface([self.size, self.size + self.size * 0.3]) # Slightly taller for legs
        self.image.set_colorkey(BLACK) # Make black transparent
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (60 / PIXEL_SCALE, ground_level)
        self.vy = 0
        self.on_ground = True
        self._draw_shape() # Initial draw

    def _draw_shape(self):
        self.image.fill(BLACK) # Clear previous drawing
        body_rect = pygame.Rect(0, 0, self.size, self.size)
        head_rect = pygame.Rect(self.size * 0.7, -self.size * 0.3, self.size * 0.6, self.size * 0.6)
        tail_rect = pygame.Rect(-self.size * 0.4, self.size * 0.3, self.size * 0.4, self.size * 0.3)

        pygame.draw.rect(self.image, DINO_COLOR, body_rect.move(0, self.size * 0.3)) # Move body down for legs
        pygame.draw.rect(self.image, DINO_COLOR, head_rect.move(0, self.size * 0.3))
        pygame.draw.rect(self.image, DINO_COLOR, tail_rect.move(0, self.size * 0.3))

        # Legs - simple animation
        leg_y = self.size + self.size * 0.2
        if self.on_ground and frame_count % 10 < 5: # Running step 1
           pygame.draw.rect(self.image, DINO_COLOR, (self.size * 0.2, leg_y, self.size * 0.2, self.size*0.3))
           pygame.draw.rect(self.image, DINO_COLOR, (self.size * 0.6, leg_y, self.size * 0.2, self.size*0.3))
        else: # Running step 2 or jumping
           pygame.draw.rect(self.image, DINO_COLOR, (self.size * 0.3, leg_y, self.size * 0.2, self.size*0.3))
           pygame.draw.rect(self.image, DINO_COLOR, (self.size * 0.7, leg_y - self.size*0.1, self.size * 0.2, self.size*0.3)) # one leg slightly back

    def jump(self):
        if self.on_ground:
            self.vy = JUMP_FORCE
            self.on_ground = False

    def update(self):
        # Apply gravity
        self.vy += GRAVITY
        self.rect.y += self.vy

        # Check ground collision
        if self.rect.bottom >= ground_level:
            self.rect.bottom = ground_level
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False

        # Redraw the dino shape for animation
        self._draw_shape()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.w = random.uniform(15, 40) / PIXEL_SCALE
        self.min_h = 20 / PIXEL_SCALE
        self.max_h = 50 / PIXEL_SCALE
        self.h = random.uniform(self.min_h, self.max_h)
        self.image = pygame.Surface([self.w, self.h])
        self.image.fill(random.choice(OBSTACLE_COLORS))
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (BUFFER_WIDTH, ground_level)

    def update(self):
        self.rect.x -= game_speed
        if self.rect.right < 0:
            self.kill() # Remove sprite if it goes off-screen


# --- Game Reset Function ---
def reset_game():
    global score, game_speed, frame_count, game_state, player, all_sprites, obstacles

    score = 0
    game_speed = INITIAL_GAME_SPEED
    frame_count = 0
    game_state = 'start'

    # Sprite Groups
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)


# --- Initial Game Setup ---
reset_game()

# --- Main Game Loop ---
running = True
last_obstacle_spawn_time = 0 # Use frame_count for simple timing
last_obstacle_right_edge = BUFFER_WIDTH # Track last obstacle position

while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                if game_state == 'playing':
                    player.jump()
                elif game_state == 'start':
                    game_state = 'playing'
            if (event.key == pygame.K_r) and game_state == 'gameOver':
                reset_game()

    # --- Game Logic ---
    if game_state == 'playing':
        frame_count += 1
        game_speed += GAME_SPEED_INCREASE / FPS # Gradual speed increase

        # Update Sprites
        all_sprites.update()

        # Spawn obstacles
        can_spawn = True
        if obstacles: # Check gap if obstacles exist
            # Find the obstacle with the maximum right x-coordinate
            # This is safer than assuming the last one added is the rightmost one
            # if they spawn very quickly or have varying widths
            try:
                # This might fail if obstacles group is briefly empty during spawn check
                last_obstacle = max(obstacles, key=lambda obs: obs.rect.right)
                last_obstacle_right_edge = last_obstacle.rect.right
                if BUFFER_WIDTH - last_obstacle_right_edge < MIN_OBSTACLE_GAP:
                    can_spawn = False
            except ValueError: # Handle case where obstacles group is empty
                 can_spawn = True


        # Use frame_count for timing, similar to p5 version
        if frame_count - last_obstacle_spawn_time > OBSTACLE_INTERVAL and can_spawn:
             if random.random() < 0.6: # Chance to spawn
                new_obstacle = Obstacle()
                obstacles.add(new_obstacle)
                all_sprites.add(new_obstacle)
                last_obstacle_spawn_time = frame_count # Reset timer

        # Check for collisions
        if pygame.sprite.spritecollide(player, obstacles, False):
            game_state = 'gameOver'

        # Update score (count passed obstacles indirectly)
        if frame_count % (FPS // 2) == 0: # Increment score every half second
            score += 1

        # Background updating is no longer needed here


    # --- Drawing ---
    # 1. Draw game elements to the low-res buffer
    draw_background(pixel_buffer) # Draws sky and ground
    if game_state == 'start':
        # Draw static player on start screen
        player.update() # Update animation only
        all_sprites.draw(pixel_buffer)
    elif game_state == 'playing':
        all_sprites.draw(pixel_buffer)
    elif game_state == 'gameOver':
        # Draw sprites in their final position
        all_sprites.draw(pixel_buffer)


    # 2. Scale the low-res buffer to the main screen
    scaled_buffer = pygame.transform.scale(pixel_buffer, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_buffer, (0, 0))

    # 3. Draw UI elements directly onto the main screen (full resolution)
    draw_text(f"Score: {score}", font_medium, WHITE, screen, 20, 20, center=False)

    if game_state == 'start':
        # Transparent overlay box
        overlay = pygame.Surface((SCREEN_WIDTH * 0.8, SCREEN_HEIGHT * 0.4), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 180)) # White with alpha
        screen.blit(overlay, (SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.3))
        # Text on overlay
        draw_text("PIXEL DINO RUNNER", font_large, BLACK, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.4)
        draw_text("Press [SPACE] or [UP] to Jump", font_medium, BLACK, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.5)
        draw_text("Press [SPACE] or [UP] to Start", font_medium, BLACK, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.6)

    elif game_state == 'gameOver':
         # Transparent overlay box
        overlay = pygame.Surface((SCREEN_WIDTH * 0.6, SCREEN_HEIGHT * 0.4), pygame.SRCALPHA)
        overlay.fill((255, 0, 0, 180)) # Red with alpha
        screen.blit(overlay, (SCREEN_WIDTH * 0.2, SCREEN_HEIGHT * 0.3))
        # Text on overlay
        draw_text("GAME OVER", font_large, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.4)
        draw_text(f"Final Score: {score}", font_medium, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.5)
        draw_text("Press [R] to Restart", font_small, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.6)

    elif game_state == 'playing':
        # Only show score and maybe jump instruction if needed
        # draw_text("[SPACE] = Jump", font_small, WHITE, screen, SCREEN_WIDTH - 20, 20, center=False) # Optional reminder
        pass # Keep it clean during play


    # --- Update Display ---
    pygame.display.flip()

    # --- Control Frame Rate ---
    clock.tick(FPS)

# --- Quit Pygame ---
pygame.quit()
sys.exit()