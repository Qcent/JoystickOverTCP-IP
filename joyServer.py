import vgamepad as vg
import vgamepad.win.vigem_commons as vcom
import socket
import urllib.request
import time
import ctypes
import argparse


def convert_byte_array_to_ds4_report_ex(byte_array):
    ds4_report_ex = vcom.DS4_REPORT_EX()
    ctypes.memmove(ctypes.addressof(ds4_report_ex), byte_array, ctypes.sizeof(ds4_report_ex))
    return ds4_report_ex


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

    # initialize vgamepad emulating a DS4 controller
    gamepad = vg.VDS4Gamepad()

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

        # update gamepad
        gamepad.update_extended_report(
            convert_byte_array_to_ds4_report_ex(data)
        )

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

    # reset gamepad to default state
    gamepad.reset()
    gamepad.update()


while True:
    awaitConnection()
