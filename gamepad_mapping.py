import keyboard
import os
import pickle
import helper_functions as hfunc
from xbox_reports import XBOX_REPORT, XBOX_BUTTON

APP_NAME = 'joyClient'  # saved maps will be in %APPDATA%/APP_NAME
STICK_THRESHOLD = 24  # stick HID input must change value by threshold to be noticed


class PyGameButtonMapping:
    class ButtonMap:
        def __init__(self, input_type=None, index=None, value=None):
            self.input_type = input_type
            self.index = index
            self.value = value

        def set(self, type=None, index=None, value=None):
            self.input_type = type
            self.index = index
            self.value = value

        def clear(self):
            self.input_type = None
            self.index = None
            self.value = None

        def set_type(self, type):
            self.input_type = type

        def set_index(self, index):
            self.index = index

        def set_value(self, value):
            self.value = value

    def __init__(self):
        self.DPAD_UP = self.ButtonMap()
        self.DPAD_DOWN = self.ButtonMap()
        self.DPAD_LEFT = self.ButtonMap()
        self.DPAD_RIGHT = self.ButtonMap()
        self.START = self.ButtonMap()
        self.BACK = self.ButtonMap()
        self.LEFT_THUMB = self.ButtonMap()
        self.RIGHT_THUMB = self.ButtonMap()
        self.LEFT_SHOULDER = self.ButtonMap()
        self.RIGHT_SHOULDER = self.ButtonMap()
        self.GUIDE = self.ButtonMap()
        self.A = self.ButtonMap()
        self.B = self.ButtonMap()
        self.X = self.ButtonMap()
        self.Y = self.ButtonMap()

        self.LEFT_TRIGGER = self.ButtonMap()
        self.RIGHT_TRIGGER = self.ButtonMap()

        self.LEFT_STICK_X = self.ButtonMap()
        self.LEFT_STICK_Y = self.ButtonMap()
        self.RIGHT_STICK_X = self.ButtonMap()
        self.RIGHT_STICK_Y = self.ButtonMap()

    def display_button_maps(self):
        button_maps = [attr for attr in dir(self) if isinstance(getattr(self, attr), self.ButtonMap)]
        for button_map in button_maps:
            print(
                f"Name: {button_map}, Input Type: {getattr(self, button_map).input_type}, Type Index: {getattr(self, button_map).index}, Value: {getattr(self, button_map).value}")

    def save_button_maps(self, filename):
        button_list = []
        button_maps = [attr for attr in dir(self) if isinstance(getattr(self, attr), self.ButtonMap)]
        for button_map in button_maps:
            button_list.append([button_map,
                                getattr(self, button_map).input_type,
                                getattr(self, button_map).index,
                                getattr(self, button_map).value])
        with open(filename, 'wb') as f:
            pickle.dump(button_list, f)

    def load_button_maps(self, filename):
        with open(filename, 'rb') as f:
            button_list = pickle.load(f)
        for button_data in button_list:
            button_name, type, index, value = button_data
            setattr(self, button_name, self.ButtonMap(type, index, value))

    def get_all_button_names(self):
        return [attr for attr in dir(self) if isinstance(getattr(self, attr), self.ButtonMap)]

    def get_set_button_names(self):
        return [attr for attr in dir(self) if
                isinstance(getattr(self, attr), self.ButtonMap) and getattr(self, attr).input_type is not None]

    def get_unset_button_names(self):
        return [attr for attr in dir(self) if
                isinstance(getattr(self, attr), self.ButtonMap) and getattr(self, attr).input_type is None]

    def get_all_stick_button_names(self):
        button_names = self.get_all_button_names()
        return [name for name in button_names if 'stick' in name.lower()]

    def get_all_trigger_button_names(self):
        button_names = self.get_all_button_names()
        return [name for name in button_names if 'trigger' in name.lower()]

    def get_all_thumb_button_names(self):
        button_names = self.get_all_button_names()
        return [name for name in button_names if 'thumb' in name.lower()]

    def get_all_shoulder_button_names(self):
        button_names = self.get_all_button_names()
        return [name for name in button_names if 'shoulder' in name.lower()]

    def get_all_dpad_button_names(self):
        button_names = self.get_all_button_names()
        return [name for name in button_names if 'dpad' in name.lower()]

    def get_all_generic_button_names(self):
        button_names = self.get_all_button_names()
        generic_names = [name for name in button_names if not ('dpad' in name.lower() or 'shoulder' in name.lower()
                                                               or 'thumb' in name.lower() or 'trigger' in name.lower()
                                                               or 'stick' in name.lower())]
        return sorted(generic_names, key=lambda x: len(x))


