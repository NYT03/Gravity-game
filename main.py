import json
import sys

import pygame

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Gravity Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Load images
background = pygame.image.load("11250684_20067904.jpg").convert()
astronaut_img = pygame.image.load("astronaut-svgrepo-com.svg").convert_alpha()
coin_img = pygame.image.load("coin-svgrepo-com.svg").convert_alpha()

# Scale images
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
astronaut_img = pygame.transform.scale(astronaut_img, (50, 50))
coin_img = pygame.transform.scale(coin_img, (30, 30))

# Load level data
with open("level.json", "r") as f:
# Load level data
    level_data = json.load(f)

current_level = 0
total_levels = len(level_data)
print(level_data)

# Game variables
clock = pygame.time.Clock()
FPS = 60

class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        font = pygame.font.Font(None, 36)
        text = font.render(self.text, True, self.text_color)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Astronaut(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = astronaut_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.jumping = False
        self.move_speed = 3

    def jump(self, gravity):
        if not self.jumping:
            self.velocity_y = -10 * (1 / gravity)  # Decreased jump strength
            self.jumping = True

    def move_left(self):
        self.velocity_x = -self.move_speed

    def move_right(self):
        self.velocity_x = self.move_speed

    def stop(self):
        self.velocity_x = 0

    def update(self, gravity):
        self.velocity_y += gravity * 0.5
        self.rect.y += self.velocity_y
        self.rect.x += self.velocity_x

        # Keep astronaut within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.jumping = False
            self.velocity_y = 0

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = coin_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Hazard(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((255, 0, 0))  # Red color for hazards
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def start_menu():
    start_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 25, 200, 50, "Start Game", (0, 255, 0), BLACK)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.is_clicked(pygame.mouse.get_pos()):
                    return

        screen.blit(background, (0, 0))
        start_button.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

def show_level_complete(score):
    font = pygame.font.Font(None, 72)
    congrats_text = font.render("Congratulations!", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    next_level_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, 140, 50, "Next Level", (0, 255, 0), BLACK)
    repeat_button = Button(SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT // 2 + 50, 140, 50, "Repeat", (0, 200, 255), BLACK)

    animation_angle = 0
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if next_level_button.is_clicked(pygame.mouse.get_pos()):
                    return "next"
                elif repeat_button.is_clicked(pygame.mouse.get_pos()):
                    return "repeat"

        screen.blit(background, (0, 0))
        screen.blit(congrats_text, (SCREEN_WIDTH // 2 - congrats_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))

        # Simple rotation animation for the astronaut
        rotated_astronaut = pygame.transform.rotate(astronaut_img, animation_angle)
        screen.blit(rotated_astronaut, (SCREEN_WIDTH // 2 - rotated_astronaut.get_width() // 2, SCREEN_HEIGHT // 2 - 200))
        animation_angle += 2  # Adjust rotation speed

        next_level_button.draw(screen)
        repeat_button.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

def load_level(level_number):
    global current_level, level_data, total_levels
    current_level = level_number % total_levels
    current_level_data = level_data[current_level]

    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    hazards = pygame.sprite.Group()
    collectibles = pygame.sprite.Group()

    astronaut = Astronaut(50, SCREEN_HEIGHT - 100)
    all_sprites.add(astronaut)

    for platform in current_level_data["platforms"]:
        new_platform = Platform(platform["x"], platform["y"], platform["width"], platform["height"])
        all_sprites.add(new_platform)
        platforms.add(new_platform)

    for hazard in current_level_data["hazards"]:
        new_hazard = Hazard(hazard["x"], hazard["y"], hazard["width"], hazard["height"])
        all_sprites.add(new_hazard)
        hazards.add(new_hazard)

    for collectible in current_level_data["collectibles"]:
        new_collectible = Collectible(collectible["x"], collectible["y"])
        all_sprites.add(new_collectible)
        collectibles.add(new_collectible)

    return astronaut, all_sprites, platforms, hazards, collectibles

def main():
    global current_level, level_data, total_levels
    start_menu()  # Show start menu before starting the game

    astronaut, all_sprites, platforms, hazards, collectibles = load_level(current_level)

    score = 0
    time_left = 60  # You might want to add a time limit for each level in your JSON
    gravity = 0.5  # You might want to add gravity for each level in your JSON

    running = True
    paused = False
    level_complete = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    astronaut.jump(gravity)
                elif event.key == pygame.K_ESCAPE:
                    paused = not paused  # Toggle pause state
                elif event.key == pygame.K_LEFT:
                    astronaut.move_left()
                elif event.key == pygame.K_RIGHT:
                    astronaut.move_right()
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    astronaut.stop()

        if not paused and not level_complete:
            all_sprites.update(gravity)

            # Check for collisions with platforms
            if pygame.sprite.spritecollide(astronaut, platforms, False):
                astronaut.rect.bottom = pygame.sprite.spritecollide(astronaut, platforms, False)[0].rect.top
                astronaut.jumping = False
                astronaut.velocity_y = 0

            # Check for coin collection
            collected_coins = pygame.sprite.spritecollide(astronaut, collectibles, True)
            score += len(collected_coins)

            # Check for level completion
            if len(collected_coins) == len(collectibles):
                level_complete = True
                print(f"Level {current_level + 1} completed!")  # Debug print
                collectibles.empty()

            # Check for game over conditions
            if astronaut.rect.top > SCREEN_HEIGHT or time_left <= 0:
                game_over(score)
                running = False

            # Draw everything
            screen.blit(background, (0, 0))
            all_sprites.draw(screen)

            # Display score and time
            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Score: {score}", True, WHITE)
            time_text = font.render(f"Time: {int(time_left)}", True, WHITE)
            level_text = font.render(f"Level: {current_level + 1}", True, WHITE)  # Display current level
            screen.blit(score_text, (10, 10))
            screen.blit(time_text, (SCREEN_WIDTH - 120, 10))
            screen.blit(level_text, (SCREEN_WIDTH // 2 - 50, 10))

            pygame.display.flip()

            # Update time only if the level is not complete
            if not level_complete:
                time_left -= 1 / FPS
        elif paused:
            # Display pause message
            font = pygame.font.Font(None, 72)
            pause_text = font.render("PAUSED", True, WHITE)
            screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2))
            pygame.display.flip()
        
        if level_complete:
            result = show_level_complete(score)
            if result == "next":
                current_level = (current_level + 1) % total_levels
                print(f"Moving to level {current_level + 1}")  # Debug print
            astronaut, all_sprites, platforms, hazards, collectibles = load_level(current_level)
            score = 0
            time_left = 60  # Reset time for the new level
            level_complete = False

        clock.tick(FPS)

def game_over(score):
    font = pygame.font.Font(None, 72)
    game_over_text = font.render("Game Over", True, WHITE)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    restart_text = font.render("Press R to Restart", True, WHITE)
    quit_text = font.render("Press Q to Quit", True, WHITE)

    screen.blit(background, (0, 0))
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))
    screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 150))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()
                    waiting = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

if __name__ == "__main__":
    main()