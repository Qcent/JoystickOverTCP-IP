import pygame
import socket
import ipaddress
import time
import argparse

# Create an argument parser
parser = argparse.ArgumentParser(description='Send joystick data to a computer over tcp/ip')

# Add arguments to the parser
parser.add_argument('-n', '--host', type=str, help='IP address of host/server')
parser.add_argument('-p', '--port', type=str, help='Port that the host/server is listening on')
parser.add_argument('-f', '--fps', type=str,
                    help='How many times the client will attempt to communicate with server per second')
parser.add_argument('-l', '--latency', action='store_true', help='Show latency output')
parser.add_argument('-s', '--select', action='store_true', help='Show select joystick screen')

# Parse the arguments
args = parser.parse_args()

# set port
if args.port:
    PORT = int(args.port)
else:
    PORT = 5000

# set fps
if args.port:
    TARGET_FPS = int(args.fps)
else:
    TARGET_FPS = 50

# initialize pygame
pygame.init()
clock = pygame.time.Clock()

# initialize the joystick module
pygame.joystick.init()

# get the number of joysticks connected
joystick_count = pygame.joystick.get_count()


def default_joystick():
    # get the first joystick
    return pygame.joystick.Joystick(0)


def select_joystick():
    # if there are any joystick devices connected
    if joystick_count > 0:
        # allow user to select a joystick device
        print("Select a joystick device:")
        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            print(f"{i}: {joystick.get_name()}")

        joystick_index = int(input("Enter joystick index: "))
        return pygame.joystick.Joystick(joystick_index)


def get_host_address():
    # request server ip address
    while True:
        if not args.host:
            host_address = input("Please enter the host ip address (or nothing for localhost): ")
        else:
            host_address = args.host
        if not host_address:
            host_address = "127.0.0.1"
        try:
            ipaddress.ip_address(host_address)
            break
        except ValueError:
            print("Invalid IP address. Please try again.")
            args.host = ''
    return host_address


def establish_connection(ip_address):
    # establish client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (ip_address, PORT)
    try:
        client_socket.connect(server_address)
        client_socket.sendall(str(TARGET_FPS).encode())
        response = client_socket.recv(1024)
    except Exception:
        print("<< Connection Failed >>")
        return False

    print("Connected!")
    loop_count = 0

    # send joystick input to server
    while True:
        # handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                client_socket.close()
                pygame.quit()
                quit()

        # get joystick input and store in data
        data = {'axes': [joystick.get_axis(i) for i in range(joystick.get_numaxes())],
                'buttons': [joystick.get_button(i) for i in range(joystick.get_numbuttons())],
                'hats': [joystick.get_hat(i) for i in range(joystick.get_numhats())]}

        # let's calculate some latency
        if args.latency and loop_count == 19:
            start_time = time.time()

        # send joystick input to server
        message = str(data)
        try:
            client_socket.sendall(message.encode())
        except Exception:
            print("<< Connection Lost >>")
            return False

        # wait for server response
        try:
            response = client_socket.recv(1024)
            if args.latency:
                loop_count += 1
                if loop_count == 20:
                    end_time = time.time()          # 20 round trips completed
                    print(f'Latency: {(end_time - start_time)*1000 : .2f} ms')
                    loop_count = 0
            # print(response.decode())
        except Exception:
            print("<< Connection Lost >>")
            return False

        # set clock to limit FPS
        clock.tick(TARGET_FPS)


# LOOP STARTS HERE

FAILEDCONNECTIONS = 0
end_time = 0
start_time = 0

# check if any joysticks are connected
if joystick_count > 0:
    if args.select:
        joystick = select_joystick()
    else:
        joystick = default_joystick()
    joystick.init()
    print(f"Using joystick '{joystick.get_name()}'")
    while True:
        establish_connection(get_host_address())
        FAILEDCONNECTIONS += 1
        if FAILEDCONNECTIONS > 3:
            args.host = ''
            FAILEDCONNECTIONS = 0
else:
    print("No joysticks detected.")
