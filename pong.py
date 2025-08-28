import math
import sys
import random
import pygame

# --------- Config ---------
WIDTH, HEIGHT = 900, 600
PADDLE_W, PADDLE_H = 12, 100
BALL_SIZE = 14
PADDLE_SPEED = 380  # pixels per second
BALL_SPEED = 320    # starting speed
BALL_SPEED_GAIN = 18  # speed added after each paddle hit
WIN_SCORE = 10
FONT_NAME = "freesansbold.ttf"  # bundled with pygame
BG_COLOR = (16, 18, 24)
FG_COLOR = (230, 230, 230)
NET_COLOR = (90, 90, 110)

# --------- Helpers ---------
def draw_center_net(surface):
    dash_h = 16
    gap = 12
    x = WIDTH // 2 - 2
    for y in range(0, HEIGHT, dash_h + gap):
        pygame.draw.rect(surface, NET_COLOR, (x, y, 4, dash_h))

def reset_ball(ball_rect, direction=None):
    ball_rect.center = (WIDTH // 2, HEIGHT // 2)
    angle = random.uniform(-0.8, 0.8)  # shallow-ish angles
    if direction is None:
        direction = random.choice([-1, 1])
    vx = direction * BALL_SPEED
    vy = BALL_SPEED * random.choice([-1, 1]) * abs(math.sin(angle))  # <-- fixed here
    return pygame.Vector2(vx, vy)

def clamp_paddle(rect):
    if rect.top < 0:
        rect.top = 0
    if rect.bottom > HEIGHT:
        rect.bottom = HEIGHT

def render_text(surface, text, size, color, center):
    font = pygame.font.Font(FONT_NAME, size)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=center)
    surface.blit(surf, rect)

