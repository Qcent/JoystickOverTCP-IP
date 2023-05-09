from enum import IntFlag
from ctypes import *


class XBOX_BUTTON(IntFlag):
    """
    XUSB report buttons.
    """
    XBOX_DPAD_UP = 0x0001
    XBOX_DPAD_DOWN = 0x0002
    XBOX_DPAD_LEFT = 0x0004
    XBOX_DPAD_RIGHT = 0x0008
    XBOX_START = 0x0010
    XBOX_BACK = 0x0020
    XBOX_LEFT_THUMB = 0x0040
    XBOX_RIGHT_THUMB = 0x0080
    XBOX_LEFT_SHOULDER = 0x0100
    XBOX_RIGHT_SHOULDER = 0x0200
    XBOX_GUIDE = 0x0400
    XBOX_A = 0x1000
    XBOX_B = 0x2000
    XBOX_X = 0x4000
    XBOX_Y = 0x8000


class XBOX_REPORT(Structure):
    """
    Represents an XINPUT_GAMEPAD-compatible report structure.
    """
    _fields_ = [("wButtons", c_ushort),
                ("bLeftTrigger", c_byte),
                ("bRightTrigger", c_byte),
                ("sThumbLX", c_short),
                ("sThumbLY", c_short),
                ("sThumbRX", c_short),
                ("sThumbRY", c_short)]


def print_xbox_report(report: XBOX_REPORT) -> None:
    print(f"wButtons: {report.wButtons}")
    print(f"bLeftTrigger: {report.bLeftTrigger}")
    print(f"bRightTrigger: {report.bRightTrigger}")
    print(f"sThumbLX: {report.sThumbLX}")
    print(f"sThumbLY: {report.sThumbLY}")
    print(f"sThumbRX: {report.sThumbRX}")
    print(f"sThumbRY: {report.sThumbRY}")
