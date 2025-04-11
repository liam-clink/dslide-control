import ctypes
import atexit

performax = ctypes.WinDLL("./PerformaxCom.dll")

# BOOL PERFORMAXCOM_API _stdcall fnPerformaxComFlush(IN HANDLE pHandle);
# BOOL PERFORMAXCOM_API _stdcall fnPerformaxComGetNumDevices(OUT PDWORD lpNumDevices);
# BOOL PERFORMAXCOM_API _stdcall fnPerformaxComGetProductString(IN DWORD dwNumDevices, OUT PVOID lpDeviceString, IN DWORD dwOptions);
# BOOL PERFORMAXCOM_API _stdcall fnPerformaxComOpen(IN DWORD dwDeviceNum, OUT HANDLE *pHandle);
# BOOL PERFORMAXCOM_API _stdcall fnPerformaxComClose(IN HANDLE pHandle);
# BOOL PERFORMAXCOM_API _stdcall fnPerformaxComSetTimeouts(IN DWORD dwReadTimeout, DWORD dwWriteTimeout);
# BOOL PERFORMAXCOM_API _stdcall fnPerformaxComSendRecv(IN HANDLE pHandle, IN PVOID wBuffer, IN DWORD dwNumBytesToWrite, IN DWORD dwNumBytesToRead, OUT PVOID rBuffer);

# Function signatures
performax.fnPerformaxComFlush.restype = ctypes.c_int
performax.fnPerformaxComFlush.argtypes = [ctypes.c_void_p]
performax.fnPerformaxComGetNumDevices.restype = ctypes.c_int
performax.fnPerformaxComGetNumDevices.argtypes = [ctypes.POINTER(ctypes.c_ulong)]
performax.fnPerformaxComGetProductString.restype = ctypes.c_int
performax.fnPerformaxComGetProductString.argtypes = [
    ctypes.c_ulong,
    ctypes.c_char_p,
    ctypes.c_ulong,
]
performax.fnPerformaxComOpen.restype = ctypes.c_int
performax.fnPerformaxComOpen.argtypes = [
    ctypes.c_ulong,
    ctypes.POINTER(ctypes.c_void_p),
]
performax.fnPerformaxComClose.restype = ctypes.c_int
performax.fnPerformaxComClose.argtypes = [ctypes.c_void_p]
performax.fnPerformaxComSetTimeouts.restype = ctypes.c_int
performax.fnPerformaxComSetTimeouts.argtypes = [ctypes.c_ulong, ctypes.c_ulong]
performax.fnPerformaxComSendRecv.restype = ctypes.c_int
performax.fnPerformaxComSendRecv.argtypes = [
    ctypes.c_void_p,
    ctypes.c_char_p,
    ctypes.c_ulong,
    ctypes.c_ulong,
    ctypes.c_char_p,
]


def get_num_devices() -> int:
    """
    Get the number of connected Performax devices
    """
    count = ctypes.c_ulong()
    performax.fnPerformaxComGetNumDevices(ctypes.byref(count))
    return count.value


def set_timeouts(read_timeout: int, write_timeout: int):
    """
    Set the time in milliseconds to wait for reading and writing in milliseconds
    """
    performax.fnPerformaxComSetTimeouts(
        ctypes.c_ulong(read_timeout), ctypes.c_ulong(write_timeout)
    )


class DSlide:
    """
    A class to represent a Newmark D-Slide
    """

    def __init__(self):
        device_count = get_num_devices()
        print(f"Device count: {device_count}")
        self.open_connection(0)
        self.flush()
        set_timeouts(1000, 1000)
        atexit.register(self.close_connection)

    def flush(self):
        """
        Flushes the communication buffer on the PC as well as the USB controller. It
        is recommended to perform this operation right after the communication
        handle is opened
        """
        performax.fnPerformaxComFlush(self.handle)

    def open_connection(self, device_number: int) -> bool:
        """
        Tries to open connection to device at index "device_number"
        Returns true if success
        """
        self.handle = ctypes.c_void_p()
        performax.fnPerformaxComOpen(ctypes.c_ulong(device_number), self.handle)

    def close_connection(self) -> bool:
        """
        Closes connection to the D-Slide
        """
        performax.fnPerformaxComClose(self.handle)

    def send_command(self, command: str) -> str:
        """
        Sends command to the D-Slide and returns the reply
        """
        command_buffer = ctypes.create_string_buffer(command)
        reply_buffer = ctypes.create_string_buffer(64)
        performax.fnPerformaxComSendRecv(
            self.handle,
            command_buffer,
            ctypes.c_ulong(64),
            ctypes.c_ulong(64),
            reply_buffer,
        )
        reply = reply_buffer.value.decode("ascii")
        return reply

    def get_position_index(self) -> int:
        """
        Gets the integer valued index that the stage is currently at.
        This value can be changed either by a move command, or setting the current position.
        """
        return int(self.send_command(b"PX"))

    def set_position_index(self, index: int):
        """
        Does an absolute move to the given index.
        TODO: calculate wait time or figure out how to ask if still moving
        """
        self.send_command(b"X" + str(index).encode("ascii"))
        print(f"Moving to index: {index}")

    def index_to_mm(self, index: int) -> float:
        """
        Convert index value to length in millimeters
        """
        return index * 400 / 1000000

    def mm_to_index(self, mm: float) -> int:
        """
        Convert length in mm to index
        """
        return int(round(mm * 1000000 / 400))

    def stop(self):
        """
        Stops the motor using deceleration
        """
        self.send_command(b"STOP")

    def set_accel_time(self, accel_time_ms: int):
        """
        Set the time it takes to accelerate and decelerate in milliseconds
        """
        self.send_command(b"ACC" + str(accel_time_ms).encode("ascii"))

    def get_accel_time(self) -> int:
        """
        Gets the acceleration time in milliseconds
        """
        return int(self.send_command(b"ACC"))

    def set_move_speed(self, move_speed_hz: int):
        """
        Sets the move speed in index / s
        """
        return int(self.send_command(b"HSPD" + str(move_speed_hz).encode("ascii")))

    def get_move_speed(self) -> int:
        """
        Gets the move speed in index / s
        """
        return int(self.send_command(b"HSPD"))


if __name__ == "__main__":
    test = DSlide()