def try_load_beeps():
    """Load simple generated beep sounds if mixer is available; otherwise return stubs."""
    try:
        pygame.mixer.init()
        # Generate quick tones
        def tone(freq=440, ms=60, volume=0.25):
            # Create a simple sine wave
            sample_rate = 44100
            n_samples = int(sample_rate * ms / 1000)
            buf = (pygame.sndarray.make_sound(
                (volume * 32767 *
                 (pygame.numpy.sin(2.0 * pygame.numpy.pi * pygame.numpy.arange(n_samples) * freq / sample_rate))
                ).astype(pygame.numpy.int16)
            ))
            return buf
        hit = tone(620, 70, 0.22)
        wall = tone(440, 60, 0.18)
        score = tone(300, 120, 0.28)
        return hit, wall, score
    except Exception:
        class Silent:
            def play(self): pass
        s = Silent()
        return s, s, s

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong (2P)")
    clock = pygame.time.Clock()

    # Paddles and ball
    left = pygame.Rect(40, HEIGHT//2 - PADDLE_H//2, PADDLE_W, PADDLE_H)
    right = pygame.Rect(WIDTH - 40 - PADDLE_W, HEIGHT//2 - PADDLE_H//2, PADDLE_W, PADDLE_H)
    ball = pygame.Rect(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)

    ball_vel = reset_ball(ball)

    left_score = 0
    right_score = 0
    paused = False
    game_over = False

    # Sounds (optional)
    hit_snd, wall_snd, score_snd = try_load_beeps()

    # Input state for smoother movement
    move_left = 0
    move_right = 0

    while True:
        dt = clock.tick(120) / 1000.0  # seconds
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_p and not game_over:
                    paused = not paused
                if event.key == pygame.K_r:
                    # reset everything
                    left_score = right_score = 0
                    left.centery = right.centery = HEIGHT//2
                    ball_vel = reset_ball(ball)
                    paused = False
                    game_over = False
                # movement
                if event.key == pygame.K_w:   move_left = -1
                if event.key == pygame.K_s:   move_left =  1
                if event.key == pygame.K_UP:  move_right = -1
                if event.key == pygame.K_DOWN:move_right =  1
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_w, pygame.K_s):
                    # recompute based on current keys (to handle overlaps)
                    keys = pygame.key.get_pressed()
                    move_left = (-1 if keys[pygame.K_w] else 0) + (1 if keys[pygame.K_s] else 0)
                    move_left = max(-1, min(1, move_left))
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    keys = pygame.key.get_pressed()
                    move_right = (-1 if keys[pygame.K_UP] else 0) + (1 if keys[pygame.K_DOWN] else 0)
                    move_right = max(-1, min(1, move_right))

        if not paused and not game_over:
            # Update paddles
            left.y += int(move_left * PADDLE_SPEED * dt)
            right.y += int(move_right * PADDLE_SPEED * dt)
            clamp_paddle(left)
            clamp_paddle(right)

            # Move ball
            ball.x += int(ball_vel.x * dt)
            ball.y += int(ball_vel.y * dt)

            # Wall collisions (top/bottom)
            if ball.top <= 0:
                ball.top = 0
                ball_vel.y *= -1
                wall_snd.play()
            if ball.bottom >= HEIGHT:
                ball.bottom = HEIGHT
                ball_vel.y *= -1
                wall_snd.play()

            # Paddle collisions
            if ball.colliderect(left) and ball_vel.x < 0:
                # calculate deflection based on hit position
                offset = (ball.centery - left.centery) / (PADDLE_H / 2)
                angle_scale = 260  # vertical push
                ball.left = left.right
                ball_vel.x = abs(ball_vel.x) + BALL_SPEED_GAIN
                ball_vel.y = max(-520, min(520, ball_vel.y + offset * angle_scale))
                hit_snd.play()

            if ball.colliderect(right) and ball_vel.x > 0:
                offset = (ball.centery - right.centery) / (PADDLE_H / 2)
                angle_scale = 260
                ball.right = right.left
                ball_vel.x = -abs(ball_vel.x) - BALL_SPEED_GAIN
                ball_vel.y = max(-520, min(520, ball_vel.y + offset * angle_scale))
                hit_snd.play()

            # Scoring
            if ball.right < 0:
                right_score += 1
                score_snd.play()
                ball_vel = reset_ball(ball, direction=1)
            elif ball.left > WIDTH:
                left_score += 1
                score_snd.play()
                ball_vel = reset_ball(ball, direction=-1)

            # Win condition
            if left_score >= WIN_SCORE or right_score >= WIN_SCORE:
                game_over = True
                paused = False

        # --------- Draw ---------
        screen.fill(BG_COLOR)
        draw_center_net(screen)

        pygame.draw.rect(screen, FG_COLOR, left, border_radius=4)
        pygame.draw.rect(screen, FG_COLOR, right, border_radius=4)
        pygame.draw.ellipse(screen, FG_COLOR, ball)

        # Scores
        render_text(screen, str(left_score), 48, FG_COLOR, (WIDTH * 0.25, 50))
        render_text(screen, str(right_score), 48, FG_COLOR, (WIDTH * 0.75, 50))

        if paused:
            render_text(screen, "Paused - Press P to Resume", 28, FG_COLOR, (WIDTH//2, HEIGHT//2 - 12))
            render_text(screen, "R: Restart  Esc/Q: Quit", 22, NET_COLOR, (WIDTH//2, HEIGHT//2 + 24))

        if game_over:
            winner = "Left" if left_score > right_score else "Right"
            render_text(screen, f"{winner} Player Wins!", 44, FG_COLOR, (WIDTH//2, HEIGHT//2 - 10))
            render_text(screen, "Press R to Restart  |  Esc/Q to Quit", 24, NET_COLOR, (WIDTH//2, HEIGHT//2 + 30))

        # Small help hint
        render_text(screen, "W/S  vs  ↑/↓   |   P: Pause   R: Restart", 18, NET_COLOR, (WIDTH//2, HEIGHT - 20))

        pygame.display.flip()

if __name__ == "__main__":
    main()