class HIDButtonMapping:
    class ButtonMap:
        def __init__(self, byte_offset=None, bit_offset=None, value=None):
            self.byte_offset = byte_offset
            self.bit_offset = bit_offset
            self.value = value

        def set(self, byte_offset=None, bit_offset=None, value=None):
            self.byte_offset = byte_offset
            self.bit_offset = bit_offset
            self.value = value

        def clear(self):
            self.byte_offset = None
            self.bit_offset = None
            self.value = None

        def set_byte_offset(self, byte_offset):
            self.byte_offset = byte_offset

        def set_bit_offset(self, bit_offset):
            self.bit_offset = bit_offset

        def set_value(self, value):
            self.value = value

    def __init__(self):
        self.DPAD_UP = self.ButtonMap()
        self.DPAD_DOWN = self.ButtonMap()
        self.DPAD_LEFT = self.ButtonMap()
        self.DPAD_RIGHT = self.ButtonMap()
        self.START = self.ButtonMap()
        self.BACK = self.ButtonMap()
        self.LEFT_THUMB = self.ButtonMap()
        self.RIGHT_THUMB = self.ButtonMap()
        self.LEFT_SHOULDER = self.ButtonMap()
        self.RIGHT_SHOULDER = self.ButtonMap()
        self.GUIDE = self.ButtonMap()
        self.A = self.ButtonMap()
        self.B = self.ButtonMap()
        self.X = self.ButtonMap()
        self.Y = self.ButtonMap()

        self.LEFT_TRIGGER = self.ButtonMap()
        self.RIGHT_TRIGGER = self.ButtonMap()

        self.LEFT_STICK_X = self.ButtonMap()
        self.LEFT_STICK_Y = self.ButtonMap()
        self.RIGHT_STICK_X = self.ButtonMap()
        self.RIGHT_STICK_Y = self.ButtonMap()

    def display_button_maps(self):
        button_maps = [attr for attr in dir(self) if isinstance(getattr(self, attr), self.ButtonMap)]
        for button_map in button_maps:
            print(
                f"Name: {button_map}, Byte offset: {getattr(self, button_map).byte_offset}, Bit offset: {getattr(self, button_map).bit_offset}, Value: {getattr(self, button_map).value}")

    def save_button_maps(self, filename):
        button_list = []
        button_maps = [attr for attr in dir(self) if isinstance(getattr(self, attr), self.ButtonMap)]
        for button_map in button_maps:
            button_list.append([button_map,
                                getattr(self, button_map).byte_offset,
                                getattr(self, button_map).bit_offset,
                                getattr(self, button_map).value])
        with open(filename, 'wb') as f:
            pickle.dump(button_list, f)

    def load_button_maps(self, filename):
        with open(filename, 'rb') as f:
            button_list = pickle.load(f)
        for button_data in button_list:
            button_name, byte_offset, bit_offset, value = button_data
            setattr(self, button_name, self.ButtonMap(byte_offset, bit_offset, value))

    def get_all_button_names(self):
        return [attr for attr in dir(self) if isinstance(getattr(self, attr), self.ButtonMap)]

    def get_set_button_names(self):
        return [attr for attr in dir(self) if
                isinstance(getattr(self, attr), self.ButtonMap) and getattr(self, attr).byte_offset is not None]

    def get_unset_button_names(self):
        return [attr for attr in dir(self) if
                isinstance(getattr(self, attr), self.ButtonMap) and getattr(self, attr).byte_offset is None]

    def get_all_stick_button_names(self):
        button_names = self.get_all_button_names()
        return [name for name in button_names if 'stick' in name.lower()]

    def get_all_trigger_button_names(self):
        button_names = self.get_all_button_names()
        return [name for name in button_names if 'trigger' in name.lower()]

    def get_all_thumb_button_names(self):
        button_names = self.get_all_button_names()
        return [name for name in button_names if 'thumb' in name.lower()]

    def get_all_shoulder_button_names(self):
        button_names = self.get_all_button_names()
        return [name for name in button_names if 'shoulder' in name.lower()]

    def get_all_dpad_button_names(self):
        button_names = self.get_all_button_names()
        return [name for name in button_names if 'dpad' in name.lower()]

    def get_all_generic_button_names(self):
        button_names = self.get_all_button_names()
        generic_names = [name for name in button_names if not ('dpad' in name.lower() or 'shoulder' in name.lower()
                                                               or 'thumb' in name.lower() or 'trigger' in name.lower()
                                                               or 'stick' in name.lower())]
        return sorted(generic_names, key=lambda x: len(x))


