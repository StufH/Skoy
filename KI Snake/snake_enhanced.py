import pygame
import random
import json
import math
import sys
from enum import Enum
from collections import deque

# --- Configuration Loading ---
class Settings:
    def __init__(self, filename="config.json"):
        try:
            with open(filename, 'r') as f:
                self.config = json.load(f)
            print(f"Loaded settings from {filename}")
        except FileNotFoundError:
            print(f"Error: {filename} not found. Using default settings.")
            self.config = self._get_default_settings()
        except json.JSONDecodeError:
            print(f"Error: Could not decode {filename}. Using default settings.")
            self.config = self._get_default_settings()

        # Assign settings to attributes for easier access
        for key, value in self.config.items():
            setattr(self, key, value)

        # Calculate grid dimensions based on screen size and grid size
        self.grid_width = self.screen_width // self.grid_size
        self.grid_height = self.screen_height // self.grid_size

    def _get_default_settings(self):
        # Define default settings here in case config file fails
        return {
          "screen_width": 800, "screen_height": 600, "grid_size": 20,
          "fps": 60, "initial_snake_speed": 10, "enable_trail": True,
          "trail_length": 15, "trail_fade_speed": 10,
          "enable_pulsing_background": True, "bg_pulse_speed": 0.5,
          "enable_particle_effects": True, "particle_count": 30,
          "particle_lifespan": 1.0, "particle_speed": 150,
          "enable_powerups": True, "powerup_duration": 5.0,
          "speed_boost_multiplier": 2.0, "slow_mo_multiplier": 0.5,
          "enable_evolving_snake": True, "enable_obstacles": True,
          "obstacle_count": 5, "enable_ai_opponent": True, "ai_speed": 9,
          "enable_screen_shake": True, "shake_intensity": 5, "shake_duration": 0.2
        }

    def get(self, key, default=None):
        return self.config.get(key, default)

# --- Enums ---
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class FoodType(Enum):
    NORMAL = 0
    SPEED_BOOST = 1
    SLOW_MO = 2
    # Add more types here: REVERSE_CONTROL, DOUBLE_VISION

# --- Colors ---
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_PURPLE = (128, 0, 128)
COLOR_ORANGE = (255, 165, 0)
COLOR_CYAN = (0, 255, 255)
COLOR_GREY = (128, 128, 128)

FOOD_COLORS = {
    FoodType.NORMAL: COLOR_GREEN,
    FoodType.SPEED_BOOST: COLOR_ORANGE,
    FoodType.SLOW_MO: COLOR_CYAN,
}

