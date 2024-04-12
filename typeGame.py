import pygame
import requests
import sys
import random

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Initialize Pygame
pygame.init()

# Set up the screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Typing Speed Game")

# Fonts
font = pygame.font.SysFont(None, 36)

# Clock
clock = pygame.time.Clock()

# Function to fetch random words from Wordnik API
def fetch_random_words(api_key, count):
    url = f"https://api.wordnik.com/v4/words.json/randomWords?hasDictionaryDef=true&minCorpusCount=0&maxCorpusCount=-1&minDictionaryCount=1&maxDictionaryCount=-1&minLength=5&maxLength=10&limit={count}&api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        words = [word['word'] for word in response.json()]
        return words
    else:
        print("Failed to fetch words from API.")
        return []

# Function to generate a random word
def generate_word(api_key):
    words = fetch_random_words(api_key, 1)
    if words:
        return words[0]
    else:
        print("Failed to fetch word from API.")
        return "ERROR"

# Class for the falling words
class Word(pygame.sprite.Sprite):
    def __init__(self, api_key):
        super().__init__()
        self.word = generate_word(api_key)
        self.font = font
        self.color = random.choice([RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE])
        self.image = self.font.render(self.word, True, self.color)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = 0
        self.speed = 1  # Reduced speed

    def update(self):
        self.rect.y += self.speed

# Function to display text on screen
def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

# Main function
def main(api_key):
    all_sprites = pygame.sprite.Group()
    words = pygame.sprite.Group()
    word_delay = 1000  # milliseconds
    last_word_time = 0
    typed_text = ""
    score = 0

    input_box = pygame.Rect(10, HEIGHT - 40, WIDTH - 20, 30)
    color_inactive = GRAY
    color_active = BLACK
    color = color_inactive
    active = False

    running = True
    game_over = False

    while running:
        current_time = pygame.time.get_ticks()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicks on the input box
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        if typed_text:
                            for word in words:
                                if word.word == typed_text:
                                    words.remove(word)
                                    all_sprites.remove(word)
                                    typed_text = ""
                                    score += 1
                                    break
                    elif event.key == pygame.K_BACKSPACE:
                        typed_text = typed_text[:-1]
                    else:
                        typed_text += event.unicode

        if not game_over:
            # Generate a new word periodically with a delay
            if current_time - last_word_time > word_delay:
                word = Word(api_key)
                all_sprites.add(word)
                words.add(word)
                last_word_time = current_time

            # Update word positions
            all_sprites.update()

            # Check for collisions with the bottom of the screen
            for word in words:
                if word.rect.bottom >= HEIGHT:
                    game_over = True
                    break

            # Clear the screen
            screen.fill(WHITE)

            # Draw input box
            pygame.draw.rect(screen, color, input_box, 2)

            # Render typed text
            text_surface = font.render(typed_text, True, BLACK)
            screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))

            # Draw all sprites
            all_sprites.draw(screen)

            # Draw score
            draw_text(screen, f"Score: {score}", font, BLACK, WIDTH // 2, 10)

            # Update the display
            pygame.display.flip()

            # Cap the frame rate
            clock.tick(60)
        else:
            # Game over screen
            screen.fill(WHITE)
            draw_text(screen, "Game Over", font, BLACK, WIDTH // 2, HEIGHT // 2 - 50)
            draw_text(screen, f"Your Score: {score}", font, BLACK, WIDTH // 2, HEIGHT // 2)
            draw_text(screen, "Press Enter to play again", font, BLACK, WIDTH // 2, HEIGHT // 2 + 50)
            pygame.display.flip()

            # Reset the game when Enter is pressed
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        game_over = False
                        words.empty()
                        all_sprites.empty()
                        last_word_time = 0
                        typed_text = ""
                        score = 0

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    api_key = 'YOUR_WORDNIK_API_KEY_HERE'
    main(api_key)
