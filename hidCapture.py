import os
import sys
import time
import hid
from helper_functions import array_to_code, get_bytes_from_report, parse_index_string, is_gamepad


# Get the command-line argument for range of bytes
if len(sys.argv) > 1:
    wanted_bytes = sys.argv[1]
else:
    wanted_bytes = '0-63'

# Prompt the user to select an HID device
devices = hid.enumerate()
print('Select an HID device:')
for i, device in enumerate(devices):
    print(f'{i}: {device["manufacturer_string"]} {device["product_string"]}')
    # print(f'\t is gamepad?: {is_gamepad(device["vendor_id"],device["product_id"])}')
device_index = int(input('Device index: '))
device_info = devices[device_index]
vendor_id = device_info['vendor_id']
product_id = device_info['product_id']


# Open the selected device
device = hid.device()
device.open(vendor_id, product_id)

# Continuously read and print HID reports from the selected device
while True:
    # Clear the screen
    os.system('cls' if os.name == 'nt' else 'clear')

    # Read the next HID report (up to 64 bytes)
    report = device.read(64)

    # Print the report bytes as hexadecimal values
    readable = get_bytes_from_report(parse_index_string(wanted_bytes), report)
    print(readable)

    # Print the report as a copyable string
    #print(array_to_code(report))

    # Wait for 1/3 of a second
    time.sleep(1/3)