def check_for_saved_mapping(_filename) -> []:
    appdata_folder = os.getenv('APPDATA')
    save_folder = os.path.join(appdata_folder, APP_NAME)
    filename = os.path.join(save_folder, f'{_filename}.map')

    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
        return [False, filename]

    if os.path.isfile(filename):
        return [True, filename]
    else:
        return [False, filename]


def input_verb(type):
    if type == 3:
        return "squeeze"
    if type == 2:
        return "move"
    else:
        return "press"


def format_input_name(name: str) -> str:
    name = name.replace('_', ' ')
    if ' ' not in name:
        name += ' Button'
    return ' '.join(word.capitalize() for word in name.split())


# HID mapping functions
def get_xbox_report_from_hidmap(gamepad, report_size, buttons, input_lists: ([[str]]), xbox_report: XBOX_REPORT):
    (stick_list, trigger_list, button_list) = input_lists
    # Receive new input report
    report = gamepad.read(report_size)

    for input_name in stick_list:
        button_value = get_xbox_input_from_bytearray('XBOX_' + input_name,
                                                     getattr(buttons, input_name).value,
                                                     report,
                                                     getattr(buttons, input_name).byte_offset,
                                                     getattr(buttons, input_name).bit_offset,
                                                     )
        # Assign value to the proper XBOX report field
        if input_name == 'LEFT_STICK_X':
            xbox_report.sThumbLX = hfunc.byte_to_c_short(button_value)
        if input_name == 'LEFT_STICK_Y':
            xbox_report.sThumbLY = hfunc.byte_to_c_short(button_value)
        if input_name == 'RIGHT_STICK_X':
            xbox_report.sThumbRX = hfunc.byte_to_c_short(button_value)
        if input_name == 'RIGHT_STICK_Y':
            xbox_report.sThumbRY = hfunc.byte_to_c_short(button_value)

    for input_name in trigger_list:
        button_value = get_xbox_input_from_bytearray('XBOX_' + input_name,
                                                     getattr(buttons, input_name).value,
                                                     report,
                                                     getattr(buttons, input_name).byte_offset,
                                                     getattr(buttons, input_name).bit_offset,
                                                     )
        # Assign value to the proper XBOX report field
        if input_name == 'LEFT_TRIGGER':
            xbox_report.bLeftTrigger = hfunc.byte_to_c_byte(button_value)
        if input_name == 'RIGHT_TRIGGER':
            xbox_report.bRightTrigger = hfunc.byte_to_c_byte(button_value)

    # Add all generic values together for button field
    button_value = 0
    for input_name in button_list:
        button_value += get_xbox_input_from_bytearray('XBOX_' + input_name,
                                                      getattr(buttons, input_name).value,
                                                      report,
                                                      getattr(buttons, input_name).byte_offset,
                                                      getattr(buttons, input_name).bit_offset)
    # Assign button_value to the proper XBOX report button field
    xbox_report.wButtons = button_value


