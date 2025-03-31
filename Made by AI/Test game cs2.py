import pygame
import sys
import random
import math

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0) # For enemy bullets
WALL_COLOR = (130, 130, 130)
PLAYER_COLOR = BLUE
ENEMY_COLOR = RED
PLAYER_BULLET_COLOR = YELLOW
ENEMY_BULLET_COLOR = ORANGE

# --- Map Definition ---
GAME_MAP = [
    "####################",
    "#P........#........#",
    "#.........#........#",
    "#....E....#...E....#",
    "#####.....#....#####",
    "#.........#........#",
    "#...E.....#........#",
    "#.........#####....#",
    "#.........#........#",
    "#....E....#...E....#",
    "####################",
]
MAP_HEIGHT_TILES = len(GAME_MAP)
MAP_WIDTH_TILES = len(GAME_MAP[0])

# --- Helper Function: Line of Sight (Raycasting) ---
def has_line_of_sight(start_pos, end_pos, walls_group):
    """ Checks if there is a clear line between start_pos and end_pos, blocked by walls """
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    distance = math.hypot(dx, dy)
    if distance == 0:
        return True # Target is at the start position

    steps = int(distance / (TILE_SIZE / 4)) # Check every quarter tile along the line
    if steps == 0: steps = 1

    for i in range(1, steps + 1):
        t = i / steps
        check_x = start_pos[0] + dx * t
        check_y = start_pos[1] + dy * t
        # Check if this point falls within any wall rectangle
        for wall in walls_group:
            if wall.rect.collidepoint(check_x, check_y):
                return False # Hit a wall
    return True # No walls hit

# --- Player Class ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([TILE_SIZE * 0.7, TILE_SIZE * 0.7])
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect(topleft=(x * TILE_SIZE, y * TILE_SIZE))
        self.health = 100
        self.speed = 4
        # Shooting cooldown
        self.shoot_cooldown = 250 # Milliseconds (4 shots per second)
        self.last_shot_time = 0

    def move(self, dx, dy, walls):
        if dx != 0:
            self.rect.x += dx
            collided_walls = pygame.sprite.spritecollide(self, walls, False)
            for wall in collided_walls:
                if dx > 0: self.rect.right = wall.rect.left
                if dx < 0: self.rect.left = wall.rect.right
        if dy != 0:
            self.rect.y += dy
            collided_walls = pygame.sprite.spritecollide(self, walls, False)
            for wall in collided_walls:
                if dy > 0: self.rect.bottom = wall.rect.top
                if dy < 0: self.rect.top = wall.rect.bottom
        self.rect.clamp_ip(pygame.Rect(0, 0, MAP_WIDTH_TILES * TILE_SIZE, MAP_HEIGHT_TILES * TILE_SIZE))

    def update(self, keys, walls):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = self.speed
        if dx != 0 and dy != 0:
             dx /= math.sqrt(2)
             dy /= math.sqrt(2)
        self.move(int(dx), int(dy), walls)

    def shoot(self, target_pos, current_time):
        # Check cooldown
        if current_time - self.last_shot_time < self.shoot_cooldown:
            return None # Still on cooldown

        self.last_shot_time = current_time # Update last shot time

        start_pos = self.rect.center
        target_x, target_y = target_pos
        dx = target_x - start_pos[0]
        dy = target_y - start_pos[1]
        distance = math.hypot(dx, dy)
        if distance == 0: return None
        dx /= distance
        dy /= distance
        bullet_start_x = start_pos[0] + dx * (self.rect.width / 2)
        bullet_start_y = start_pos[1] + dy * (self.rect.height / 2)

        # Create a player bullet
        bullet = Bullet(bullet_start_x, bullet_start_y, dx, dy, PLAYER_BULLET_COLOR)
        return bullet

