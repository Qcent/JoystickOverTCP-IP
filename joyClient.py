import pygame
import socket
import ipaddress
import time

# initialize pygame
pygame.init()
clock = pygame.time.Clock()

# find all connected joystick devices
pygame.joystick.init()
joystick_count = pygame.joystick.get_count()
print(f"Found {joystick_count} joystick devices")

# if there are any joystick devices connected
if joystick_count > 0:
    # allow user to select a joystick device
    print("Select a joystick device:")
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        print(f"{i}: {joystick.get_name()}")

    joystick_index = int(input("Enter joystick index: "))
    joystick = pygame.joystick.Joystick(joystick_index)
    joystick.init()
    print(f"Using joystick '{joystick.get_name()}'")


# request server ip address
while True:
    ip_address = input("Please enter the host address (or nothing for localhost): ")
    if not ip_address:
        ip_address = "127.0.0.1"
    try:
        ipaddress.ip_address(ip_address)
        break
    except ValueError:
        print("Invalid IP address. Please try again.")

def establishConnection():
    # establish client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (ip_address, 5000)
    client_socket.connect(server_address)

    print("Connected!")

    # send joystick input to server
    while True:
        # handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                client_socket.close()
                pygame.quit()
                quit()

        # get joystick input
        data = {}
        data['axes'] = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
        data['buttons'] = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]
        data['hats'] = [joystick.get_hat(i) for i in range(joystick.get_numhats())]

        # send joystick input to server
        message = str(data)
        client_socket.sendall(message.encode())

        # wait for server response
        try:
            response = client_socket.recv(1024)
            # print(response.decode())
        except Exception as e:
            print("Connection failed... Attempting to re-Establish:")
            time.sleep(0.3)
            establishConnection()

        # set clock to limit FPS
        clock.tick(60)

establishConnection()