def get_xbox_input_from_bytearray(name: str, comparison: str,
                                  bytearray_: bytearray, byte_offset: int, bit_offset: int):
    """
    Compares bits in bytearray at given byte offset and bit offset to given comparison value.
    If comparison value is found, returns corresponding XBOX_BUTTON value based on input name.
    """
    # Convert comparison value to binary string and pad to 8 bits if necessary
    #  if isinstance(comparison, int):
    #    comparison = bin(comparison)[2:]  # .zfill(8)
    #  comparison = comparison.rjust(8, '0')

    # Get byte value at byte offset
    byte_value = bytearray_[byte_offset]

    if not bit_offset and not comparison:
        return byte_value

    # Create mask to extract required bits
    mask = (1 << len(comparison)) - 1
    mask <<= bit_offset

    # Extract bits from byte value
    bits = (byte_value & mask) >> bit_offset

    if hfunc.get_input_type(name) == 2:  # Stick by button
        return bits * 255

    # Compare bits to comparison value
    if bits == int(comparison, 2):
        if hfunc.get_input_type(name) == 3:  # Trigger by button
            return 255

        # Return corresponding XBOX_BUTTON value based on input name
        return getattr(XBOX_BUTTON, name)
    else:
        return XBOX_BUTTON(0)


def filter_hid_stick_gitter(results, stick_indices) -> []:
    output = []
    for byte in results:
        if byte['index'] in stick_indices:
            # sticks must clear a threshold to be considered an active input
            if abs(byte['second_value'] - byte['first_value']) \
                    > max([range_baseline[byte['index']] * 3, STICK_THRESHOLD]):
                output.append(byte)
        else:
            output.append(byte)
    return output


def hat_check(byte_offset, report):
    DPAD_UP = '0000'
    DPAD_DOWN = '0100'
    DPAD_LEFT = '0110'
    DPAD_RIGHT = '0010'
    value = bin(report[byte_offset])[2:].zfill(4)
    if value == DPAD_UP or value == DPAD_RIGHT or value == DPAD_DOWN or value == DPAD_LEFT:
        return value
    return False


def wait_for_no_hid_gamepad_input(gamepad, ignore_indices, stick_indices):
    awaiting_silence = True
    while awaiting_silence:
        results_canceled = 0
        # Receive updates from the device
        update = gamepad.read(report_size)
        # Compare update to the average baseline reading, ignoring supplied indices
        results = hfunc.get_diff_in_bytearrays(avg_baseline, update, ignore_indices)

        for byte in results:
            if byte['index'] in stick_indices:
                # sticks must clear a threshold to be considered an active input
                if abs(byte['second_value'] - byte['first_value']) \
                        < max([range_baseline[byte['index']] * 2, STICK_THRESHOLD]):
                    results_canceled += 1

        if len(results) - results_canceled == 0:
            awaiting_silence = False


