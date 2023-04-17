import os
import sys
import time
import hid
from helper_functions import monitor_byte_array

def array_to_code(arr):
    """
    Takes a byte array and outputs it in a format that can be copied and pasted
    into a script.
    """
    output = "byte_array = [\n"
    for i in range(len(arr)):
        if i % 16 == 0:
            output += "    "
        output += "{:#04x}, ".format(arr[i])
        if i % 16 == 15 or i == len(arr) - 1:
            output = output[:-2] + "\n"
            if i != len(arr) - 1:
                output += "    "
    output += "]"
    return output


def get_bytes_from_report(indices, report, items_per_line=16):
    """
    Returns a string containing the bytes from an HID report that correspond to the provided indices.

    Parameters:
    - indices: A list of integers representing the indices of the bytes to extract from the report.
    - report: A bytes object representing an HID report.

    Returns:
    A string containing the bytes from the report that correspond to the provided indices.
    """
    num_indices = len(indices)
    chunks = [indices[i:i+items_per_line] for i in range(0, num_indices, items_per_line)]
    output = ""

    for i, chunk in enumerate(chunks):
        index_header = " Byte: " + "   ".join([f"{i+1:02}" for i in chunk])
        value_header = "Value: " + "   ".join([f"{report[i]:02X}" for i in chunk])
        output += f"{index_header}\n{value_header}\n\n"

    print(output)


def parse_index_string(index_string):
    """
    Returns a list of integers representing the indices specified in the provided string.

    Parameters:
    - index_string: A string containing ranges and values separated by commas.
                    Example: "2-12,16,20,22-26,30"

    Returns:
    A list of integers representing the indices specified in the provided string.
    """
    indices = []
    ranges = index_string.split(",")
    for r in ranges:
        if "-" in r:
            start, end = r.split("-")
            indices.extend(range(int(start), int(end) + 1))
        else:
            indices.append(int(r))
    return indices


# Get the command-line argument for range of bytes
if len(sys.argv) > 1:
    wanted_bytes = sys.argv[1]
else:
    wanted_bytes = '0-15'

# Prompt the user to select an HID device
devices = hid.enumerate()
print('Select an HID device:')
for i, device in enumerate(devices):
    print(f'{i}: {device["manufacturer_string"]} {device["product_string"]}')
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

# TEST BUTTON MAPPING CAPTURE
    #monitor_byte_array(report, ["Triangle", "Circle", "Square", "Cross", "Left Stick X", "Left Stick Y"])

    # Print the report bytes as hexadecimal values
    #print('Report:', ' '.join(f'{b:02x}' for b in report))
    get_bytes_from_report(parse_index_string(wanted_bytes), report)

    # Print the report as a copyable string
    #print(array_to_code(report))

    # Wait for 1/3 of a second
    time.sleep(1/3)
