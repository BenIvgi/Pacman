import pygame
import socket
import struct
import secret
import zlib

# Initialize Pygame
pygame.init()

# Game settings
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 750

# Load the icon image
ICON_IMAGE = pygame.image.load("pacman.png")

# Initialize the screen surface
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Set the caption of the window
pygame.display.set_caption("PacMan")

# Set the window icon
pygame.display.set_icon(ICON_IMAGE)


class Client:
    def __init__(self, ip, server_ip, server_port):
        self.client_socket = None
        self.ip = ip
        self.server_ip = server_ip
        self.server_port = server_port

    def send_input(self, msg):
        self.client_socket.sendall(secret.encrypt(msg).encode())

    def start(self):
        try:
            # Connect to the server
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_ip, self.server_port))
            print(f"Connected to server: {self.server_ip}:{self.server_port}")

            # Set the font and size
            font = pygame.font.Font('game_font.ttf', 70)  # You can specify the font file and size here

            # Set the text color
            text_color = (255, 255, 255)  # RGB value for black

            game_over_display = f"LOADING..."
            game_over_surface = font.render(game_over_display, True, text_color)
            screen.blit(game_over_surface,
                        ((SCREEN_WIDTH - game_over_surface.get_width()) // 2, SCREEN_HEIGHT // 2))
            pygame.display.flip()

            data = 'False'
            while data != 'True':
                secret.key_window(self.send_input)
                data = secret.decrypt(self.client_socket.recv(1024).decode().strip())

            running = True

            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            self.send_input('UP')
                        elif event.key == pygame.K_DOWN:
                            self.send_input('DOWN')
                        elif event.key == pygame.K_LEFT:
                            self.send_input('LEFT')
                        elif event.key == pygame.K_RIGHT:
                            self.send_input('RIGHT')

                # Receive the frame size from the server
                frame_size_data = self.client_socket.recv(4)
                frame_size = struct.unpack('!I', frame_size_data)[0]

                # Receive the compressed frame from the server
                compressed_frame = b''
                while len(compressed_frame) < frame_size:
                    data = self.client_socket.recv(frame_size - len(compressed_frame))
                    if not data:
                        break
                    compressed_frame += data

                # Decompress the frame data
                frame_data = pygame.image.fromstring(zlib.decompress(compressed_frame), (SCREEN_WIDTH, SCREEN_HEIGHT),
                                                     'RGB')

                # Display the frame on the screen
                screen.blit(frame_data, (0, 0))
                pygame.display.flip()
        except ConnectionResetError:
            self.client_socket.close()
            pygame.quit()


if __name__ == "__main__":
    c = Client('127.0.0.1', '127.0.0.1', 5000)
    c.start()