def receive_single_hid_input_map(gamepad, ignore_indices, stick_indices):
    offset_byte = offset_bit = value = None
    while True:
        # Allow for a user abort on input
        if keyboard.is_pressed('esc'):
            while keyboard.is_pressed('esc'):
                True
            return None, None, None
        # Receive updates from the device
        update = gamepad.read(report_size)
        # Find bytes with values different from their baseline average
        results = hfunc.get_diff_in_bytearrays(avg_baseline, update, ignore_indices)
        # Filter results to remove stick gitter
        results = filter_hid_stick_gitter(results, stick_indices)

        for byte in results:
            offset_byte = byte["index"]
            offset_bit = value = None
            bits = hfunc.get_bits_different(byte['first_value'], byte['second_value'])

            if byte['index'] in stick_indices:
                # sticks must clear a threshold to be considered an active input
                if abs(byte['second_value'] - byte['first_value']) \
                        > max([range_baseline[byte['index']] * 2, STICK_THRESHOLD]):
                    # print(f'condition 1 - stick')
                    return offset_byte, offset_bit, value

            elif avg_baseline[byte['index']] == 0x0F or avg_baseline[byte['index']] == 0x08:
                # likely DPAD nibble change
                value = hat_check(byte["index"], update)
                if value:
                    offset_bit = 0
                    # print(f'condition 2 - d-hat')
                    return offset_byte, offset_bit, value

            elif len(results) == 2:  # likely trigger bit with value byte
                if len(bits) > 2:  # Trigger value detected
                    # print(f'condition 3 - analog trigger')
                    return offset_byte, offset_bit, value

            if len(results) == 1 and len(bits) == 1 and byte['index'] not in stick_indices:
                # Single bit button
                offset_bit = bits[0]
                value = f'{hfunc.get_bit_value(update, offset_byte, offset_bit)}'
                # print(f'condition 4 - normal button')
                return offset_byte, offset_bit, value


def set_hid_mapping(gamepad, buttons: HIDButtonMapping, input_list: [str]):
    # Default Inputs (all)
    if not input_list:
        input_list = sum([buttons.get_all_stick_button_names(),
                          buttons.get_all_shoulder_button_names(),
                          buttons.get_all_trigger_button_names(),
                          buttons.get_all_thumb_button_names(),
                          buttons.get_all_dpad_button_names(),
                          buttons.get_all_generic_button_names()
                          ], [])

    # Obtain baseline controller readings and generate analytic reports
    global first_baseline, avg_baseline, median_baseline, mode_baseline, range_baseline, report_size
    first_baseline, avg_baseline, median_baseline, mode_baseline, range_baseline = \
        hfunc.get_data_stream_reports(gamepad)
    report_size = len(first_baseline)

    # Rule out non-user input fields
    ignore_indices = hfunc.find_values_in(range_baseline, '>0')  # values that changed at all during the sample
    ignore_indices += hfunc.find_values_in(avg_baseline, '>133')  # average values higher than expected neutral sticks

    # Intuit likely stick indices
    stick_step1 = hfunc.find_values_in(avg_baseline, '~127/12')  # expected neutral stick average within 12
    stick_step2 = hfunc.find_values_in(range_baseline, '~0/9')  # expected neutral stick range within 9
    stick_indices = list(set(stick_step1).intersection(set(stick_step2)))

    # filter out higher indexed possible sticks as they are likely motion controls
    # the first four are usually the two main sticks
    stick_indices = sorted(stick_indices)[:4]

    # remove gittery sticks from ignored indices
    # ignore_indices = [item for item in ignore_indices if item not in stick_indices]

    # Create a dictionary to ensure no input is used twice
    received_input = {}

    # display ignore and stick indices
    print(f'Ignore Indices: {ignore_indices}')
    print(f'Stick Indices: {stick_indices}')

    # Map all inputs in input_list
    for input_name in input_list:
        input_type = hfunc.get_input_type(input_name)

        # Prompt the user for input
        print(f"{input_verb(input_type).capitalize()} {format_input_name(input_name)} ...")

        # Wait for no input to be detected
        wait_for_no_hid_gamepad_input(gamepad, ignore_indices, stick_indices)

        # Receive updates from the device and map inputs
        setting_input = True
        while setting_input:
            # Receive an input signature
            byte_offset, bit_offset, value = receive_single_hid_input_map(gamepad, ignore_indices, stick_indices)
            # create dictionary key from input
            input_key = (byte_offset, bit_offset, value)
            if input_key == (None, None, None):
                print(f'<< Input {format_input_name(input_name)} has been skipped! >>')
                setting_input = False
            elif input_key not in received_input:
                received_input[input_key] = True
                # if bit_offset == None:  # input uses entire byte
                # block its inputs // this is a fix for a bad stick i am testing with
                #    ignore_indices.append(byte_offset)
                setting_input = False
            else:
                print(f'<< That button has already been used! >>')
                # Prompt the user for input
                print(f"{input_verb(input_type).capitalize()} {format_input_name(input_name)} ...")

        # print(f'Set at byte: {hex(byte_offset)}  bit: {bit_offset} with a value of: {value} \n')
        getattr(buttons, input_name).set(byte_offset, bit_offset, value)


