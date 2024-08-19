import pygame
import random
import time
from datetime import datetime
from handopenclose import handgesture_setup, generate_results
from  game_json import *
import cv2

pygame.init()
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("HandGesture Controlled Flappy Bird")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

bg_img1 = pygame.image.load("images/background.png")
bg_img = pygame.transform.scale(bg_img1, (SCREEN_WIDTH, SCREEN_HEIGHT))

bird_img1 = pygame.image.load("images/bird.png")
bird_img = pygame.transform.scale(bird_img1, (40, 30)) 

bird_x = 50
bird_y = 300
bird_y_change = 0

gravity = 0.5
jump_strength = -7

pipe_width = 60
pipe_height = random.randint(150, 400)
pipe_gap = 200
pipe_x = SCREEN_WIDTH
pipe_y = random.randint(150, 400)
pipe_color = (255, 0, 0)
pipe_speed = 3

bg_x = 0
bg_speed = 1

score = 0

font = pygame.font.Font(None, 36)

game_over = False
cap, hands, mp_draw = handgesture_setup()
running = True
clock = pygame.time.Clock()

game_data = read_json()

current_date = datetime.now().strftime("%Y-%m-%d")
check_date_exist(game_data=game_data)
start_time = time.time()
# Created by Jonnalagadda Nihit
# Created on 19-August-2024

while running:
    elapsed_time = time.time() - start_time
    total_time_played_today = cal_total_time_played(game_data, start_time)

    if total_time_played_today >= 20 * 60: 
        screen.fill(WHITE)
        game_over_text = font.render("Maximum play time reached for the day", True, BLACK)
        screen.blit(game_over_text, (18, SCREEN_HEIGHT // 2 - 20)) 
        sub_text = font.render("Press escape button to exit", True, BLACK)
        screen.blit(sub_text, (70, SCREEN_HEIGHT // 2 + 20))  
        pygame.display.update()
        cap.release()
        pygame.time.wait(3000)
        running = False
        break
    
    hand_closed = generate_results(cap, hands)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  
                print("Escape key pressed! Exiting the game")
                running = False

    if hand_closed and not game_over:
        bird_y_change = jump_strength
    if hand_closed and game_over:
        bird_y = 300
        bird_y_change = 0
        pipe_x = SCREEN_WIDTH
        pipe_height = random.randint(150, 400)
        score = 0
        game_over = False

    if not game_over:
        bird_y_change += gravity
        bird_y += bird_y_change
        pipe_x -= pipe_speed
        bg_x -= bg_speed
        if bg_x <= -SCREEN_WIDTH:
            bg_x = 0
        if pipe_x < -pipe_width:
            pipe_x = SCREEN_WIDTH
            pipe_height = random.randint(150, 400)
            score += 1
        if (bird_y < 0 or bird_y > SCREEN_HEIGHT or
                (pipe_x < bird_x + 40 < pipe_x + pipe_width and
                 (bird_y < pipe_height or bird_y > pipe_height + pipe_gap))):
            game_over = True

    screen.blit(bg_img, (bg_x, 0))
    screen.blit(bg_img, (bg_x + SCREEN_WIDTH, 0))
    screen.blit(bird_img, (bird_x, bird_y))
    pygame.draw.rect(screen, pipe_color, (pipe_x, 0, pipe_width, pipe_height))
    pygame.draw.rect(screen, pipe_color, (pipe_x, pipe_height + pipe_gap, pipe_width, SCREEN_HEIGHT - pipe_height - pipe_gap))
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    if score % 10 == 0 and score!=0:
        pipe_speed += 0.05

    if game_over:
        game_over_text = font.render("Game Over! Close hand to restart", True, BLACK)
        screen.blit(game_over_text, (30, SCREEN_HEIGHT // 2))

    pygame.display.update()
    clock.tick(60)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
         running = False

save_game_data(game_data, score, elapsed_time)

cap.release()
pygame.quit()
