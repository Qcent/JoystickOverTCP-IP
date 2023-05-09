import time
import hid
import struct
from ctypes import *
import ctypes


# misc helpers
class FpsLimiter:
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


def time_function(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        print(f"Time taken by {func.__name__}: {end_time - start_time:.6f}s")
        return result
    return wrapper


def get_localtime():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())


def get_input_type(s):
    s = s.lower()
    if "dpad" in s:
        return 4
    elif "trigger" in s:
        return 3
    elif "stick" in s:
        return 2
    elif "button" in s:
        return 1
    else:
        return 0


def encode_string_to_hex(s: str) -> str:
    """
    Encodes a string into a hex value.

    Returns:
        A hex value representing the encoded string.
    """
    encoded = s.encode()
    return encoded.hex()


def decode_hex_to_string(hex_str: str) -> str:
    """
    Decodes a hex value into a string.

    Returns:
        The original string that was encoded into the hex value.
    """
    decoded = bytes.fromhex(hex_str)
    return decoded.decode()


def get_hidmap_input_lists(buttons, input_list):
    stick_list = list(
        set(buttons.get_all_stick_button_names()).intersection(set(input_list)))  # Only sticks that have been set
    trigger_list = list(
        set(buttons.get_all_trigger_button_names()).intersection(set(input_list)))  # Only triggers that have been set
    button_list = unique_values(input_list, sum([stick_list, trigger_list], []))  # all other set inputs
    return stick_list, trigger_list, button_list


# Network data packaging
def pack_bytearray(data: bytearray) -> bytes:
    return struct.pack(f"{len(data)}B", *data)


def unpack_bytearray(fmt: str, data: bytes) -> bytearray:
    # Usage :
    # unpacked_data = unpack_bytearray(f"{len(my_data)}B", packed_data)
    return bytearray(struct.unpack(fmt, data))


def package_xbox_report(report):
    # Create a format string that matches the XBOX_REPORT structure
    fmt = "<Hbbhhhh"
    # Pack the report fields into a byte string
    data = struct.pack(fmt, report.wButtons, report.bLeftTrigger,
                       report.bRightTrigger, report.sThumbLX, report.sThumbLY,
                       report.sThumbRX, report.sThumbRY)
    return data


# @time_function
def unpack_xbox_report(data):
    # Create a format string that matches the XBOX_REPORT structure
    fmt = "<Hbbhhhh"
    # Unpack the byte string into individual fields
    fields = struct.unpack(fmt, data)
    # Create an XBOX_REPORT instance with the unpacked fields
    return fields
    # report = XBOX_REPORT(*fields)
    # return report


# @time_function
def byte_array_to_ds4_report_ex(byte_array, ds4_report_ex):
    if len(byte_array) < ctypes.sizeof(ds4_report_ex):
        byte_array += bytearray(ctypes.sizeof(ds4_report_ex) - len(byte_array))
    ctypes.memmove(ctypes.addressof(ds4_report_ex), byte_array, ctypes.sizeof(ds4_report_ex))
    #return ds4_report_ex


# hid/pygame input selection
def select_pygame_device(pygame, auto_select=0, other=False):
    # find all connected joystick devices
    pygame.joystick.init()
    joystick_count = pygame.joystick.get_count()
    print(f"Found {joystick_count} joystick devices")

    if joystick_count == 0:
        return None
    if joystick_count == 1 or auto_select == 1:
        joystick_index = 0
    else:
        # Prompt the user to select from a list of connected devices
        print("Select a joystick device:")
        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            print(f"{i}: {joystick.get_name()}")
        if other:
            print(f"{joystick_count + 1}: {other}")

        joystick_index = int(input("Enter joystick index: "))
    if joystick_index == joystick_count + 1:
        return -1
    joystick = pygame.joystick.Joystick(joystick_index)
    joystick.init()
    print(f"Using joystick '{joystick.get_name()}'")

    return joystick