# PyGame mapping functions
def get_xbox_report_from_pymap(pygame, gamepad, buttons, input_list: [str], xbox_report: XBOX_REPORT):
    # Reset button values
    xbox_report.wButtons = 0
    # Receive new input events
    pygame.event.get()

    for input_name in input_list:
        (typ, idx, val) = (getattr(buttons, input_name).input_type,
                           getattr(buttons, input_name).index,
                           getattr(buttons, input_name).value)
        # Hat Value
        if typ == 4:
            button_value = get_hat_direction_from_tuple(gamepad.get_hat(idx))
            if val == button_value:
                # Assign value to the proper XBOX report field
                if input_name == 'LEFT_STICK_X':
                    xbox_report.sThumbLX = hfunc.float_to_c_short(button_value)
                elif input_name == 'LEFT_STICK_Y':
                    xbox_report.sThumbLY = hfunc.float_to_c_short(button_value)
                elif input_name == 'RIGHT_STICK_X':
                    xbox_report.sThumbRX = hfunc.float_to_c_short(button_value)
                elif input_name == 'RIGHT_STICK_Y':
                    xbox_report.sThumbRY = hfunc.float_to_c_short(button_value)
                elif input_name == 'LEFT_TRIGGER':
                    xbox_report.bLeftTrigger = hfunc.byte_to_c_byte(button_value)
                elif input_name == 'RIGHT_TRIGGER':
                    xbox_report.bRightTrigger = hfunc.byte_to_c_byte(button_value)
                else:
                    # Return corresponding XBOX_BUTTON value based on input name
                    xbox_report.wButtons += getattr(XBOX_BUTTON, 'XBOX_' + input_name)
        # Axis Value
        elif typ == 2:
            button_value = gamepad.get_axis(idx)
            # Assign value to the proper XBOX report field
            if input_name == 'LEFT_STICK_X':
                xbox_report.sThumbLX = hfunc.float_to_c_short(button_value)
            elif input_name == 'LEFT_STICK_Y':
                xbox_report.sThumbLY = hfunc.float_to_c_short(button_value * -1)
            elif input_name == 'RIGHT_STICK_X':
                xbox_report.sThumbRX = hfunc.float_to_c_short(button_value)
            elif input_name == 'RIGHT_STICK_Y':
                xbox_report.sThumbRY = hfunc.float_to_c_short(button_value * -1)
            elif input_name == 'LEFT_TRIGGER':
                xbox_report.bLeftTrigger = hfunc.float_to_c_byte(button_value)
            elif input_name == 'RIGHT_TRIGGER':
                xbox_report.bRightTrigger = hfunc.float_to_c_byte(button_value)
        # Standard Button
        if typ == 1:
            button_value = gamepad.get_button(idx)
            if input_name == 'LEFT_STICK_X':
                xbox_report.sThumbLX = hfunc.float_to_c_short(button_value)
            elif input_name == 'LEFT_STICK_Y':
                xbox_report.sThumbLY = hfunc.float_to_c_short(button_value)
            elif input_name == 'RIGHT_STICK_X':
                xbox_report.sThumbRX = hfunc.float_to_c_short(button_value)
            elif input_name == 'RIGHT_STICK_Y':
                xbox_report.sThumbRY = hfunc.float_to_c_short(button_value)
            elif input_name == 'LEFT_TRIGGER':
                xbox_report.bLeftTrigger = hfunc.byte_to_c_byte(button_value * 255)
            elif input_name == 'RIGHT_TRIGGER':
                xbox_report.bRightTrigger = hfunc.byte_to_c_byte(button_value * 255)
            elif button_value:
                # Return corresponding XBOX_BUTTON value based on input name
                xbox_report.wButtons += getattr(XBOX_BUTTON, 'XBOX_' + input_name)


