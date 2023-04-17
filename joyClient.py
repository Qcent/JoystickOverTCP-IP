import hid
import socket
import ipaddress
import time
import argparse
from helper_functions import is_gamepad

# Create an argument parser
parser = argparse.ArgumentParser(description='Send joystick data to a computer over tcp/ip')

# Add arguments to the parser
parser.add_argument('-n', '--host', type=str, help='IP address of host/server')
parser.add_argument('-p', '--port', type=str, help='Port that the host/server is listening on')
parser.add_argument('-f', '--fps', type=str,
                    help='How many times the client will attempt to communicate with server per second')
parser.add_argument('-l', '--latency', action='store_true', help='Show latency output')
parser.add_argument('-s', '--select', action='store_true', help='Show select input menu')
parser.add_argument('-a', '--auto', type=str, help='set to 0 to disable')

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

# set auto
if args.auto:
    args.auto = int(args.auto)
else:
    args.auto = 1

class FPSlimiter:
    def __init__(self, target_fps):
        self.target_fps = target_fps
        self.target_frame_time = 1.0 / target_fps
        self.last_frame_time = time.monotonic()

    def tick(self):
        current_time = time.monotonic()
        elapsed_time = current_time - self.last_frame_time
        sleep_time = self.target_frame_time - elapsed_time

        if sleep_time > 0:
            time.sleep(sleep_time)

        self.last_frame_time = current_time

def select_device(devices, auto_select=0):
    if len(devices) == 1 or auto_select == 1:
        device_index = 0
    else:
        # Prompt the user to select an HID device from a list of devices provided
        print('Select a Gamepad:')
        for i, device in enumerate(devices):
            print(f'{i}: {device["manufacturer_string"]} {device["product_string"]}',
                  f' ({device["vendor_id"]:x}, {device["product_id"]:x})' if args.select else '')
        device_index = int(input('Enter device index: '))
    device_info = devices[device_index]
    device = hid.device()
    device.open(device_info['vendor_id'], device_info['product_id'])
    print(f"Using joystick '{device_info['product_string']}'")

    return device


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

    print("Connected! \u263A")
    loop_count = 0

    # send joystick input to server
    while True:

        # Read the next HID report (up to 64 bytes)
        report = device.read(64)

        # let's calculate some latency
        if args.latency and loop_count == 19:
            start_time = time.time()

        # send joystick input to server
        try:
            # Shift bytearray because first byte is not needed
            client_socket.sendall(bytes(report[1:]))
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

        # run clock to limit FPS
        clock.tick()


# ENTRY POINT STARTS HERE

clock = FPSlimiter(TARGET_FPS)
FAILEDCONNECTIONS = 0
end_time = 0
start_time = 0

# Examine HID's  and search for known gamepads
devices = hid.enumerate()
gamepads = [device for device in devices if is_gamepad(device)]


# check if any joysticks are connected
joystick_count = len(gamepads)

if joystick_count > 0:
    if args.select:
        device = select_device(devices)
    else:
        device = select_device(gamepads,args.auto)
else:
    print("No gamepads detected.  \u2639")
    device = select_device(devices)

# main loop keeps client running
# asks for new host if connection fails 3 times
while True:
    establish_connection(get_host_address())
    FAILEDCONNECTIONS += 1
    if FAILEDCONNECTIONS > 3:
        args.host = ''
        FAILEDCONNECTIONS = 0