# --- Game Objects ---
class Snake:
    def __init__(self, settings, start_pos, color, is_ai=False):
        self.settings = settings
        self.grid_size = settings.grid_size
        self.body = deque([pygame.Vector2(start_pos)])
        self.direction = random.choice(list(Direction))
        self.new_direction = self.direction
        self.color = color
        self.base_color = color
        self.grow = False
        self.is_ai = is_ai
        self.alive = True
        self.move_timer = 0
        self.base_speed = settings.ai_speed if is_ai else settings.initial_snake_speed
        self.current_speed = self.base_speed

        # Power-up state
        self.powerup_type = None
        self.powerup_timer = 0.0

        # Trail
        self.trail_points = deque(maxlen=settings.trail_length if settings.enable_trail else 0)

    def update(self, dt, food_list, obstacles, other_snake_body=None):
        if not self.alive:
            return

        # Update power-up timer
        if self.powerup_timer > 0:
            self.powerup_timer -= dt
            if self.powerup_timer <= 0:
                self._deactivate_powerup()
        else:
            self.current_speed = self.base_speed # Reset speed if no powerup

        # Control movement speed
        self.move_timer += dt * self.current_speed
        if self.move_timer >= 1.0:
            self.move_timer -= 1.0
            self._move()
            self._check_collisions(obstacles, other_snake_body)
            if self.settings.enable_trail:
                 self._update_trail()


    def _move(self):
        # Update direction only if it's not opposite
        if (self.new_direction.value[0] != -self.direction.value[0] or \
            self.new_direction.value[1] != -self.direction.value[1]):
             self.direction = self.new_direction

        head = self.body[0]
        new_head = head + pygame.Vector2(self.direction.value)

        # Wrap around screen edges
        new_head.x %= self.settings.grid_width
        new_head.y %= self.settings.grid_height

        self.body.appendleft(new_head)

        if self.grow:
            self.grow = False
            if self.settings.enable_evolving_snake:
                self._evolve_visuals()
        else:
            self.body.pop()

    def _update_trail(self):
         if self.body:
             self.trail_points.appendleft({
                 'pos': self.body[-1].copy() * self.grid_size + pygame.Vector2(self.grid_size / 2),
                 'alpha': 200 # Start slightly transparent
             })


    def _check_collisions(self, obstacles, other_snake_body):
        head = self.body[0]

        # Self collision
        for segment in list(self.body)[1:]:
            if head == segment:
                self.alive = False
                return

        # Obstacle collision
        if self.settings.enable_obstacles:
            for obstacle in obstacles:
                 # Check if head grid position matches obstacle grid position
                 if head.x == obstacle.pos.x and head.y == obstacle.pos.y:
                    self.alive = False
                    return


        # Other snake collision
        if other_snake_body:
            for segment in other_snake_body:
                 if head == segment:
                    self.alive = False
                    return


    def change_direction(self, new_direction):
        # Prevent instant 180 degree turns if snake is longer than 1 segment
        if len(self.body) > 1:
             if (new_direction == Direction.UP and self.direction == Direction.DOWN) or \
                (new_direction == Direction.DOWN and self.direction == Direction.UP) or \
                (new_direction == Direction.LEFT and self.direction == Direction.RIGHT) or \
                (new_direction == Direction.RIGHT and self.direction == Direction.LEFT):
                 return # Ignore opposite direction change
        self.new_direction = new_direction


    def eat(self, food):
        self.grow = True
        if self.settings.enable_powerups and food.food_type != FoodType.NORMAL:
            self._activate_powerup(food.food_type)

    def _activate_powerup(self, food_type):
        self._deactivate_powerup() # Deactivate any existing powerup first
        self.powerup_type = food_type
        self.powerup_timer = self.settings.powerup_duration

        if food_type == FoodType.SPEED_BOOST:
            self.current_speed = self.base_speed * self.settings.speed_boost_multiplier
        elif food_type == FoodType.SLOW_MO:
             # Slow down self, potentially affect global game speed in Game class later
            self.current_speed = self.base_speed * self.settings.slow_mo_multiplier
            # TODO: Trigger visual distortion effects (blur, chromatic shift) in Game class

    def _deactivate_powerup(self):
        self.powerup_type = None
        self.powerup_timer = 0
        self.current_speed = self.base_speed
        # TODO: Stop visual distortion effects in Game class

    def _evolve_visuals(self):
        # Simple color evolution based on length
        length_factor = min(len(self.body) / 50.0, 1.0) # Max effect at length 50
        r = int(self.base_color[0] * (1 - length_factor) + COLOR_YELLOW[0] * length_factor)
        g = int(self.base_color[1] * (1 - length_factor) + COLOR_YELLOW[1] * length_factor)
        b = int(self.base_color[2] * (1 - length_factor) + COLOR_YELLOW[2] * length_factor)
        self.color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
        # TODO: Implement more complex biomechanical textures/shaders/layered sprites here

    def ai_control(self, food_list, obstacles, other_snake_body):
        if not self.alive or not food_list:
            return

        head = self.body[0]
        target_food = min(food_list, key=lambda f: head.distance_squared_to(f.pos))

        possible_moves = {} # Direction: next_pos
        for direction in Direction:
             # Prevent 180 turns immediately
            if len(self.body) > 1 and \
               (direction.value[0] == -self.direction.value[0] and direction.value[1] == -self.direction.value[1]):
                continue

            next_pos = head + pygame.Vector2(direction.value)
            next_pos.x %= self.settings.grid_width
            next_pos.y %= self.settings.grid_height

            # Check for immediate collisions
            safe = True
            # Self collision check
            if next_pos in list(self.body):
                 safe = False
            # Obstacle collision check
            if self.settings.enable_obstacles:
                 if any(next_pos == obs.pos for obs in obstacles):
                     safe = False
            # Other snake collision check
            if other_snake_body:
                 if next_pos in list(other_snake_body):
                     safe = False

            if safe:
                possible_moves[direction] = next_pos

        if not possible_moves:
            # No safe moves, maybe just continue straight? (might still collide)
            if self.direction in possible_moves: # Check if current direction is calculated as safe
                 self.new_direction = self.direction
            # AI might die here if trapped, needs better pathfinding like A*
            # For now, just pick a random valid direction if possible, otherwise keep going
            elif possible_moves:
                 self.new_direction = random.choice(list(possible_moves.keys()))
            return


        # Choose the move that gets closer to the target food
        best_move = min(possible_moves.keys(),
                        key=lambda d: possible_moves[d].distance_squared_to(target_food.pos))

        self.new_direction = best_move
        # TODO: Draw AI intent lines (line from head to target_food.pos)


    def draw(self, surface):
        # Draw Trail First (so it's behind the snake)
        if self.settings.enable_trail:
            for i, point_data in enumerate(reversed(self.trail_points)): # Draw oldest first
                alpha = point_data['alpha']
                if alpha > 0:
                     trail_surf = pygame.Surface((self.grid_size, self.grid_size), pygame.SRCALPHA)
                     # Fade color towards background or just fade alpha
                     trail_color = (*self.color[:3], int(alpha))
                     pygame.draw.rect(trail_surf, trail_color, (0, 0, self.grid_size, self.grid_size), border_radius=3)
                     surface.blit(trail_surf, (point_data['pos'].x - self.grid_size / 2, point_data['pos'].y - self.grid_size / 2))
                     # Decrease alpha for next frame
                     point_data['alpha'] -= self.settings.trail_fade_speed * (len(self.trail_points) / self.settings.trail_length) # Faster fade for older points


        # Draw Snake Body
        for segment in self.body:
            rect = pygame.Rect(segment.x * self.grid_size, segment.y * self.grid_size,
                               self.grid_size, self.grid_size)
            pygame.draw.rect(surface, self.color, rect)
            pygame.draw.rect(surface, COLOR_BLACK, rect, 1) # Outline

        # Draw head slightly different
        if self.body:
             head_rect = pygame.Rect(self.body[0].x * self.grid_size, self.body[0].y * self.grid_size,
                                     self.grid_size, self.grid_size)
             pygame.draw.rect(surface, tuple(min(255, c+30) for c in self.color[:3]), head_rect, border_radius=4) # Brighter head with rounded corners
             pygame.draw.rect(surface, COLOR_BLACK, head_rect, 1) # Outline


