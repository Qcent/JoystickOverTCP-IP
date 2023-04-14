import socket
import ast
import pyvjoy
import urllib.request
import time
import argparse

# Create an argument parser
parser = argparse.ArgumentParser(description='Receive joystick data from a computer over tcp/ip')

# Add arguments to the parser
parser.add_argument('-p', '--port', type=str, help='Port that you would like to listen on')
parser.add_argument('-l', '--latency', action='store_true', help='Show latency output')

# Parse the arguments
args = parser.parse_args()

HOST = '0.0.0.0'    # listen on all addresses
# set port
if args.port:
    PORT = int(args.port)
else:
    PORT = 5000

# identify internal and external ip addresses
hostname = socket.gethostname()
lan_ip = socket.gethostbyname(hostname)
external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')

# establish server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (HOST, PORT)
server_socket.bind(server_address)
server_socket.listen(1)

# initialize vJoy joystick
joystick = pyvjoy.VJoyDevice(1)


def awaitConnection():
    print(f'Waiting for Connection on port: {PORT}\n\t\t LAN: {lan_ip}\n\t\t WAN: {external_ip}')

    # accept client connection
    client_socket, client_address = server_socket.accept()
    print(f'Connection from {client_address} established')

    response = 'Ok'
    client_timing = int(client_socket.recv(1024).decode())
    client_socket.sendall(response.encode())
    loop_count = 0
    print(f'Client Timing: {client_timing}fps established')

    # receive joystick input from client
    while True:
        try:
            data = client_socket.recv(1024)
            if args.latency:
                loop_count += 1
                if loop_count == 20:    # 20 round trips completed
                    end_time = time.time()
                    print(f'Latency: {((end_time - start_time )*1000) - 1000/client_timing : .2f} ms')
                    loop_count = 0
        except Exception:
            break

        if not data:
            break

        # parse joystick input
        data = ast.literal_eval(data.decode())
        axes = data['axes']
        buttons = data['buttons']
        hats = data['hats']

        # update vJoy joystick
        joystick.set_axis(pyvjoy.HID_USAGE_X, int(axes[0] * 16384 + 16384))
        joystick.set_axis(pyvjoy.HID_USAGE_Y, int(axes[1] * 16384 + 16384))
        joystick.set_axis(pyvjoy.HID_USAGE_RX, int(axes[2] * 16384 + 16384))
        joystick.set_axis(pyvjoy.HID_USAGE_RY, int(axes[3] * 16384 + 16384))
        joystick.set_axis(pyvjoy.HID_USAGE_Z, int(axes[4] * 16384 + 16384))
        joystick.set_axis(pyvjoy.HID_USAGE_RZ, int(axes[5] * 16384 + 16384))

        for i, button_state in enumerate(buttons):
            joystick.set_button(i+1, button_state)

        hat_value = hats[0]
        if hat_value == (0, 1):
            joystick.set_disc_pov(1, 0)
        elif hat_value == (0, -1):
            joystick.set_disc_pov(1, 2)
        elif hat_value == (-1, 0):
            joystick.set_disc_pov(1, 3)
        elif hat_value == (1, 0):
            joystick.set_disc_pov(1, 1)
        else:
            joystick.set_disc_pov(1, -1)

        # send response back to client
        try:
            client_socket.sendall(response.encode())
            if args.latency and loop_count == 19:
                start_time = time.time()        # let's calculate some latency
        except Exception:
            break

    # close connection
    client_socket.close()
    print("\tDisconnected")

    # reset vJoy joystick
    joystick.reset()


while True:
    awaitConnection()