# --- Enemy Class ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([TILE_SIZE * 0.7, TILE_SIZE * 0.7])
        self.image.fill(ENEMY_COLOR)
        self.rect = self.image.get_rect(topleft=(x * TILE_SIZE, y * TILE_SIZE))
        self.health = 50
        self.speed = 2
        self.move_timer = 0
        self.move_interval = random.randint(FPS // 2, FPS * 2)
        self.vx = 0
        self.vy = 0
        # Shooting AI
        self.shoot_cooldown = random.randint(1000, 2500) # Milliseconds (shoot every 1-2.5 secs if LoS)
        self.last_shot_time = 0
        self.vision_range = TILE_SIZE * 8 # How far the enemy can "see"

    def move(self, dx, dy, walls):
        if dx != 0:
            self.rect.x += dx
            collided_walls = pygame.sprite.spritecollide(self, walls, False)
            for wall in collided_walls:
                if dx > 0: self.rect.right = wall.rect.left
                if dx < 0: self.rect.left = wall.rect.right
                self.vx *= -random.uniform(0.8, 1.2)
        if dy != 0:
            self.rect.y += dy
            collided_walls = pygame.sprite.spritecollide(self, walls, False)
            for wall in collided_walls:
                if dy > 0: self.rect.bottom = wall.rect.top
                if dy < 0: self.rect.top = wall.rect.bottom
                self.vy *= -random.uniform(0.8, 1.2)
        self.rect.clamp_ip(pygame.Rect(0, 0, MAP_WIDTH_TILES * TILE_SIZE, MAP_HEIGHT_TILES * TILE_SIZE))

    def update(self, walls, player_pos, current_time):
        # --- Movement AI ---
        self.move_timer += 1
        if self.move_timer >= self.move_interval or (self.vx == 0 and self.vy == 0):
            self.move_timer = 0
            self.move_interval = random.randint(FPS // 2, FPS * 2)
            direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0),
                                        (1, 1), (1, -1), (-1, 1), (-1, -1)])
            speed_multiplier = self.speed / math.sqrt(2) if direction[0] != 0 and direction[1] != 0 else self.speed
            self.vx = direction[0] * speed_multiplier
            self.vy = direction[1] * speed_multiplier
        self.move(int(self.vx), int(self.vy), walls)

        # --- Shooting AI ---
        # Check cooldown
        if current_time - self.last_shot_time >= self.shoot_cooldown:
            # Check distance to player
            dist_to_player = math.hypot(player_pos[0] - self.rect.centerx, player_pos[1] - self.rect.centery)

            if dist_to_player <= self.vision_range:
                # Check Line of Sight
                if has_line_of_sight(self.rect.center, player_pos, walls):
                    # Shoot at the player
                    self.last_shot_time = current_time # Reset cooldown
                    return self.shoot(player_pos) # Return the bullet object
        return None # Did not shoot

    def shoot(self, target_pos):
        start_pos = self.rect.center
        target_x, target_y = target_pos
        dx = target_x - start_pos[0]
        dy = target_y - start_pos[1]
        distance = math.hypot(dx, dy)
        if distance == 0: return None
        dx /= distance
        dy /= distance
        bullet_start_x = start_pos[0] + dx * (self.rect.width / 2)
        bullet_start_y = start_pos[1] + dy * (self.rect.height / 2)

        # Create an enemy bullet
        bullet = Bullet(bullet_start_x, bullet_start_y, dx, dy, ENEMY_BULLET_COLOR)
        return bullet


# --- Bullet Class ---
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, color): # Added color parameter
        super().__init__()
        self.image = pygame.Surface([8, 8])
        self.image.set_colorkey(BLACK) # Make black transparent if needed
        # Draw bullet shape
        pygame.draw.circle(self.image, color, (4, 4), 4)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 8 # Slightly slower than player bullets
        self.vx = dx * self.speed
        self.vy = dy * self.speed
        self.spawn_time = pygame.time.get_ticks()
        self.lifespan = 3000 # Disappear after 3 seconds

    def update(self, walls):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if pygame.sprite.spritecollide(self, walls, False):
            self.kill()
        if not pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT).colliderect(self.rect):
             self.kill()
        if pygame.time.get_ticks() - self.spawn_time > self.lifespan:
            self.kill()

# --- Wall Class ---
class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([TILE_SIZE, TILE_SIZE])
        self.image.fill(WALL_COLOR)
        pygame.draw.rect(self.image, BLACK, self.image.get_rect(), 1) # Border
        self.rect = self.image.get_rect(topleft=(x * TILE_SIZE, y * TILE_SIZE))

