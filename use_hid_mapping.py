import hid
from xbox_reports import XBOX_REPORT, print_xbox_report
from helper_functions import unique_values, get_data_stream_reports, select_hid_device
from gamepad_mapping import HIDButtonMapping, set_hid_mapping, check_for_saved_mapping, get_xbox_report_from_hidmap

buttons = HIDButtonMapping()
gamepad, vendor_id, product_id = select_hid_device(hid.enumerate())

# Look for an existing map for selected device
map_check = check_for_saved_mapping(f'{hex(vendor_id)}{hex(product_id)}')
# Load map if it exists
if map_check[0]:
    print("Loading Saved Button Map")
    # Load button map for known device
    buttons.load_button_maps(map_check[1])
else:
    # Set all inputs
    set_hid_mapping(gamepad, buttons, [])
    # Save mapping to %APPDATA%/APP_NAME
    buttons.save_button_maps(map_check[1])

### NOT WORKING
# Enable motion sensors
motion_sensor_command = [0xa2, 0x11, 0xc0, 0x20, 0xf0, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                         0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x43, 0x43, 0x00, 0x4d, 0x85, 0x00, 0x00, 0x00, 0x00, 0x00,
                         0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                         0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                         0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xd8, 0x8e, 0x94, 0xdd]
gamepad.write(motion_sensor_command)

### NOT WORKING
# Set light-bar color to green
set_color_command = [0x05, 0xff, 0x53, 0x46, 0x01, 0x00, 0x00, 0xff, 0x00, 0x00]
gamepad.send_feature_report(set_color_command)

# Build Input Lists
input_list = buttons.get_set_button_names()
stick_list = list(
    set(buttons.get_all_stick_button_names()).intersection(set(input_list)))  # Only sticks that have been set
trigger_list = list(
    set(buttons.get_all_trigger_button_names()).intersection(set(input_list)))  # Only triggers that have been set
button_list = unique_values(input_list, sum([stick_list, trigger_list], []))  # all other set inputs

# Display Mapping
buttons.display_button_maps()

# Obtain baseline controller readings and generate analytic reports
first_baseline, avg_baseline, median_baseline, mode_baseline, range_baseline = get_data_stream_reports(gamepad)
report_size = len(first_baseline)

# Convert gamepad reports into XBOX reports from mapping
xbox_report = XBOX_REPORT()
while True:
    get_xbox_report_from_hidmap(gamepad, report_size,  buttons, (stick_list, trigger_list, button_list), xbox_report)

    print_xbox_report(xbox_report)
