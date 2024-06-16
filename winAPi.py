import ctypes
import time
import numpy as np

from ctypes import wintypes
from PIL import Image, ImageDraw
from random import randrange


KEY_CODES = {
    'A': 0x41,
    'B': 0x42,
    'C': 0x43,
    'D': 0x44,
    'E': 0x45,
    'F': 0x46,
    'G': 0x47,
    'H': 0x48,
    'I': 0x49,
    'J': 0x4A,
    'K': 0x4B,
    'L': 0x4C,
    'M': 0x4D,
    'N': 0x4E,
    'O': 0x4F,
    'P': 0x50,
    'Q': 0x51,
    'R': 0x52,
    'S': 0x53,
    'T': 0x54,
    'U': 0x55,
    'V': 0x56,
    'W': 0x57,
    'X': 0x58,
    'Y': 0x59,
    'Z': 0x5A,
    '0': 0x30,
    '1': 0x31,
    '2': 0x32,
    '3': 0x33,
    '4': 0x34,
    '5': 0x35,
    '6': 0x36,
    '7': 0x37,
    '8': 0x38,
    '9': 0x39,
    'ENTER': 0x0D,
    'ESC': 0x1B,
    'BACKSPACE': 0x08,
    'TAB': 0x09,
    'SPACE': 0x20,
    'LEFT': 0x25,
    'UP': 0x26,
    'RIGHT': 0x27,
    'DOWN': 0x28,
    'F1': 0x70,
    'F2': 0x71,
    'F3': 0x72,
    'F4': 0x73,
    'F5': 0x74,
    'F6': 0x75,
    'F7': 0x76,
    'F8': 0x77,
    'F9': 0x78,
    'F10': 0x79,
    'F11': 0x7A,
    'F12': 0x7B
}


user32 = ctypes.WinDLL('user32', use_last_error=True)
gdi32 = ctypes.WinDLL('gdi32', use_last_error=True)


HWND_BROADCAST = 0xFFFF
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
SRCCOPY = 0x00CC0020



# Định nghĩa các giá trị và hàm cần thiết
# GWL_EXSTYLE = -20
GWL_STYLE = -16
WS_DISABLED = 0x08000000
WS_SYSMENU = 0x00080000
WS_MINIMIZEBOX = 0x00020000
WS_MAXIMIZEBOX = 0x00010000


class MSG(ctypes.Structure):
    _fields_ = [("hwnd", wintypes.HWND),
                ("message", wintypes.UINT),
                ("wParam", wintypes.WPARAM),
                ("lParam", wintypes.LPARAM),
                ("time", wintypes.DWORD),
                ("pt", wintypes.POINT)]

class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ('biSize', wintypes.DWORD),
        ('biWidth', wintypes.LONG),
        ('biHeight', wintypes.LONG),
        ('biPlanes', wintypes.WORD),
        ('biBitCount', wintypes.WORD),
        ('biCompression', wintypes.DWORD),
        ('biSizeImage', wintypes.DWORD),
        ('biXPelsPerMeter', wintypes.LONG),
        ('biYPelsPerMeter', wintypes.LONG),
        ('biClrUsed', wintypes.DWORD),
        ('biClrImportant', wintypes.DWORD)
    ]

class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ('bmiHeader', BITMAPINFOHEADER),
        ('bmiColors', wintypes.DWORD * 3)
    ]

def make_lparam(low, high):
    return (high << 16) | (low & 0xFFFF)

def post_message(hwnd, msg, wparam, lparam):
    user32.PostMessageW(hwnd, msg, wparam, lparam)
    
def get_window_offsets(hwnd):
    rect = wintypes.RECT()
    client_rect = wintypes.RECT()

    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    user32.GetClientRect(hwnd, ctypes.byref(client_rect))

    border_width = (rect.right - rect.left - client_rect.right) // 2
    title_bar_height = rect.bottom - rect.top - client_rect.bottom - border_width

    return border_width, title_bar_height