def get_hat_direction_from_tuple(hat_tuple):
    """
    Translates a tuple returned by pygame .get_hat() into an integer flag for the cardinal direction.
    """
    x, y = hat_tuple
    if x == 1 and y == 0:
        return 1  # East
    elif x == 1 and y == 1:
        return 2  # Northeast
    elif x == 0 and y == 1:
        return 3  # North
    elif x == -1 and y == 1:
        return 4  # Northwest
    elif x == -1 and y == 0:
        return 5  # West
    elif x == -1 and y == -1:
        return 6  # Southwest
    elif x == 0 and y == -1:
        return 7  # South
    elif x == 1 and y == -1:
        return 8  # Southeast
    else:
        return 0  # No cardinal direction


def wait_for_no_pygamepad_input(pygame, gamepad):
    awaiting_silence = True
    while awaiting_silence:
        pygame.event.get()
        axis_value = button_value = hat_value = 0
        # iterate over all gamepad axes and record their value
        for i in range(gamepad.get_numaxes()):
            read_val = gamepad.get_axis(i)
            axis_value += read_val if abs(read_val) - 1 > .25 else 0
        # iterate over all gamepad buttons and record their value
        for i in range(gamepad.get_numbuttons()):
            button_value += gamepad.get_button(i)
        # iterate over DPad axes and record their value
        for i in range(gamepad.get_numhats()):
            hat_value += get_hat_direction_from_tuple(gamepad.get_hat(i))
        # if no values are detected the function may exit
        if not axis_value + hat_value + button_value:
            awaiting_silence = False
        # print(f'hats:{hat_value}\t buttons:{button_value} \t axis:{axis_value}')


def get_pygamepad_input(pygame, gamepad):
    BUTTON = 1
    STICK = 2
    DPAD = 4
    while True:
        pygame.event.get()
        # Allow for a user abort on input
        if keyboard.is_pressed('esc'):
            while keyboard.is_pressed('esc'):
                True
            return None, None, None
        # iterate over all gamepad axes
        for i in range(input_info[0]):  # gamepad.get_numaxes()):
            if abs(gamepad.get_axis(i) - avg_baseline[i]) > .5:
                print(f'Axis:{i}::{gamepad.get_axis(i)} - {avg_baseline[i]}')
                return STICK, i, None
        # iterate over all gamepad buttons
        for i in range(input_info[1]):  # gamepad.get_numbuttons()):
            if gamepad.get_button(i):
                return BUTTON, i, None
        # iterate over DPad axes and record their value
        for i in range(input_info[2]):  # gamepad.get_numhats()):
            if get_hat_direction_from_tuple(gamepad.get_hat(i)):
                return DPAD, i, get_hat_direction_from_tuple(gamepad.get_hat(i))


def get_pygame_input_array(pygame, gamepad, numaxes, numbuttons, numhats):
    pygame.event.get()
    out_array = []
    # iterate over all gamepad axes
    for i in range(numaxes):
        out_array.append(gamepad.get_axis(i))

    # iterate over all gamepad buttons
    for i in range(numbuttons):
        out_array.append(gamepad.get_button(i))

    # iterate over DPad axes and record their value
    for i in range(numhats):
        out_array.append(get_hat_direction_from_tuple(gamepad.get_hat(i)))

    return out_array


