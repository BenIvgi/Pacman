import datetime
import random

import pygame
import socket
import struct
import zlib
import map
from threading import Thread
import secret

# Initialize Pygame
pygame.init()

# Server settings
SERVER_IP = '127.0.0.1'  # Replace with your server IP
SERVER_PORT = 5000

# Game settings
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 750

# Map settings
CUBE_SIZE = 50
POINT_SIZE = 15

# Load IMAGES for player1 and g.player2
IMAGES = {'PACMAN': pygame.image.load('pacman.png'),
          'INKY': pygame.image.load('inky.png'),
          'PINKY': pygame.image.load('pinky.png'),
          'BLINKY': pygame.image.load('blinky.png'),
          'CLYDE': pygame.image.load('clyde.png'),
          'RISKY': pygame.image.load('blue_ghost.png'),
          'DEAD': pygame.image.load('dead_ghost.png'),
          }

# Define map elements
EMPTY = 0
WALL = 1
POINT = 2
BOOST = 3
DOOR = 4


# Content of each cube on the map
class Map:
    def __init__(self):
        self.mat = map.map1
        self.name = map.map1_name
        self.height = len(self.mat)
        self.width = len(self.mat[0])

    def update(self):
        # Update the map content
        for y in range(self.height):
            for x in range(self.width):
                if self.mat[y][x] == WALL:
                    pygame.draw.rect(screen, (0, 0, 255), (x * CUBE_SIZE, y * CUBE_SIZE, CUBE_SIZE, CUBE_SIZE))
                elif self.mat[y][x] == POINT:
                    pygame.draw.circle(screen, (255, 255, 255),
                                       (x * CUBE_SIZE + CUBE_SIZE // 2, y * CUBE_SIZE + CUBE_SIZE // 2),
                                       POINT_SIZE // 2)
                elif self.mat[y][x] == BOOST:
                    pygame.draw.circle(screen, (255, 255, 255),
                                       (x * CUBE_SIZE + CUBE_SIZE // 2, y * CUBE_SIZE + CUBE_SIZE // 2),
                                       POINT_SIZE * 1.5 // 2)
                elif self.mat[y][x] == DOOR:
                    pygame.draw.rect(screen, (255, 255, 255),
                                     (x * CUBE_SIZE, (y + 0.4) * CUBE_SIZE, CUBE_SIZE, CUBE_SIZE * 0.2))


# Pacman class
class Pacman:
    def __init__(self, x, y, img):
        self.color = (255, 255, 0)
        self.boost = False
        self.lives = 3
        self.x = x
        self.y = y
        self.velocity = [0, 0]
        self.speed = 4
        self.img = img
        self.points = 0
        self.boost_clock = 0

    def update(self, direction):
        if direction == 'UP':
            self.velocity = [0, -self.speed]
            self.img = pygame.transform.rotate(IMAGES['PACMAN'], 90)
        elif direction == 'DOWN':
            self.velocity = [0, self.speed]
            self.img = pygame.transform.rotate(IMAGES['PACMAN'], -90)
        elif direction == 'LEFT':
            self.velocity = [-self.speed, 0]
            self.img = pygame.transform.rotate(IMAGES['PACMAN'], 180)
        elif direction == 'RIGHT':
            self.velocity = [self.speed, 0]
            self.img = pygame.transform.rotate(IMAGES['PACMAN'], 0)

    def move(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]


# Ghost class
class Ghost:
    def __init__(self, x, y, color, type):
        self.color = color
        self.type = type
        self.x = x
        self.y = y
        self.speed = 5
        self.velocity = [0, -self.speed]
        self.img = IMAGES[type]

    def update(self, direction):
        if direction == 'UP':
            self.velocity = [0, -self.speed]
        elif direction == 'DOWN':
            self.velocity = [0, self.speed]
        elif direction == 'LEFT':
            self.velocity = [-self.speed, 0]
        elif direction == 'RIGHT':
            self.velocity = [self.speed, 0]

    def move(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]


class Game:

    def __init__(self):
        self.player1 = Pacman(175, 275, IMAGES['PACMAN'])
        self.player2 = Ghost(490, 270, (255, 0, 0), 'CLYDE')
        self.npc1 = Ghost(530, 270, (255, 0, 0), 'INKY')
        self.npc2 = Ghost(490, 220, (255, 0, 0), 'BLINKY')
        self.npc3 = Ghost(530, 220, (255, 0, 0), 'PINKY')
        self.map = Map()

    def check_collisions(self):
        player1_rect = pygame.Rect(self.player1.x - 20, self.player1.y - 20, 40, 40)
        player2_rect = pygame.Rect(self.player2.x - 20, self.player2.y - 20, 40, 40)
        npc1_rect = pygame.Rect(self.npc1.x - 20, self.npc1.y - 20, 40, 40)
        npc2_rect = pygame.Rect(self.npc2.x - 20, self.npc2.y - 20, 40, 40)
        npc3_rect = pygame.Rect(self.npc3.x - 20, self.npc3.y - 20, 40, 40)

        clear = True

        for y in range(self.map.height):
            for x in range(self.map.width):
                if self.map.mat[y][x] == WALL:
                    wall_rect = pygame.Rect(x * CUBE_SIZE, y * CUBE_SIZE, CUBE_SIZE, CUBE_SIZE)
                    for rect, entity in zip(
                            [player1_rect, player2_rect, npc1_rect, npc2_rect, npc3_rect],
                            [self.player1, self.player2, self.npc1, self.npc2, self.npc3]):
                        if rect.colliderect(wall_rect):
                            entity.x -= entity.velocity[0]
                            entity.y -= entity.velocity[1]
                            if entity in [self.npc1, self.npc2, self.npc3]:
                                if entity.velocity[0] == 0:
                                    new_dir = random.choice(['LEFT', 'RIGHT'])
                                else:
                                    new_dir = random.choice(['UP', 'DOWN'])
                                entity.update(new_dir)
                        else:
                            if entity in [self.npc1, self.npc2, self.npc3] and random.randint(1, 40000) == 4:
                                if entity.velocity[0] == 0:
                                    new_dir = random.choice(['LEFT', 'RIGHT'])
                                else:
                                    new_dir = random.choice(['UP', 'DOWN'])
                                entity.update(new_dir)

                elif self.map.mat[y][x] == POINT:
                    clear = False
                    point_rect = pygame.Rect(x * CUBE_SIZE + CUBE_SIZE // 2 - POINT_SIZE // 2,
                                             y * CUBE_SIZE + CUBE_SIZE // 2 - POINT_SIZE // 2, POINT_SIZE, POINT_SIZE)
                    if player1_rect.colliderect(point_rect):
                        self.map.mat[y][x] = 0  # Remove the point
                        self.player1.points += 1  # Increase the point counter

                elif self.map.mat[y][x] == BOOST:
                    boost_rect = pygame.Rect(x * CUBE_SIZE + CUBE_SIZE // 2 - POINT_SIZE // 2,
                                             y * CUBE_SIZE + CUBE_SIZE // 2 - POINT_SIZE // 2, POINT_SIZE * 1.5,
                                             POINT_SIZE * 1.5)
                    if player1_rect.colliderect(boost_rect):
                        self.map.mat[y][x] = 0  # Remove the point
                        self.player1.boost = True
                        for npc in [self.npc1, self.npc2, self.npc3, self.player2]:
                            if npc.img != IMAGES['DEAD']:
                                npc.img = IMAGES['RISKY']
                        self.player1.boost_clock = 0

                elif self.map.mat[y][x] == DOOR:
                    door_rect = pygame.Rect(x * CUBE_SIZE, (y + 0.4) * CUBE_SIZE, CUBE_SIZE, CUBE_SIZE * 0.2)
                    for rect, entity in zip(
                            [player1_rect, player2_rect, npc1_rect, npc2_rect, npc3_rect],
                            [self.player1, self.player2, self.npc1, self.npc2, self.npc3]):
                        if rect.colliderect(door_rect):
                            if entity is self.player1:
                                entity.x -= entity.velocity[0]
                                entity.y -= entity.velocity[1]
                            elif entity.img == IMAGES['DEAD']:
                                entity.update('DOWN')
                            elif entity.y < door_rect.y:
                                entity.update('UP')

            # Check for ghost - pacman collide

            for ghost, rect in zip([self.npc1, self.npc2, self.npc3, self.player2],
                                   [npc1_rect, npc2_rect, npc3_rect, player2_rect]):
                if player1_rect.colliderect(rect):
                    if self.player1.boost is False:
                        self.player1.x = 200
                        self.player1.y = 300
                        self.player2.x = 490
                        self.player2.y = 270

                        self.npc1.x = 530
                        self.npc1.y = 270
                        self.npc1.velocity = [0, -self.npc1.speed]
                        self.npc2.x = 490
                        self.npc2.y = 220
                        self.npc2.velocity = [0, -self.npc2.speed]
                        self.npc3.x = 530
                        self.npc3.y = 220
                        self.npc3.velocity = [0, -self.npc3.speed]

                        self.player1.lives -= 1

                        if self.player1.lives == 0:
                            game_over_display = f"GAME OVER! GHOSTS WON!"
                            game_over_surface = font.render(game_over_display, True, text_color, (255, 255, 255))
                            screen.blit(game_over_surface,
                                        ((SCREEN_WIDTH - game_over_surface.get_width()) // 2, SCREEN_HEIGHT // 2))
                            return False, False
                        else:
                            pygame.time.wait(1000)

                    else:
                        ghost.x = 530
                        ghost.y = 220
                        ghost.speed = 3
                        ghost.img = IMAGES['DEAD']
                        self.player1.points += 100

                    player1_rect = pygame.Rect(self.player1.x - 20, self.player1.y - 20, 40, 40)
                    player2_rect = pygame.Rect(self.player2.x - 20, self.player2.y - 20, 40, 40)
                    npc1_rect = pygame.Rect(self.npc1.x - 20, self.npc1.y - 20, 40, 40)
                    npc2_rect = pygame.Rect(self.npc2.x - 20, self.npc2.y - 20, 40, 40)
                    npc3_rect = pygame.Rect(self.npc3.x - 20, self.npc3.y - 20, 40, 40)

        if clear:
            game_over_display = f"GAME OVER! PACMAN WON!"
            game_over_surface = font.render(game_over_display, True, text_color, (255, 255, 255))
            screen.blit(game_over_surface,
                        ((SCREEN_WIDTH - game_over_surface.get_width()) // 2, SCREEN_HEIGHT // 2))
            return False, True

        if self.player1.boost is True:
            self.player1.boost_clock += 1

        if self.player1.boost_clock > 500:
            self.player1.boost = False
            for ghost in [self.npc1, self.npc2, self.npc3, self.player2]:
                ghost.img = IMAGES[ghost.type]
                ghost.speed = 5
        return True, None


g = Game()

KEYS = open('KEYS.txt', 'r').read().split('\n')

# Set the display mode
screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))


# Function to handle client connection
def handle_client(client_socket, character):
    while True:
        try:
            # Receive player input from the client
            data = secret.decrypt(client_socket.recv(1024).decode().strip())
            if not data:
                # Handle client disconnection
                break

            # Update the character direction based on the received input
            character.update(data)
        except:
            # Handle client disconnection
            break

    # Close the client connection
    client_socket.close()


# Start the server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(2)
print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")

clients = []
threads = []
while len(clients) < 2:
    client_socket, client_address = server_socket.accept()
    print(f"Client connected: {client_address}")

    try:
        key = secret.decrypt(client_socket.recv(1024).decode().strip())
        while key not in KEYS:
            client_socket.send(secret.encrypt('False').encode())
            key = secret.decrypt(client_socket.recv(1024).decode().strip())
        client_socket.send(secret.encrypt('True').encode())
        KEYS.remove(key)
    except Exception as e:
        continue

    print(f'Client {client_address} used key: {key}.')

    clients.append(client_socket)

    # Assign character object to the client
    if len(clients) == 1:
        character = g.player1
    else:
        character = g.player2

    # Start a new thread to handle the client connection
    thread = Thread(target=handle_client, args=(client_socket, character))
    thread.start()
    threads.append(thread)

# Game loop
clock = pygame.time.Clock()
running = True

# Set the font and size
font = pygame.font.Font('game_font.ttf', 36)  # You can specify the font file and size here

# Set the text color
text_color = (0, 0, 0)  # RGB value for black

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill((0, 0, 0))

    g.map.update()

    # Update the character positions and check collision with walls
    g.player1.move()
    g.player2.move()
    g.npc1.move()
    g.npc2.move()
    g.npc3.move()

    running, won = g.check_collisions()

    # Draw the characters on the screen
    screen.blit(g.player1.img,
                (g.player1.x - g.player1.img.get_width() // 2, g.player1.y - g.player1.img.get_height() // 2))
    screen.blit(g.player2.img,
                (g.player2.x - g.player2.img.get_width() // 2, g.player2.y - g.player2.img.get_height() // 2))

    screen.blit(g.npc1.img, (g.npc1.x - g.npc1.img.get_width() // 2, g.npc1.y - g.npc1.img.get_height() // 2))
    screen.blit(g.npc2.img, (g.npc2.x - g.npc2.img.get_width() // 2, g.npc2.y - g.npc2.img.get_height() // 2))
    screen.blit(g.npc3.img, (g.npc3.x - g.npc3.img.get_width() // 2, g.npc3.y - g.npc3.img.get_height() // 2))

    # Set the text content
    point_display = f"score: {g.player1.points}"

    # Render the text as a Pygame surface
    point_surface = font.render(point_display, True, text_color)

    screen.blit(point_surface, (10, 10))

    # Set the text content
    hp_display = f"lives: {g.player1.lives}"

    # Render the text as a Pygame surface
    hp_surface = font.render(hp_display, True, text_color)

    screen.blit(hp_surface, (SCREEN_WIDTH - 400, SCREEN_HEIGHT - 40))

    # Convert the screen surface to a string
    frame_data = pygame.image.tostring(screen, 'RGB')

    # Compress the frame data
    compressed_frame = zlib.compress(frame_data)

    # Get the size of the compressed frame
    frame_size = len(compressed_frame)

    # Pack the frame size into a 4-byte binary string
    frame_size_data = struct.pack('!I', frame_size)

    # Send the frame size and compressed frame to all clients
    for client_socket in clients:
        try:
            client_socket.sendall(frame_size_data)
            client_socket.sendall(compressed_frame)
        except:
            # Handle client disconnection
            clients.remove(client_socket)

    # Limit the frame rate
    clock.tick(60)

open('score.txt', 'a').write(f'Date:{datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}'
                             f'\nPacman:{clients[0].getsockname()}\nClyde:{clients[1].getsockname()}\nScore:'
                             f'{g.player1.points}\nIsWin:{won}\nLives:{g.player1.lives}\n\n')

pygame.time.wait(5000)
for client_socket in clients:
    client_socket.close()
# Close the server socket
server_socket.close()
