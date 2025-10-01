import pygame
import random
import time
import sys
from datetime import datetime
from handopenclose import handgesture_setup, generate_results
from db_operations import db
from patient_form import get_patient_info
import cv2

def show_text(surface, text, size, x, y, color=(0, 0, 0)):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

class GameState:
    def __init__(self):
        self.overlay_surface = None
        self.title = None
        self.score = None
        self.instruction1 = None
        self.instruction2 = None
        self.title_rect = None
        self.score_rect = None
        self.inst1_rect = None
        self.inst2_rect = None
        self.is_game_over = False
        self.score_value = 0

    def reset(self):
        self.overlay_surface = None
        self.title = None
        self.score = None
        self.instruction1 = None
        self.instruction2 = None
        self.title_rect = None
        self.score_rect = None
        self.inst1_rect = None
        self.inst2_rect = None
        self.is_game_over = False

def start_game(patient_name, patient_id):
    # Initialize Pygame
    pygame.init()
    SCREEN_WIDTH = 500
    SCREEN_HEIGHT = 600
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    hands = handgesture_setup()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(f"HandGesture Controlled Flappy Bird - {patient_name}")
    
    # Initialize game state
    running = True
    game_state = GameState()
    paused = False
    clock = pygame.time.Clock()
    
    # Game variables
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    
    # Get patient's high score from database
    current_high_score = 0
    try:
        stats = db.get_patient_stats(patient_id)
        if stats and 'high_score' in stats:
            current_high_score = stats['high_score']
    except Exception as e:
        print(f"Error fetching high score: {e}")
    
    # Bird dimensions
    bird_width = 40  # Slightly smaller bird for better proportions
    bird_height = 30
    
    # Load and scale images
    bg_img1 = pygame.image.load("images/background.png")
    bg_img = pygame.transform.scale(bg_img1, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    bird_img1 = pygame.image.load("images/bird.png")
    bird_img = pygame.transform.scale(bird_img1, (bird_width, bird_height))  # Use defined dimensions
    
    # Game objects
    bird_x = SCREEN_WIDTH // 4  # Position bird at 1/4 of screen width
    bird_y = SCREEN_HEIGHT // 2
    bird_y_change = 0
    
    # Game settings
    gravity = 0.5  # Reduced gravity for better control
    jump_strength = -8  # Adjusted jump strength
    
    # Pipes
    pipe_width = 60  # Slightly narrower pipes
    pipe_gap = 180  # Adjusted gap for the screen height
    pipe_x = SCREEN_WIDTH
    pipe_height = random.randint(150, SCREEN_HEIGHT - pipe_gap - 100)  # Keep pipes within screen bounds
    pipe_y = 0  # Starting y position of top pipe
    pipe_color = (60, 180, 75)  # Green color for pipes
    pipe_speed = 3  # Slightly slower for better playability
    pipe_passed = False
    pipe_spawn_x = SCREEN_WIDTH + 50  # Spawn pipes slightly off-screen
    
    # Background
    bg_x = 0
    bg_speed = 1  # Slower background movement
    
    # Score
    score = 0
    # Get patient's high score from database
    current_high_score = 0
    try:
        stats = db.get_patient_stats(patient_id)
        if stats and 'high_score' in stats:
            current_high_score = int(stats['high_score'])  # Ensure it's an integer
    except Exception as e:
        print(f"Error fetching high score: {e}")
    start_time = time.time()
    
    # Initialize hand tracking
    cap, hands, mp_draw = handgesture_setup()
    
    # Game font
    font = pygame.font.Font(None, 32)  # Slightly smaller font
    
    # Collision detection function
    def check_collision():
        # Check if bird hits the ground or ceiling
        if bird_y <= 0 or bird_y + bird_height >= SCREEN_HEIGHT:
            return True
            
        # Check if bird hits the pipes
        bird_rect = pygame.Rect(bird_x, bird_y, bird_width, bird_height)
        top_pipe_rect = pygame.Rect(pipe_x, 0, pipe_width, pipe_height)
        bottom_pipe_rect = pygame.Rect(pipe_x, pipe_height + pipe_gap, pipe_width, SCREEN_HEIGHT - pipe_height - pipe_gap)
        
        return bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect)
    
    # Main game loop
    while running:
        elapsed_time = time.time() - start_time
        
        # Check for maximum play time (20 minutes per day)
        stats = db.get_patient_stats(patient_id)
        total_play_time = float(stats.get('total_play_time', 0)) if stats else 0.0
        if total_play_time + elapsed_time >= 20 * 60:  # 20 minutes max per day
            screen.fill(WHITE)
            game_over_text = font.render("Maximum play time reached for the day", True, BLACK)
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT//2 - 20)) 
            sub_text = font.render("Press ESC to exit", True, BLACK)
            screen.blit(sub_text, (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 + 20))  
            pygame.display.update()
            
            # Wait for ESC key
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting = False
                        running = False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        waiting = False
                        running = False
            break
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  
                    running = False
                elif event.key == pygame.K_p:  # Pause game
                    paused = not paused
                elif event.key == pygame.K_SPACE and game_state.is_game_over:  # Restart game
                    game_state.reset()
                    bird_y = SCREEN_HEIGHT // 2
                    bird_y_change = 0
                    pipe_x = SCREEN_WIDTH
                    pipe_height = random.randint(150, SCREEN_HEIGHT - pipe_gap - 100)
                    score = 0
                    pipe_passed = False
                    start_time = time.time()
                    db.start_session(patient_id)
        
        if not game_state.is_game_over and not paused:
            # Get hand gesture input
            hand_closed = generate_results(cap, hands)
            
            # Update game state
            if hand_closed:
                bird_y_change = jump_strength
            
            bird_y_change += gravity
            bird_y += bird_y_change
            
            # Update pipes
            pipe_x -= pipe_speed
            
            # Check for collision
            if check_collision():
                game_state.is_game_over = True
                game_state.score_value = score
                db.end_session(patient_id, score)
            
            # Check if pipe is passed
            if pipe_x < bird_x - pipe_width and not pipe_passed:
                score += 1
                if score > current_high_score:
                    current_high_score = score
                pipe_passed = True
            
            # Generate new pipe when current one goes off screen
            if pipe_x < -pipe_width:
                pipe_x = SCREEN_WIDTH
                pipe_height = random.randint(150, SCREEN_HEIGHT - pipe_gap - 100)
                pipe_passed = False
        
        # Draw everything
        # Draw background
        screen.blit(bg_img, (bg_x, 0))
        screen.blit(bg_img, (bg_x + SCREEN_WIDTH, 0))
        bg_x -= bg_speed
        if bg_x <= -SCREEN_WIDTH:
            bg_x = 0
            
        # Draw pipes
        if not game_state.is_game_over:
            # Top pipe
            pygame.draw.rect(screen, pipe_color, (pipe_x, 0, pipe_width, pipe_height))
            # Bottom pipe
            pygame.draw.rect(screen, pipe_color, 
                           (pipe_x, pipe_height + pipe_gap, 
                            pipe_width, SCREEN_HEIGHT - pipe_height - pipe_gap))
        
        # Draw bird
        screen.blit(bird_img, (bird_x, bird_y))
        
        # Draw score
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (20, 20))
        
        # Draw high score
        high_score_text = font.render(f"High Score: {current_high_score}", True, BLACK)
        high_score_rect = high_score_text.get_rect(topleft=(10, 60))
        screen.blit(high_score_text, high_score_rect)
        
        # Draw play time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        time_surface = font.render(f"Time: {minutes:02d}:{seconds:02d}", True, BLACK)
        time_rect = time_surface.get_rect(topleft=(10, 90))
        screen.blit(time_surface, time_rect)
        
        # Pause message
        if paused:
            pause_surface = font.render("PAUSED - Press P to continue", True, BLACK)
            pause_rect = pause_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            pygame.draw.rect(screen, (240, 240, 240), pause_rect.inflate(20, 10))
            screen.blit(pause_surface, pause_rect)
        
        # Game over screen
        if game_state.is_game_over:
            # Create a surface for the game over screen if it doesn't exist
            if game_state.overlay_surface is None:
                # Create overlay surface
                game_state.overlay_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                game_state.overlay_surface.fill((0, 0, 0, 180))
                
                # Create text surfaces once
                game_state.title = pygame.font.SysFont('Arial', 72, bold=True).render("Game Over!", True, (255, 255, 255))
                game_state.score = pygame.font.SysFont('Arial', 48).render(f"Final Score: {score}", True, (255, 255, 255))
                game_state.instruction1 = pygame.font.SysFont('Arial', 36).render("Press SPACE to play again", True, (200, 200, 200))
                game_state.instruction2 = pygame.font.SysFont('Arial', 36).render("Press ESC to exit", True, (200, 200, 200))
                
                # Get rects for centering
                game_state.title_rect = game_state.title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60))
                game_state.score_rect = game_state.score.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
                game_state.inst1_rect = game_state.instruction1.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
                game_state.inst2_rect = game_state.instruction2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 150))
            
            # Draw the overlay and text
            screen.blit(game_state.overlay_surface, (0, 0))
            screen.blit(game_state.title, game_state.title_rect)
            screen.blit(game_state.score, game_state.score_rect)
            screen.blit(game_state.instruction1, game_state.inst1_rect)
            screen.blit(game_state.instruction2, game_state.inst2_rect)
            
            # Check for restart or exit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        # Reset game state
                        game_state.reset()
                        bird_y = SCREEN_HEIGHT // 2
                        bird_y_change = 0
                        pipe_x = SCREEN_WIDTH
                        pipe_height = random.randint(200, 500)
                        score = 0
                        pipe_passed = False
                        start_time = time.time()
                        db.start_session(patient_id)  # Start new session
        
        pygame.display.update()
        clock.tick(60)
    
    # Clean up
    cap.release()
    pygame.quit()

def main():
    # Start with Tkinter form
    get_patient_info(start_game)

if __name__ == "__main__":
    try:
        main()
    finally:
        # Clean up resources when the game exits
        if 'cap' in locals() and cap.isOpened():
            cap.release()
        db.close()
        pygame.quit()
        sys.exit()
