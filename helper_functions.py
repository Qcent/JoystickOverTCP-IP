import time
def is_gamepad(device):
    vid = device.get('vendor_id')
    pid = device.get('product_id')
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



def monitor_byte_array(byte_array, inputs):
    """
    Monitor changes in a byte array over time and record which user inputs alter specific bits in the array.

    byte_array: bytearray object to monitor
    inputs: list of user inputs to test
    """

    # Create a dictionary to store the mapping of inputs to byte array indices
    input_map = {}

    for input in inputs:
        # Prompt the user to alter the byte array by the specified input
        print(f"Please alter the byte array using input '{input}' and press Enter:")

        # Determine the indices of the byte array that were altered
        indices = []
        for i in range(len(byte_array)):
            if byte_array[i] != 0:
                indices.append(i)

        # Store the mapping of input to byte array indices in the dictionary
        input_map[input] = indices

    # Create a log file to record changes to the byte array over time
    log_file = open("byte_array_log.txt", "w")

    # Monitor changes to the byte array over time and log them to the file
    while True:
        # Check if any indices have changed since the last loop iteration
        changed_indices = []
        for i in range(len(byte_array)):
            if byte_array[i] != 0:
                if i not in input_map.values():
                    changed_indices.append(i)

        # If any indices have changed, log them to the file
        if len(changed_indices) > 0:
            log_file.write(f"{time.time()}: {' '.join(str(i) for i in changed_indices)}\n")
            log_file.flush()

        # Sleep for 0.25 seconds before checking again
        time.sleep(0.25)

    print("Inputs Saved!")