# --- Main Game Function ---
def game():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Simple 2D Shooter - Space to Shoot")
    clock = pygame.time.Clock()
    pygame.font.init()
    ui_font = pygame.font.SysFont(None, 30)
    controls_font = pygame.font.SysFont(None, 24)
    message_font = pygame.font.SysFont(None, 72)

    # --- Create Sprite Groups ---
    all_sprites = pygame.sprite.Group()
    walls = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group() # Group for enemy shots

    player = None

    # --- Build Level ---
    for r, row in enumerate(GAME_MAP):
        for c, tile in enumerate(row):
            if tile == '#':
                wall = Wall(c, r)
                all_sprites.add(wall)
                walls.add(wall)
            elif tile == 'P':
                if player is None:
                   player = Player(c, r)
                   all_sprites.add(player)
            elif tile == 'E':
                enemy = Enemy(c, r)
                all_sprites.add(enemy)
                enemies.add(enemy)
    if player is None: sys.exit("Error: No Player 'P' in MAP!")

    # --- Game Loop ---
    running = True
    game_over = False
    win = False

    while running:
        current_time = pygame.time.get_ticks() # Get time for cooldown checks

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Remove MOUSEBUTTONDOWN check for shooting

        keys = pygame.key.get_pressed() # Get state of all keys once per frame

        # --- Spacebar Shooting ---
        if not game_over and keys[pygame.K_SPACE]:
             mouse_pos = pygame.mouse.get_pos() # Aim with mouse
             new_bullet = player.shoot(mouse_pos, current_time)
             if new_bullet:
                 all_sprites.add(new_bullet)
                 player_bullets.add(new_bullet)

        # --- Game Logic (Update) ---
        if not game_over:
            player.update(keys, walls) # Update player using keys state

            # Update Enemies and check if they shoot
            for enemy in enemies:
                enemy_shot = enemy.update(walls, player.rect.center, current_time)
                if enemy_shot:
                    all_sprites.add(enemy_shot)
                    enemy_bullets.add(enemy_shot)

            player_bullets.update(walls)
            enemy_bullets.update(walls)

            # Player Bullet - Enemy Collision
            hits = pygame.sprite.groupcollide(player_bullets, enemies, True, False)
            for bullet, hit_enemies in hits.items():
                for enemy in hit_enemies:
                    enemy.health -= 35 # Player bullet damage
                    if enemy.health <= 0: enemy.kill()

            # Enemy Bullet - Player Collision
            player_hit = pygame.sprite.spritecollide(player, enemy_bullets, True) # Kill bullet on hit
            for bullet in player_hit:
                 player.health -= 15 # Enemy bullet damage
                 if player.health < 0: player.health = 0 # Don't go below zero


            # --- Check Win/Loss Conditions ---
            if player.health <= 0:
                game_over = True
                win = False
            elif len(enemies) == 0:
                 game_over = True
                 win = True

        # --- Drawing ---
        screen.fill(BLACK)
        all_sprites.draw(screen)

        # Draw UI - Health, Enemy Count, CONTROLS
        health_text = ui_font.render(f"Health: {player.health}", True, WHITE)
        screen.blit(health_text, (10, 10))
        enemy_count_text = ui_font.render(f"Enemies Left: {len(enemies)}", True, WHITE)
        screen.blit(enemy_count_text, (10, 35))

        # Display Controls Permanently
        controls_y_start = SCREEN_HEIGHT - 60
        move_text = controls_font.render("Move: WASD / Arrows", True, WHITE)
        screen.blit(move_text, (10, controls_y_start))
        shoot_text = controls_font.render("Shoot: SPACE (Aim with Mouse)", True, WHITE)
        screen.blit(shoot_text, (10, controls_y_start + 20))

        # Game Over / Win Message
        if game_over:
            if win: message_text = message_font.render("YOU WIN!", True, GREEN)
            else: message_text = message_font.render("GAME OVER", True, RED)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0,0))
            message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(message_text, message_rect)
            restart_font = ui_font.render("Press Q to Quit", True, WHITE)
            restart_rect = restart_font.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            screen.blit(restart_font, restart_rect)
            if keys[pygame.K_q]: running = False # Check quit key only when game over

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

# --- Start Game ---
if __name__ == '__main__':
    game()