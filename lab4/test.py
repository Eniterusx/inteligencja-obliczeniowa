import pygame
import sys

# Initialize pygame
pygame.init()

# Set up the screen
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Move the Box")

# Set up colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Set up the box
box_size = 50
box_x = (screen_width - box_size) // 2
box_y = (screen_height - box_size) // 2

# Set up the clock
clock = pygame.time.Clock()

# Main game loop
running = True
while running:
    screen.fill(WHITE)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Check for pressed keys
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        box_x -= 5
    if keys[pygame.K_RIGHT]:
        box_x += 5
    if keys[pygame.K_UP]:
        box_y -= 5
    if keys[pygame.K_DOWN]:
        box_y += 5

    # Draw the box
    pygame.draw.rect(screen, BLACK, (box_x, box_y, box_size, box_size))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit pygame
pygame.quit()
sys.exit()
