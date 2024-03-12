import pygame
import sys
import random
import math

pygame.init()
screen = pygame.display.set_mode((480, 360))
pygame.display.set_caption("Lai tau vu tru")

# Load and resize images
ship_img = pygame.image.load("resources/rocketship.png")
ship_img = pygame.transform.scale(ship_img, (64, 112))  # Resize to 64x112

pygame.display.set_icon(ship_img)

bg_image = pygame.image.load("resources/bg_galaxy.png")
bg_image = pygame.transform.scale(bg_image, (480, 360))  # Resize to 480x360

ship_x = 220
ship_y = 280

ship_sound = pygame.mixer.Sound("resources/explosion.wav")
countdown_sound = pygame.mixer.Sound("resources/count_down.wav")
meteor_img = pygame.image.load("resources/meteoroid.png")
meteor_img = pygame.transform.scale(meteor_img, (48, 48))  # Resize to 48x48

meteor_y_positions = []
meteor_x_positions = []
meteor_speeds = []
meteor_timers = []  # Timer for each meteoroid

meteor_spawn_timer = 0  # Timer to control meteoroid spawning
meteor_spawn_delay = 1500  # Delay between meteoroid spawns in milliseconds

x_change = 0
score = 0
meteoroids_per_wave = 1  # Number of meteoroids to spawn per wave, initially set to 1
max_meteoroids = 5  # Maximum number of meteoroids allowed on the screen at any time
wave_timer = 1  # Timer to control waves
wave_delay = 15000  # Delay between waves in milliseconds

score_text = pygame.font.SysFont("Arial", 24)
game_over_font = pygame.font.SysFont("Arial", 48)
clock = pygame.time.Clock()

def spawn_meteoroid():
    meteor_y_positions.append(0)
    meteor_x_positions.append(random.randint(0, 432 - meteor_img.get_width()))  # Adjusted to prevent meteoroid from going outside the screen width
    meteor_speeds.append(random.uniform(0.5, 2.0) * 1.25)
    meteor_timers.append(pygame.time.get_ticks())

def remove_meteoroid(index):
    meteor_y_positions.pop(index)
    meteor_x_positions.pop(index)
    meteor_speeds.pop(index)
    meteor_timers.pop(index)

def increase_difficulty():
    global meteoroids_per_wave
    meteoroids_per_wave += 1

def reset_game():
    global ship_x, ship_y, x_change, score, meteor_y_positions, meteor_x_positions, meteor_speeds, meteor_timers, meteoroids_per_wave, game_over
    ship_x = 220
    ship_y = 280
    x_change = 0
    score = 0
    meteor_y_positions.clear()
    meteor_x_positions.clear()
    meteor_speeds.clear()
    meteor_timers.clear()
    meteoroids_per_wave = 1
    game_over = False

countdown = 3  # 3-second countdown

while countdown > 0:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    countdown_sound.play()
    screen.blit(bg_image, (0, 0))
    countdown_text = score_text.render("Game starts in: " + str(countdown), True, (255, 255, 255))
    screen.blit(countdown_text, (150, 150))
    pygame.display.update()
    pygame.time.delay(1000)  # 1-second delay
    countdown -= 1
countdown_sound.stop()

meteor_speed = 2
game_over = False
max_score = 0  # Maximum score achieved

while True:
    countdown = 3
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                x_change = -5
            elif event.key == pygame.K_RIGHT:
                x_change = 5
            elif event.key == pygame.K_SPACE:
                if game_over:
                    reset_game()
                    while countdown > 0:
                        countdown_sound.play()
                        screen.blit(bg_image, (0, 0))
                        countdown_text = score_text.render("Game starts in: " + str(countdown), True, (255, 255, 255))
                        screen.blit(countdown_text, (150, 150))
                        pygame.display.update()
                        pygame.time.delay(1000)  # 1-second delay
                        countdown -= 1
                    countdown_sound.stop()

        if event.type == pygame.KEYUP:
            x_change = 0

    if not game_over:
        ship_x += x_change

        if ship_x < 0:
            ship_x = 0
        elif ship_x > 480 - ship_img.get_width():
            ship_x = 480 - ship_img.get_width()

        for i in range(len(meteor_y_positions)):
            meteor_y_positions[i] += int(meteor_speeds[i] * meteor_speed)

            distance = math.sqrt((ship_x - meteor_x_positions[i]) ** 2 + (ship_y - meteor_y_positions[i]) ** 2)
            if distance < 60:
                game_over = True
                ship_sound.play()
                break

            if meteor_y_positions[i] > 360:
                remove_meteoroid(i)  # Remove meteoroid that goes below the screen
                spawn_meteoroid()  # Spawn a new meteoroid after one disappears
                break

            # Remove meteoroid if it has been on the screen for more than 5 seconds
            if pygame.time.get_ticks() - meteor_timers[i] > 5000:
                remove_meteoroid(i)
                spawn_meteoroid()
                break

        for i in range(len(meteor_y_positions)):
            if meteor_y_positions[i] > ship_y and meteor_y_positions[i] < ship_y + ship_img.get_height():
                if meteor_x_positions[i] > ship_x and meteor_x_positions[i] < ship_x + ship_img.get_width():
                    game_over = True
                    ship_sound.play()
                    break

        if not game_over:
            score += 1
            game_over = False

        if score > max_score:
            max_score = score

        if score % 1200 == 0 and score > 0:
            increase_difficulty()

        meteor_spawn_timer += clock.get_rawtime()
        if meteor_spawn_timer >= meteor_spawn_delay:
            for _ in range(min(meteoroids_per_wave, max_meteoroids - len(meteor_y_positions))):
                spawn_meteoroid()
            meteor_spawn_timer = 1

        wave_timer += clock.get_rawtime()
        if wave_timer >= wave_delay:
            increase_difficulty()
            wave_timer = 1

    screen.blit(bg_image, (0, 0))
    if not game_over:
        screen.blit(ship_img, (ship_x, ship_y))
    for i in range(len(meteor_y_positions)):
        screen.blit(meteor_img, (meteor_x_positions[i], meteor_y_positions[i]))

    elapsed_time = pygame.time.get_ticks() // 1000
    time_text = score_text.render("Time: " + str(elapsed_time) + "s", True, (255, 255, 255))
    screen.blit(time_text, (10, 10))

    score_render = score_text.render("Score: " + str(score), True, (255, 255, 255))
    screen.blit(score_render, (10, 30))

    if game_over:
        game_over_text = game_over_font.render("Game Over", True, (255, 0, 0))
        screen.blit(game_over_text, (150, 100))  # Adjusted vertical position

        max_score_text = score_text.render("Max Score: " + str(max_score), True, (255, 255, 255))
        screen.blit(max_score_text, (150, 160))  # Adjusted vertical position

        play_again_text = score_text.render("Press SPACE to play again", True, (255, 255, 255))
        screen.blit(play_again_text, (100, 250))

    pygame.display.update()
    clock.tick(60)  # Set the frame rate to 60 FPS