def draw_point(image, x, y):
    draw = ImageDraw.Draw(image)
    radius = 1  # Điều chỉnh bán kính nhỏ hơn
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill='blue', outline='blue')
    return image

def single_click(hwnd, x, y, hover=False, draw=''):
    click_x = x - BORDER_WIDTH
    click_y = y - TITLE_BAR_HEIGHT

    lparam = make_lparam(click_x, click_y)

    if hover:
        post_message(hwnd, 0x0200, 0, lparam)  # WM_MOUSEMOVE
        time.sleep(0.1)
    
    post_message(hwnd, WM_LBUTTONDOWN, 0, lparam)
    post_message(hwnd, WM_LBUTTONUP, 0, lparam)

    if draw:
        image = capture_window(TARGET_WINDOW)
        image_with_click = draw_point(image, x, y)
        image_with_click.save(draw)

def multi_click(x, y, times=2, rand_x = False, rand_y=False , draw=''):
    i = 0

    while i < times:
        rand_x_val = randrange(rand_x) if rand_x else 0
        rand_y_val = randrange(rand_y) if rand_y else 0

        single_click(TARGET_WINDOW, x + rand_x_val, y + rand_y_val, draw)
        time.sleep(0.01)

        i+=1

def send_key(hwnd, key_code, justDown=False):
    """
    Gửi phím tới cửa sổ cụ thể mà không chiếm quyền kiểm soát chuột
    hwnd: Handle của cửa sổ đích
    key_code: Mã phím cần gửi (VD: 0x41 cho phím 'A')
    """
    lparam = (0x00000001 | (0x00000001 << 16))  # Repeat count và scan code
    post_message(hwnd, 0x0100, key_code, lparam)  # WM_KEYDOWN
    
    if justDown:
        return
    # time.sleep(0.01)  # Thời gian giữ phím
    post_message(hwnd, 0x0101, key_code, lparam)  # WM_KEYUP

def capture_window(hwnd):
    # Lấy DC của cửa sổ
    hdc_window = user32.GetWindowDC(hwnd)
    if not hdc_window:
        raise ctypes.WinError(ctypes.get_last_error())

    hdc_mem_dc = gdi32.CreateCompatibleDC(hdc_window)
    if not hdc_mem_dc:
        user32.ReleaseDC(hwnd, hdc_window)
        raise ctypes.WinError(ctypes.get_last_error())

    # Lấy thông tin về cửa sổ
    rect = wintypes.RECT()
    if not user32.GetClientRect(hwnd, ctypes.byref(rect)):
        gdi32.DeleteDC(hdc_mem_dc)
        user32.ReleaseDC(hwnd, hdc_window)
        raise ctypes.WinError(ctypes.get_last_error())

    width, height = rect.right - rect.left, rect.bottom - rect.top

    # Tạo bitmap tương thích
    hbm = gdi32.CreateCompatibleBitmap(hdc_window, width, height)
    if not hbm:
        gdi32.DeleteDC(hdc_mem_dc)
        user32.ReleaseDC(hwnd, hdc_window)
        raise ctypes.WinError(ctypes.get_last_error())

    gdi32.SelectObject(hdc_mem_dc, hbm)

    # Chụp ảnh từ DC cửa sổ vào DC bộ nhớ
    if not gdi32.BitBlt(hdc_mem_dc, 0, 0, width, height, hdc_window, 0, 0, 0x00CC0020):
        gdi32.DeleteObject(hbm)
        gdi32.DeleteDC(hdc_mem_dc)
        user32.ReleaseDC(hwnd, hdc_window)
        raise ctypes.WinError(ctypes.get_last_error())

    # Khởi tạo cấu trúc BITMAPINFO
    bmi = BITMAPINFO()
    bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = width
    bmi.bmiHeader.biHeight = -height  # top-down
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 24
    bmi.bmiHeader.biCompression = 0  # BI_RGB
    bmi.bmiHeader.biSizeImage = 0
    bmi.bmiHeader.biXPelsPerMeter = 0
    bmi.bmiHeader.biYPelsPerMeter = 0
    bmi.bmiHeader.biClrUsed = 0
    bmi.bmiHeader.biClrImportant = 0

    # Tạo buffer dữ liệu
    data = ctypes.create_string_buffer(width * height * 3)

    # Lấy dữ liệu bitmap
    bits = gdi32.GetDIBits(hdc_mem_dc, hbm, 0, height, data, ctypes.byref(bmi), 0)
    if bits == 0:
        gdi32.DeleteObject(hbm)
        gdi32.DeleteDC(hdc_mem_dc)
        user32.ReleaseDC(hwnd, hdc_window)
        raise ctypes.WinError(ctypes.get_last_error())

    # Giải phóng tài nguyên
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem_dc)
    user32.ReleaseDC(hwnd, hdc_window)

    # Tạo ảnh từ dữ liệu bitmap
    image = Image.frombuffer('RGB', (width, height), data, 'raw', 'BGR', 0, 1)
    return image

