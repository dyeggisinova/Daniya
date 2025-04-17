import pygame
import psycopg2
import sys
import pickle
from datetime import datetime

# Подключение к базе
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Создание таблиц
cur.execute('''
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS user_scores (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    score INTEGER,
    level INTEGER,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    snake BYTEA,
    food BYTEA,
    direction BYTEA
);
''')
conn.commit()

# Ввод юзернейма
username = input("Enter your username: ")
cur.execute("SELECT id FROM users WHERE username = %s", (username,))
user = cur.fetchone()

if user:
    user_id = user[0]
    cur.execute("SELECT level, snake, food, direction, score FROM user_scores WHERE user_id = %s ORDER BY saved_at DESC LIMIT 1", (user_id,))
    row = cur.fetchone()
    if row:
        level = row[0]
        saved_snake = pickle.loads(row[1])
        food = pickle.loads(row[2])
        direction = pickle.loads(row[3])
        score = row[4]
        load_saved = input("Saved game found. Load it? (y/n): ").lower() == 'y'
    else:
        level, saved_snake, food, direction, score = 1, None, None, None, 0
        load_saved = False
else:
    cur.execute("INSERT INTO users (username) VALUES (%s) RETURNING id", (username,))
    user_id = cur.fetchone()[0]
    conn.commit()
    level, saved_snake, food, direction, score = 1, None, None, None, 0
    load_saved = False

# Настройки Pygame
pygame.init()
WIDTH, HEIGHT = 600, 400
GRID_SIZE = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Стартовые значения
snake = saved_snake if load_saved else [(100, 100)]
direction = direction if load_saved else (GRID_SIZE, 0)
food = food if load_saved else (300, 200)
score = score if load_saved else 0

# Уровни и скорость
level_speeds = {1: 5, 2: 10, 3: 15}
speed = level_speeds.get(level, 5)

paused = False
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP: direction = (0, -GRID_SIZE)
            elif event.key == pygame.K_DOWN: direction = (0, GRID_SIZE)
            elif event.key == pygame.K_LEFT: direction = (-GRID_SIZE, 0)
            elif event.key == pygame.K_RIGHT: direction = (GRID_SIZE, 0)
            elif event.key == pygame.K_p:
                paused = not paused
                if paused:
                    cur.execute("""
                        INSERT INTO user_scores (user_id, score, level, snake, food, direction)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        user_id,
                        score,
                        level,
                        psycopg2.Binary(pickle.dumps(snake)),
                        psycopg2.Binary(pickle.dumps(food)),
                        psycopg2.Binary(pickle.dumps(direction))
                    ))
                    conn.commit()

    if paused:
        continue

    new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

    if (new_head[0] < 0 or new_head[0] >= WIDTH or
        new_head[1] < 0 or new_head[1] >= HEIGHT or
        new_head in snake):
        running = False

    snake.insert(0, new_head)

    if new_head == food:
        score += 1
        level = 1 + score // 5
        speed = level_speeds.get(level, speed + 2)
        food = (GRID_SIZE * (score % (WIDTH//GRID_SIZE)), GRID_SIZE * (score % (HEIGHT//GRID_SIZE)))
    else:
        snake.pop()

    screen.fill((255, 255, 255))
    for s in snake:
        pygame.draw.rect(screen, (0, 255, 0), (s[0], s[1], GRID_SIZE, GRID_SIZE))
    pygame.draw.rect(screen, (255, 0, 0), (food[0], food[1], GRID_SIZE, GRID_SIZE))
    score_text = font.render(f"Score: {score} Level: {level}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))
    pygame.display.flip()
    clock.tick(speed)

cur.close()
conn.close()
pygame.quit()
sys.exit()