class Food:
    def __init__(self, settings, snake_bodies, obstacles):
        self.settings = settings
        self.grid_size = settings.grid_size
        self.spawn(snake_bodies, obstacles)

        # Animation state (e.g., simple pulse)
        self.pulse_timer = 0
        self.pulse_scale = 1.0

    def spawn(self, snake_bodies, obstacles):
        while True:
            x = random.randint(0, self.settings.grid_width - 1)
            y = random.randint(0, self.settings.grid_height - 1)
            self.pos = pygame.Vector2(x, y)

            # Check collisions with all snakes and obstacles
            occupied = False
            for body in snake_bodies:
                if self.pos in body:
                    occupied = True
                    break
            if occupied: continue

            if self.settings.enable_obstacles:
                 if any(self.pos == obs.pos for obs in obstacles):
                     occupied = True
                     continue
            if occupied: continue

            # If position is valid, break the loop
            break

        # Determine food type (add more weights/logic for rarer powerups)
        if self.settings.enable_powerups and random.random() < 0.3: # 30% chance for powerup
            self.food_type = random.choice([FoodType.SPEED_BOOST, FoodType.SLOW_MO])
        else:
            self.food_type = FoodType.NORMAL

        self.color = FOOD_COLORS.get(self.food_type, COLOR_GREEN)

    def update(self, dt):
         # Simple pulse animation
         self.pulse_timer += dt * 5 # Speed of pulse
         self.pulse_scale = 1.0 + math.sin(self.pulse_timer) * 0.1 # Pulse between 0.9 and 1.1 scale

    def draw(self, surface):
        scaled_size = self.grid_size * self.pulse_scale
        offset = (self.grid_size - scaled_size) / 2
        rect = pygame.Rect(self.pos.x * self.grid_size + offset,
                           self.pos.y * self.grid_size + offset,
                           scaled_size, scaled_size)
        pygame.draw.ellipse(surface, self.color, rect) # Draw as ellipse
        pygame.draw.ellipse(surface, tuple(max(0, c-30) for c in self.color[:3]), rect, 1) # Outline