def capture_window_region(hwnd, x, y, w, h):
    # Lấy DC của cửa sổ
    hdc_window = user32.GetWindowDC(hwnd)
    if not hdc_window:
        raise ctypes.WinError(ctypes.get_last_error())

    hdc_mem_dc = gdi32.CreateCompatibleDC(hdc_window)
    if not hdc_mem_dc:
        user32.ReleaseDC(hwnd, hdc_window)
        raise ctypes.WinError(ctypes.get_last_error())

    # Căn chỉnh width và height thành bội số của 4
    w = (w + 3) & ~3
    h = (h + 3) & ~3

    # Tạo bitmap tương thích
    hbm = gdi32.CreateCompatibleBitmap(hdc_window, w, h)
    if not hbm:
        gdi32.DeleteDC(hdc_mem_dc)
        user32.ReleaseDC(hwnd, hdc_window)
        raise ctypes.WinError(ctypes.get_last_error())

    gdi32.SelectObject(hdc_mem_dc, hbm)

    # Chụp ảnh từ DC cửa sổ vào DC bộ nhớ
    if not gdi32.BitBlt(hdc_mem_dc, 0, 0, w, h, hdc_window, x, y, 0x00CC0020):
        gdi32.DeleteObject(hbm)
        gdi32.DeleteDC(hdc_mem_dc)
        user32.ReleaseDC(hwnd, hdc_window)
        raise ctypes.WinError(ctypes.get_last_error())

    # Khởi tạo cấu trúc BITMAPINFO
    bmi = BITMAPINFO()
    bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = w
    bmi.bmiHeader.biHeight = -h  # top-down
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 24
    bmi.bmiHeader.biCompression = 0  # BI_RGB
    bmi.bmiHeader.biSizeImage = w * h * 3
    bmi.bmiHeader.biXPelsPerMeter = 0
    bmi.bmiHeader.biYPelsPerMeter = 0
    bmi.bmiHeader.biClrUsed = 0
    bmi.bmiHeader.biClrImportant = 0

    # Tạo buffer dữ liệu
    data = ctypes.create_string_buffer(bmi.bmiHeader.biSizeImage)

    # Lấy dữ liệu bitmap
    bits = gdi32.GetDIBits(hdc_mem_dc, hbm, 0, h, data, ctypes.byref(bmi), 0)
    if bits == 0:
        gdi32.DeleteObject(hbm)
        gdi32.DeleteDC(hdc_mem_dc)
        user32.ReleaseDC(hwnd, hdc_window)
        raise ctypes.WinError(ctypes.get_last_error())

    # Giải phóng tài nguyên
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem_dc)
    user32.ReleaseDC(hwnd, hdc_window)

    # Tạo ảnh từ dữ liệu bitmap
    array = np.frombuffer(data, dtype=np.uint8).reshape((h, w, 3))

    return Image.fromarray(array)


TARGET_WINDOW = user32.FindWindowW(None, "FC Online")
BORDER_WIDTH, TITLE_BAR_HEIGHT = get_window_offsets(TARGET_WINDOW)