def get_pygamepad_baseline(pygame, gamepad, NUM_SAMPLES=64):
    num_axes = gamepad.get_numaxes()
    num_buttons = gamepad.get_numbuttons()
    num_hats = gamepad.get_numhats()
    buf_size = num_hats + num_buttons + num_axes
    # Setup sample buffer for all inputs
    sample_buf = [[[] for _ in range(buf_size)] for _ in range(NUM_SAMPLES)]
    avg_buffer = [0] * buf_size
    avg_report = [0] * buf_size
    median_report = [0] * buf_size
    mode_report = [0] * buf_size
    range_report = [0] * buf_size

    # Collect data from report
    for i in range(NUM_SAMPLES):
        report = get_pygame_input_array(pygame, gamepad, num_axes, num_buttons, num_hats)
        for j in range(buf_size):
            avg_buffer[j] += report[j]
            sample_buf[i][j] = report[j]

    # Calculate average for each byte index
    # avg_report = [avg_buffer[i] // NUM_SAMPLES for i in range(buf_size)]

    # Calculate median, mode and range and average for each byte
    for j in range(buf_size):
        data = [sample_buf[i][j] for i in range(NUM_SAMPLES)]
        median_report[j] = hfunc.get_median(data)
        mode_report[j] = hfunc.get_mode(data)
        range_report[j] = hfunc.get_range(data)
        avg_report[j] = avg_buffer[j] / NUM_SAMPLES

    return (num_axes, num_buttons, num_hats, buf_size), (avg_report, median_report, mode_report, range_report)


def set_pygame_mapping(pygame, gamepad, buttons: PyGameButtonMapping, input_list: [str]):
    # Default Inputs (all)
    if not input_list:
        input_list = sum([buttons.get_all_stick_button_names(),
                          buttons.get_all_shoulder_button_names(),
                          buttons.get_all_trigger_button_names(),
                          buttons.get_all_thumb_button_names(),
                          buttons.get_all_dpad_button_names(),
                          buttons.get_all_generic_button_names()
                          ], [])

    # Create a dictionary to ensure no input is used twice
    received_input = {}

    # Get Baseline Reading
    global input_info, avg_baseline, median_baseline, mode_baseline, range_baseline
    input_info, baseline_reports = get_pygamepad_baseline(pygame, gamepad)
    num_inputs = input_info[3]
    avg_baseline, median_baseline, mode_baseline, range_baseline = baseline_reports

    #print(hfunc.get_bytes_from_report(hfunc.parse_index_string(f'0-{num_inputs - 1}'), avg_baseline))

    # Map all inputs in input_list
    for input_name in input_list:
        input_type = hfunc.get_input_type(input_name)

        # Prompt the user for input
        print(f"{input_verb(input_type).capitalize()} {format_input_name(input_name)} ...")

        # Wait for no input to be detected
        wait_for_no_pygamepad_input(pygame, gamepad)
        print("OK")

        # Receive updates from the device and map inputs
        setting_input = True
        while setting_input:
            # Receive an input signature
            sig_type, sig_index, sig_value = get_pygamepad_input(pygame, gamepad)
            print("Received")
            # create dictionary key from input
            input_key = (sig_type, sig_index, sig_value)
            if input_key == (None, None, None):
                print(f'<< Input {format_input_name(input_name)} has been skipped! >>')
                setting_input = False
            elif input_key not in received_input:
                received_input[input_key] = True
                setting_input = False
            else:
                print(f'<< That button has already been used! >>')
                # Prompt the user for input
                print(f"{input_verb(input_type).capitalize()} {format_input_name(input_name)} ...")

        # print(f'Set at byte: {hex(sig_type)}  bit: {sig_index} with a value of: {sig_value} \n')
        getattr(buttons, input_name).set(sig_type, sig_index, sig_value)