class Particle:
    def __init__(self, pos, settings):
        self.settings = settings
        self.pos = pygame.Vector2(pos)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(settings.particle_speed * 0.5, settings.particle_speed * 1.5)
        self.vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
        self.lifespan = random.uniform(settings.particle_lifespan * 0.5, settings.particle_lifespan)
        self.age = 0
        self.color = random.choice([COLOR_YELLOW, COLOR_ORANGE, COLOR_WHITE, COLOR_GREEN])
        self.size = random.uniform(2, 5)

    def update(self, dt):
        self.pos += self.vel * dt
        self.age += dt
        # Optional: Add gravity or drag
        # self.vel.y += 50 * dt # Gravity example
        # self.vel *= 0.98 # Drag example

    def draw(self, surface):
        if self.is_alive():
            alpha = max(0, 255 * (1 - (self.age / self.lifespan)**2)) # Fade out quadratically
            particle_surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, (*self.color, int(alpha)), (self.size, self.size), self.size)
            surface.blit(particle_surf, self.pos - pygame.Vector2(self.size, self.size))


    def is_alive(self):
        return self.age < self.lifespan


class Obstacle:
    def __init__(self, settings, snake_bodies):
        self.settings = settings
        self.grid_size = settings.grid_size
        self.spawn(snake_bodies)
        self.color = COLOR_GREY
        self.animation_timer = random.uniform(0, math.pi * 2) # Start animation at random phase

    def spawn(self, snake_bodies):
         # Simple spawning, avoid snakes but might block paths - needs improvement
         while True:
            x = random.randint(1, self.settings.grid_width - 2) # Avoid edges slightly
            y = random.randint(1, self.settings.grid_height - 2)
            self.pos = pygame.Vector2(x, y)

            occupied = False
            for body in snake_bodies:
                 # Avoid spawning too close to initial snake positions
                 for segment in body:
                     if self.pos.distance_to(segment) < 3: # Don't spawn within 3 grid cells
                         occupied = True
                         break
                 if occupied: break
            if not occupied: break

    def update(self, dt):
        # Simple pulsing animation
        self.animation_timer += dt * 2
        pulse = (math.sin(self.animation_timer) + 1) / 2 # 0 to 1 range
        brightness = 100 + int(pulse * 55) # Pulse between grey 100 and 155
        self.color = (brightness, brightness, brightness)
        # TODO: Add rotation or other animations

    def draw(self, surface):
        rect = pygame.Rect(self.pos.x * self.grid_size, self.pos.y * self.grid_size,
                           self.grid_size, self.grid_size)
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, COLOR_BLACK, rect, 2) # Thicker outline

# --- Camera ---
class Camera:
    def __init__(self, settings):
        self.settings = settings
        self.offset = pygame.Vector2(0, 0)
        self.shake_timer = 0.0
        self.shake_intensity = settings.shake_intensity

    def update(self, dt):
        if self.shake_timer > 0:
            self.shake_timer -= dt
            if self.shake_timer <= 0:
                self.offset = pygame.Vector2(0, 0)
            else:
                self.offset.x = random.uniform(-self.shake_intensity, self.shake_intensity)
                self.offset.y = random.uniform(-self.shake_intensity, self.shake_intensity)
        else:
             self.offset = pygame.Vector2(0, 0)


    def apply_offset(self, pos):
        # Simple offset for shake, no zoom/pan yet
        return pos + self.offset

    def start_shake(self):
        if self.settings.enable_screen_shake:
             self.shake_timer = self.settings.shake_duration