def select_hid_device(devices, auto_select=0, other=False):
    if len(devices) == 0:
        return None, None, None
    if len(devices) == 1 or auto_select == 1:
        device_index = 0
    else:
        if other:
            devices.append({
                'manufacturer_string': other,
                'product_string': '',
                'vendor_id': None,
                'product_id': None
            })
        # Prompt the user to select an HID device from a list of devices provided
        print('Select a Gamepad:')
        for i, device in enumerate(devices):
            print(f'{i}: {device["manufacturer_string"]} {device["product_string"]}')
        device_index = int(input('Enter device index: '))
    device_info = devices[device_index]
    if device_info['vendor_id'] is None and device_info['product_id'] is None:
        return -1, device_info['vendor_id'], device_info['product_id']
    device = hid.device()
    device.open(device_info['vendor_id'], device_info['product_id'])
    print(f"Using joystick '{device_info['product_string']}'")

    return device, device_info['vendor_id'], device_info['product_id']


# hid report sampling
def get_data_stream_reports(device, NUM_SAMPLES=64):
    report_size = 64
    first_report = device.read(report_size)
    report_size = len(first_report)
    sample_buf = [[[] for _ in range(report_size)] for _ in range(NUM_SAMPLES)]
    avg_buffer = [0] * report_size

    avg_report = bytearray([0] * report_size)
    median_report = bytearray([0] * report_size)
    mode_report = bytearray([0] * report_size)
    range_report = bytearray([0] * report_size)

    # Collect data from report
    for i in range(NUM_SAMPLES):
        report = device.read(report_size)
        for j in range(report_size):
            avg_buffer[j] += int(report[j])
            sample_buf[i][j] = report[j]

    # Calculate average for each byte index
    avg_report = bytearray([avg_buffer[i] // NUM_SAMPLES for i in range(report_size)])

    # Calculate median, mode and range for each byte
    for j in range(report_size):
        data = [sample_buf[i][j] for i in range(NUM_SAMPLES)]
        median_report[j] = get_median(data)
        mode_report[j] = get_mode(data)
        range_report[j] = get_range(data)

    return first_report, avg_report, median_report, mode_report, range_report


def get_data_stream_mode(device, NUM_SAMPLES=64):
    report_size = 64
    first_report = device.read(report_size)
    report_size = len(first_report)
    sample_buf = [[[] for _ in range(report_size)] for _ in range(NUM_SAMPLES)]
    mode_report = bytearray([0] * report_size)

    # Collect data from report
    for i in range(NUM_SAMPLES):
        report = device.read(report_size)
        for j in range(report_size):
            sample_buf[i][j] = report[j]

    # Calculate mode for each byte
    for j in range(report_size):
        data = [sample_buf[i][j] for i in range(NUM_SAMPLES)]
        mode_report[j] = get_mode(data)

    return mode_report


def get_data_stream_range(device, NUM_SAMPLES=64):
    report_size = 64
    first_report = device.read(report_size)
    report_size = len(first_report)
    sample_buf = [[[] for _ in range(report_size)] for _ in range(NUM_SAMPLES)]
    range_report = bytearray([0] * report_size)

    # Collect data from report
    for i in range(NUM_SAMPLES):
        report = device.read(report_size)
        for j in range(report_size):
            sample_buf[i][j] = report[j]

    # Calculate range for each byte
    for j in range(report_size):
        data = [sample_buf[i][j] for i in range(NUM_SAMPLES)]
        range_report[j] = get_range(data)

    return range_report


# list and bytearray helper functions
def get_median(data):  # the middle value
    data.sort()
    n = len(data)
    if n % 2 == 0:
        return (data[n // 2 - 1] + data[n // 2]) // 2
    else:
        return data[n // 2]


def get_mode(data):  # most common value
    freq_dict = {}
    for x in data:
        freq_dict[x] = freq_dict.get(x, 0) + 1
    mode = None
    max_freq = 0
    for x, freq in freq_dict.items():
        if freq > max_freq:
            mode = x
            max_freq = freq
    return mode


def get_range(data):
    return max(data) - min(data)


def unique_values(list1, list2):
    unique_values = []
    for value in list1:
        if value not in list2 and value not in unique_values:
            unique_values.append(value)
    for value in list2:
        if value not in list1 and value not in unique_values:
            unique_values.append(value)
    return unique_values


def find_values_in(lst, condition):
    threshold = condition[1:]
    if condition[0] == '<':
        return [i for i, val in enumerate(lst) if val < int(threshold)]
    elif condition[0] == '>':
        return [i for i, val in enumerate(lst) if val > int(threshold)]
    elif condition[0] == '~':
        about, rng = map(int, threshold.split("/"))
        return [i for i, val in enumerate(lst) if abs(val - about) <= rng]
    else:
        return []


def get_diff_in_bytearrays(bytearray1: bytearray, bytearray2: bytearray, ignore_indices=[int]) -> []:
    result = []
    for i in range(len(bytearray1)):
        if i in ignore_indices:
            continue
        if bytearray1[i] != bytearray2[i]:
            result.append({
                'index': i,
                'first_value': bytearray1[i],
                'second_value': bytearray2[i]
            })
    return result


def get_bits_different(a: int, b: int, bits=8) -> [int]:
    # convert the integers to 8-bit(default) binary strings with leading zeros
    a_bin = bin(a)[2:].zfill(bits)
    b_bin = bin(b)[2:].zfill(bits)

    # find the number of differing bits
    diff_indices = []
    for i in range(bits):
        if a_bin[i] != b_bin[i]:
            diff_indices.append(bits - 1 - i)

    return diff_indices


def get_bit_value(arr, byte_offset, bit_offset):
    byte_value = arr[byte_offset]
    mask = 1 << bit_offset
    return (byte_value & mask) >> bit_offset


# some data unit conversion
def byte_to_c_byte(byte_value: int) -> c_byte:
    """
    Scale a value from 0-255 to a c_byte value between -128 and 127.
    """
    # Convert the byte value to a signed integer value in the range [-128, 127]
    signed_value = byte_value - 256 if byte_value > 127 else byte_value

    # Create a c_byte instance with the signed integer value
    cbyte_value = c_byte(signed_value)

    return cbyte_value


def float_to_c_byte(value) -> c_byte:
    """
    Converts a float value in the range [-1, 1] to a c_byte value between -128 and 127.
    """
    if value > 1 or value < -1:
        raise ValueError("Value must be in the range [-1, 1].")

    # Scale the float to the range of -128 to 127
    scaled_value = int(value * 127)

    # Clamp the value within the range of a signed 16-bit integer
    clamped_value = max(-128, min(scaled_value, 127))

    return c_byte(clamped_value)


def byte_to_c_short(byte_value: int) -> c_short:
    """
    Scale a value from 0-255 to a c_short value between -32768 and 32767.
    """
    # Calculate the scaling factor based on the range of possible values
    scaling_factor = 65535 / 255

    # Scale the input value to the range of possible c_short values
    scaled_value = round(byte_value * scaling_factor) - 32768

    return c_short(scaled_value)


def two_bytes_to_c_short(hex_value: bytes) -> c_short:
    """
    Convert a 2-byte hex value to a c_short.
    """
    # Convert the hex value to an integer
    int_value = int.from_bytes(hex_value, byteorder='little', signed=False)

    # Scale the input value to the range of possible c_short values
    scaled_value = round(int_value * 32767 / 32767)

    return c_short(scaled_value)


def float_to_c_short(value):
    """
    Converts a float value in the range [-1, 1] to a c_short value between [-32768, 32767].
    """
    if value > 1 or value < -1:
        raise ValueError("Value must be in the range [-1, 1].")

    # Scale the float to the range of -32768 to 32767
    scaled_value = int(value * 32767)

    # Clamp the value within the range of a signed 16-bit integer
    clamped_value = max(-32768, min(scaled_value, 32767))

    # Convert to a c_short and return
    return c_short(clamped_value)


# probably useless
def is_gamepad(vid, pid):
    controller = identify_controller(vid, pid)
    return True and controller is not False


def identify_controller(vendor_id, product_id):
    controllers = {
        (0x045e, 0x0007): "SideWinder_0007",
        (0x045e, 0x000e): "SideWinder_000e",
        (0x045e, 0x0026): "SideWinderPro",
        (0x045e, 0x0027): "SideWinder_0027",
        (0x045e, 0x0028): "SideWinderDualStrike",
        (0x045e, 0x0202): "XboxControllerUsa_0202",
        (0x045e, 0x0285): "XboxControllerJapan",
        (0x045e, 0x0287): "XboxControllerS_0287",
        (0x045e, 0x0288): "XboxControllerS_0288",
        (0x045e, 0x0289): "XboxControllerUsa_0289",
        (0x045e, 0x028e): "Xbox360Controller",
        (0x045e, 0x0291): "UnlicensedXbox360WirelessReceiver",
        (0x045e, 0x02a0): "Xbox360BigButtonReceiver",
        (0x045e, 0x02a1): "Xbox360WirelessController",
        (0x045e, 0x02d1): "XboxOneController_02d1",
        (0x045e, 0x02dd): "XboxOneController_02dd",
        (0x045e, 0x02e0): "XboxOneSControllerBluetooth_02e0",
        (0x045e, 0x02e3): "XboxOneEliteController_02e3",
        (0x045e, 0x02ea): "XboxOneSControllerUsb",
        (0x045e, 0x02fd): "XboxOneSControllerBluetooth_02fd",
        (0x045e, 0x02ff): "XboxOneEliteController_02ff",
        (0x045e, 0x0719): "Xbox360WirelessReceiver",
        (0x046d, 0xca84): "CordlessXbox",
        (0x046d, 0xca88): "CompactXbox",
        (0x046d, 0xf301): "LogitechXbox360",
        (0x047d, 0x4003): "GravisXterminator",
        (0x047d, 0x4005): "GravisEliminator",
        (0x047d, 0x4008): "GravisDestroyerTiltpad",
        (0x04b4, 0xd5d5): "ZoltrixZBoxer",
        (0x04d9, 0x0002): "TwinShockPs2",
        (0x054c, 0x0268): "Dualshock3Sixaxis",
        (0x054c, 0x05c4): "Dualshock4_05c4",
        (0x054c, 0x05c5): "StrikePackFpsDominator",
        (0x054c, 0x09cc): "Dualshock4_09cc",
        (0x054c, 0x0ba0): "Dualshock4UsbReceiver",
        (0x057e, 0x0306): "Wiimote",
        (0x057e, 0x0330): "WiiUProController",
        (0x057e, 0x0337): "GameCubeControllerAdapter",
        (0x057e, 0x2006): "SwitchJoyConLeft",
        (0x057e, 0x2007): "SwitchJoyConRight",
        (0x057e, 0x2009): "SwitchProController",
        (0x057e, 0x200e): "SwitchJoyConChargingGrip",
        (0x05a0, 0x3232): "8BitdoZero",
        (0x0738, 0x02a0): "MadCatzGamepad_02a0",
        (0x0738, 0x4426): "MadCatzGamepad_4426",
        (0x0738, 0x4506): "MadCatzWirelessXbox",
        (0x16c0, 0x0a99): "SegaJoypadAdapter",
        (0x1bad, 0xf020): "MadCatzMc2",
        (0x1bad, 0xf027): "MadCatzFpsProXbox360",
        (0x1bad, 0xf028): "MadCatzStreetFighterIVFightPadXbox360",
        (0x1bad, 0xf02e): "MadCatzFightPadXbox360",
        (0x1bad, 0xf030): "MadCatzMc2MicroconRacingWheelXbox360",
        (0x1bad, 0xf036): "MadCatzMicroconGamePadProXbox360",
        (0x1bad, 0xfd00): "RazerOnzaTeXbox360",
        (0x1bad, 0xfd01): "RazerOnzaXbox360",
        (0x2002, 0x9000): "8BitdoNes30Pro_9000",
        (0x2563, 0x0547): "ShanWanGamepad",
        (0x2563, 0x0575): "ShanwanPs3PcGamepad",
        (0x25f0, 0x83c1): "GoodbetterbestUsbController",
        (0x25f0, 0xc121): "ShanWanGioteckPs3WiredController",
        (0x2810, 0x0009): "8BitdoSfc30Gamepad",
        (0x28de, 0x0476): "SteamController_0476",
        (0x28de, 0x1102): "SteamController_1102",
        (0x28de, 0x1142): "SteamController_1142",
        (0x28de, 0x11fc): "SteamController_11fc",
        (0x28de, 0x11ff): "SteamVirtualGamepad",
        (0x28de, 0x1201): "SteamController_1201",
        (0x2dc8, 0x1003): "8BitdoN30Arcade_1003",
        (0x2dc8, 0x1080): "8BitdoN30Arcade_1080",
        (0x2dc8, 0x2810): "8BitdoF30_2810",
        (0x2dc8, 0x2820): "8BitdoN30_2820",
        (0x2dc8, 0x2830): "8BitdoSf30_2830",
        (0x2dc8, 0x2840): "8BitdoSn30_2840",
        (0x2dc8, 0x3000): "8BitdoSn30_3000",
        (0x2dc8, 0x3001): "8BitdoSf30_3001",
        (0x2dc8, 0x3810): "8BitdoF30Pro_3810",
        (0x2dc8, 0x3820): "8BitdoNes30Pro_3820",
        (0x2dc8, 0x3830): "Rb864_3830",
        (0x2dc8, 0x6000): "8BitdoSf30Pro_6000",
        (0x2dc8, 0x6001): "8BitdoSn30Pro_6001",
        (0x2dc8, 0x6100): "8BitdoSf30Pro_6100",
        (0x2dc8, 0x6101): "8BitdoSn30Pro_6101",
        (0x2dc8, 0x9000): "8BitdoF30Pro_9000",
        (0x2dc8, 0x9001): "8BitdoNes30Pro_9001",
        (0x2dc8, 0x9002): "Rb864_9002",
        (0x2dc8, 0xab11): "8BitdoF30_ab11",
        (0x2dc8, 0xab12): "8BitdoN30_ab12",
        (0x2dc8, 0xab20): "8BitdoSn30_ab20",
        (0x2dc8, 0xab21): "8BitdoSf30_ab21",
        (0x3820, 0x0009): "8BitdoNes30Pro_0009",
        (0x6666, 0x8804): "SuperJoyBox5ProPs2ControllerAdapter",
        (0x8000, 0x1002): "8BitdoF30Arcade_1002",
        (0x8888, 0x0308): "UnlicensedPs3_0308",
        (0xaa55, 0x0101): "XarcadeToGamepadDevice",
        (0xd209, 0x0450): "JPac",
        (0xf000, 0x0003): "RetroUsbRetroPad",
        (0xf000, 0x0008): "RetroUsbGenesisRetroport",
        (0xf000, 0x00f1): "RetroUsbSuperRetroPort",
        (0xf766, 0x0001): "GreystormPcGamepad"
    }
    return controllers.get((vendor_id, product_id), False)


# The following functions are used by hidCapture.py
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


def get_bytes_from_report(indices, report, items_per_line=16) -> str:
    """
    Returns a string containing the bytes from an HID report that correspond to the provided indices.

    Parameters:
    - indices: A list of integers representing the indices of the bytes to extract from the report.
    - report: A bytes object representing an HID report.

    Returns:
    A string containing the bytes from the report that correspond to the provided indices.
    """
    num_indices = len(indices)
    chunks = [indices[i:i + items_per_line] for i in range(0, num_indices, items_per_line)]
    output = ""

    for i, chunk in enumerate(chunks):
        index_header = " Byte: " + "   ".join([f"{i:02}" for i in chunk])
        value_header = "Value: " + "   ".join([f"{report[i]:02X}" for i in chunk])
        output += f"{index_header}\n{value_header}\n\n"

    return output


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
