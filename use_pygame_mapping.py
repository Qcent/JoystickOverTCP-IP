import pygame
from xbox_reports import XBOX_REPORT, print_xbox_report
from helper_functions import select_pygame_device, encode_string_to_hex
from gamepad_mapping import PyGameButtonMapping, set_pygame_mapping, check_for_saved_mapping, get_xbox_report_from_pymap


pygame.init()

# User selects gamepad
gamepad = select_pygame_device(pygame)

# Initialize a GamepadMapping object
buttons = PyGameButtonMapping()

# Look for an existing map for selected device
map_check = check_for_saved_mapping(f'{encode_string_to_hex(gamepad.get_name())}')

# Load map if it exists
if map_check[0]:
    print("Loading Saved Button Map")
    # Load button map for known device
    buttons.load_button_maps(map_check[1])
else:
    # Set all inputs
    set_pygame_mapping(pygame, gamepad, buttons, [])
    # Save mapping to %APPDATA%/APP_NAME
    buttons.save_button_maps(map_check[1])

# Build Input Lists
input_list = buttons.get_set_button_names()

# Display Mapping
buttons.display_button_maps()

# Convert gamepad reports into XBOX reports from mapping
xbox_report = XBOX_REPORT()
while True:
    get_xbox_report_from_pymap(pygame, gamepad, buttons, input_list, xbox_report)
    print_xbox_report(xbox_report)