# --- Main Game Class ---
class Game:
    def __init__(self):
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Enhanced Snake")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.running = True
        self.game_over_flag = False

        self.camera = Camera(self.settings)
        self.particles = []

        self.player_snake = None
        self.ai_snake = None
        self.food_list = []
        self.obstacles = []

        self.background_color_1 = pygame.Color(30, 0, 30)
        self.background_color_2 = pygame.Color(0, 30, 30)
        self.bg_pulse_value = 0.0

        self.reset_game()

    def reset_game(self):
        self.game_over_flag = False
        self.particles.clear()
        self.food_list.clear()
        self.obstacles.clear()

        # Initialize Player Snake
        player_start_pos = (self.settings.grid_width // 4, self.settings.grid_height // 2)
        self.player_snake = Snake(self.settings, player_start_pos, COLOR_BLUE)

        snake_bodies = [self.player_snake.body]

        # Initialize AI Snake
        if self.settings.enable_ai_opponent:
            ai_start_pos = (self.settings.grid_width * 3 // 4, self.settings.grid_height // 2)
            self.ai_snake = Snake(self.settings, ai_start_pos, COLOR_PURPLE, is_ai=True)
            snake_bodies.append(self.ai_snake.body)
        else:
            self.ai_snake = None

        # Initialize Obstacles (pass initial snake positions)
        if self.settings.enable_obstacles:
             initial_bodies = [s.body for s in [self.player_snake, self.ai_snake] if s]
             self.obstacles = [Obstacle(self.settings, initial_bodies) for _ in range(self.settings.obstacle_count)]

        # Initial food spawn (pass all relevant bodies)
        self._spawn_food()


    def _spawn_food(self):
         snake_bodies = [self.player_snake.body]
         if self.ai_snake:
             snake_bodies.append(self.ai_snake.body)
         # Only spawn one food item for now
         self.food_list = [Food(self.settings, snake_bodies, self.obstacles)]


    def run(self):
        while self.running:
            dt = self.clock.tick(self.settings.fps) / 1000.0 # Delta time in seconds

            self._handle_input()
            if not self.game_over_flag:
                self._update(dt)
            self._render(dt)

        pygame.quit()
        sys.exit()

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if self.game_over_flag:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        self.running = False
                else:
                    if event.key == pygame.K_UP:
                        self.player_snake.change_direction(Direction.UP)
                    elif event.key == pygame.K_DOWN:
                        self.player_snake.change_direction(Direction.DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.player_snake.change_direction(Direction.LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.player_snake.change_direction(Direction.RIGHT)
                    # Debug keys (optional)
                    # elif event.key == pygame.K_SPACE: # Trigger shake
                    #      self.camera.start_shake()


    def _update(self, dt):
        other_snake_body_for_player = self.ai_snake.body if self.ai_snake else None
        other_snake_body_for_ai = self.player_snake.body if self.player_snake else None

        # Update Player Snake
        self.player_snake.update(dt, self.food_list, self.obstacles, other_snake_body_for_player)

        # Update AI Snake
        if self.ai_snake:
            # Pass food_list, obstacles, and player snake body to AI control
            self.ai_snake.ai_control(self.food_list, self.obstacles, self.player_snake.body)
            self.ai_snake.update(dt, self.food_list, self.obstacles, other_snake_body_for_ai)


        # Check food collision
        player_head = self.player_snake.body[0]
        ai_head = self.ai_snake.body[0] if self.ai_snake else None

        collided_food = None
        for food in self.food_list:
            food.update(dt) # Update food animation
            if player_head == food.pos:
                self.player_snake.eat(food)
                collided_food = food
                if self.settings.enable_particle_effects:
                     self._create_particles(food.pos * self.settings.grid_size + pygame.Vector2(self.settings.grid_size/2))

            elif self.ai_snake and ai_head == food.pos:
                self.ai_snake.eat(food)
                collided_food = food
                if self.settings.enable_particle_effects:
                    self._create_particles(food.pos * self.settings.grid_size + pygame.Vector2(self.settings.grid_size/2))

        if collided_food:
            self.food_list.remove(collided_food)
            self._spawn_food()


        # Update Particles
        if self.settings.enable_particle_effects:
            self.particles = [p for p in self.particles if p.is_alive()]
            for particle in self.particles:
                particle.update(dt)

        # Update Obstacles
        if self.settings.enable_obstacles:
            for obstacle in self.obstacles:
                 obstacle.update(dt)

        # Check Game Over
        if not self.player_snake.alive:
            self.game_over_flag = True
            self.camera.start_shake()
        if self.ai_snake and not self.ai_snake.alive:
             # Decide what happens when AI dies - maybe just remove it?
             # For now, let it trigger game over too if you want a 1v1 feel
             # Or just let the player continue: self.ai_snake = None
             # If AI death = game over:
             # self.game_over_flag = True
             # self.camera.start_shake()
             print("AI Snake Died")
             self.ai_snake = None # AI is just removed for now


        # Update Camera (for shake)
        self.camera.update(dt)

    def _create_particles(self, position):
        for _ in range(self.settings.particle_count):
            self.particles.append(Particle(position, self.settings))

    def _draw_pulsing_background(self, surface, dt):
        self.bg_pulse_value = (self.bg_pulse_value + dt * self.settings.bg_pulse_speed) % (2 * math.pi)
        # Interpolate between two colors using a sine wave
        mix = (math.sin(self.bg_pulse_value) + 1) / 2 # Range 0 to 1
        r = int(self.background_color_1.r * (1 - mix) + self.background_color_2.r * mix)
        g = int(self.background_color_1.g * (1 - mix) + self.background_color_2.g * mix)
        b = int(self.background_color_1.b * (1 - mix) + self.background_color_2.b * mix)
        surface.fill((r, g, b))
        # TODO: Implement more complex gradient rendering here

    def _render(self, dt):
        # Draw Background
        if self.settings.enable_pulsing_background:
            self._draw_pulsing_background(self.screen, dt)
        else:
            self.screen.fill(COLOR_BLACK)

        # Apply camera offset to drawing positions
        draw_offset = self.camera.offset

        # Create a temporary surface for drawing game elements if shaking
        # This prevents elements 'jittering' relative to each other during shake
        temp_surface = self.screen.copy() if self.camera.shake_timer > 0 else self.screen
        temp_surface.set_colorkey(COLOR_BLACK) # Assuming black background if not pulsing

        # Draw Obstacles
        if self.settings.enable_obstacles:
            for obstacle in self.obstacles:
                obstacle.draw(temp_surface)

        # Draw Food
        for food in self.food_list:
            food.draw(temp_surface)

        # Draw Snakes (Player and AI)
        self.player_snake.draw(temp_surface)
        if self.ai_snake:
            self.ai_snake.draw(temp_surface)

        # Draw Particles
        if self.settings.enable_particle_effects:
            for particle in self.particles:
                particle.draw(temp_surface) # Draw particles directly on screen or temp surface

        # Blit the temp surface with shake offset if needed
        if self.camera.shake_timer > 0:
             self.screen.blit(temp_surface, draw_offset)


        # Draw Score / UI
        score_text = f"Score: {len(self.player_snake.body) - 1}"
        score_surface = self.font.render(score_text, True, COLOR_WHITE)
        self.screen.blit(score_surface, (10, 10))

        if self.ai_snake:
             ai_score_text = f"AI Score: {len(self.ai_snake.body) - 1}"
             ai_score_surface = self.font.render(ai_score_text, True, COLOR_WHITE)
             ai_score_rect = ai_score_surface.get_rect(topright=(self.settings.screen_width - 10, 10))
             self.screen.blit(ai_score_surface, ai_score_rect)


        # Draw Game Over Message
        if self.game_over_flag:
            overlay = pygame.Surface((self.settings.screen_width, self.settings.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180)) # Semi-transparent black overlay
            self.screen.blit(overlay, (0,0))

            go_text = self.font.render("GAME OVER", True, COLOR_RED)
            go_rect = go_text.get_rect(center=(self.settings.screen_width / 2, self.settings.screen_height / 2 - 20))
            self.screen.blit(go_text, go_rect)

            restart_text = self.font.render("Press 'R' to Restart or 'Q' to Quit", True, COLOR_WHITE)
            restart_rect = restart_text.get_rect(center=(self.settings.screen_width / 2, self.settings.screen_height / 2 + 20))
            self.screen.blit(restart_text, restart_rect)


        pygame.display.flip()


if __name__ == '__main__':
    game = Game()
    game.run()