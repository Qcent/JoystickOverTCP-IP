import socket
import ast
import pyvjoy
import urllib.request

external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
HOST = '0.0.0.0'
PORT = 5000

# establish server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (HOST, PORT)
server_socket.bind(server_address)
server_socket.listen(1)

# initialize vJoy joystick
joystick = pyvjoy.VJoyDevice(1)

def awaitConnection():
    print(f'Waiting for Connection on {external_ip}')

    # accept client connection
    client_socket, client_address = server_socket.accept()
    print(f'Connection from {client_address} established')

    # receive joystick input from client
    while True:
        data = client_socket.recv(1024)
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
        response = 'Ok'
        client_socket.sendall(response.encode())

    # close connection
    client_socket.close()
    print("\tDisconnected")

    # reset vJoy joystick
    joystick.reset()

while True:
    awaitConnection()