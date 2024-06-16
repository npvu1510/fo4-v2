import os
import time
import ctypes
import numpy as np
import cv2
import playsound

from timeCheck import  isResetTime_v2, toResetTime

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

def send_key(hwnd, key_code, justDown=True):
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

def imageToArr(image):
    return np.array(image)

def saveImage(image, imageName):
    image.save(imageName)

def mse(img1, img2, threshold = 0.0):
    h, w = img1.shape
    diff = cv2.subtract(img1, img2)
    err = np.sum(diff**2)
    mse = err/(float(h*w))

    print(mse)
    return mse != threshold, diff

def absDiff(img1, img2, threshold = 30):
    diff = cv2.absdiff(img1, img2)
    _, thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
    

    return np.count_nonzero(thresh) > 0, diff

def compareImage(img1, img2, threshold = 50, showDiff = False):
    img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    isDifferent, diff = absDiff(img1, img2, threshold)

    if showDiff:
        cv2.imshow("difference", diff)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    return isDifferent

def getStatusModal(typeModal = 'buy'):
    if typeModal == 'buy':
        return 'close' if compareImage(BUY_MODAL_IMAGE, imageToArr(capture_window_region(TARGET_WINDOW, 847, 257, 27, 17)), threshold=30, showDiff=False) else 'open'
    else:
        return 'close' if compareImage(SELL_MODAL_IMAGE, imageToArr(capture_window_region(TARGET_WINDOW,  848, 290, 27, 17)), threshold=30, showDiff=False) else 'open'

 
def waitModal(typeModal = 'buy', status = 'open', timeout = 15):
    start = time.time()

    while getStatusModal(typeModal) != status:
        if time.time() - start >= timeout:
            return False
        pass
    # time.sleep(0.25)

    return True


def isAvailableBuySlot():
    # Lấy giá đầu tiên
    initPrice = capture_window_region(TARGET_WINDOW, 930, 500, 106, 30)

    i = 0
    while i < 8:
        # Lấy giá dòng hiện tại
        currentPrice = capture_window_region(TARGET_WINDOW, 576, ORDER_ROW_POS[i], 80, 16)
        
        # Nếu gặp dòng đầu tiên không phải gạch nối
        if compareImage(imageToArr(currentPrice), HYPHEN_IMAGE, showDiff=False, threshold=100):
            break

        i+=1
    
    # Nếu chưa có ai đặt => còn slot
    if i == 8:
        return True
    
    single_click(TARGET_WINDOW , 576, ORDER_ROW_POS[i] + 8)
    time.sleep(0.1)

    currentPrice = capture_window_region(TARGET_WINDOW, 930, 500, 106, 30)

    # Nếu true => còn slot , ngược lại => hết slot
    res = compareImage(imageToArr(initPrice), imageToArr(currentPrice), threshold=100)

    # if res:
    #     saveImage(initPrice, f'init_{time.time()}.png')
    #     saveImage(currentPrice, f'current_{time.time()}.png')

    return res

def isAvailableSellSlot():
    # click gia min nguoi ta dat
    single_click(TARGET_WINDOW, 619, 434)
    time.sleep(0.1)

    # o gia
    firstPic = capture_window_region(TARGET_WINDOW,  770, 444, 264, 28)
    # saveImage(firstPic, 'a1.png')

    # click gia min hien tai
    single_click(TARGET_WINDOW, 1020, 330)
    time.sleep(0.1)

    # o gia
    secondPic = capture_window_region(TARGET_WINDOW,  770, 444, 264, 28)
    # saveImage(secondPic, 'a2.png')

    res = compareImage(imageToArr(firstPic), imageToArr(secondPic), threshold=100)
    return res


# CONSTANTS
TARGET_WINDOW = user32.FindWindowW(None, "FC Online")

BORDER_WIDTH, TITLE_BAR_HEIGHT = get_window_offsets(TARGET_WINDOW)

BUY_MODAL_IMAGE = cv2.imread('buy_modal.png') 
SELL_MODAL_IMAGE = cv2.imread('sell_modal.png') 
CLOSE_MODAL_IMAGE = cv2.imread('close_modal.png') 
RESET_MODAL_IMAGE = cv2.imread('reset_modal.png') 
HYPHEN_IMAGE = cv2.imread('hyphen.png') 
CANCEL_MODAL_IMAGE = cv2.imread('cancel_modal.png') 

ORDER_ROW_POS = [377, 361, 344, 327, 310, 294, 277, 260]

def updateBuy():
    # Click vào giá
    single_click(TARGET_WINDOW, 1031, 322)

    # Click mua
    single_click(TARGET_WINDOW, 830, 586)

    # Lưu kết quả
    saveImage(capture_window(TARGET_WINDOW), f'updated_{time.time()}.png')


def buy(priceType='max', quantity=1):
    # Click vào giá
    if priceType == 'max':
        single_click(TARGET_WINDOW, 831, 586)
        # multi_click(1267, 395, times=2)
        time.sleep(0.05)

    # Set số lượng
    quantity = 10 if quantity > 10 else quantity
    quantity = 1 if quantity < 1 else quantity

    single_click(TARGET_WINDOW,  1004, 453)
    time.sleep(0.1)
    send_key(TARGET_WINDOW, KEY_CODES[str(quantity)])
    time.sleep(0.1)

    # Click để mua
    single_click(TARGET_WINDOW, 831, 586)

    finish_capture = capture_window(TARGET_WINDOW)
    saveImage(finish_capture, f'buy_{time.time()}.png')


# def checkSpamError():
#     error = capture_window_region(TARGET_WINDOW, 562, 335, 485, 284)
    
#     if not compareImage(SPAM_ERROR_IMAGE, imageToArr(error), threshold=120):
#         time.sleep(120)
#         single_click(TARGET_WINDOW, 905, 590)
#         return True
    
#     return False


def runOnTransactions_v2(action, typeModal='buy',numRow=3, resetTime= None):
    prevPrice = [False] * numRow
    isReset = [False] * numRow
    
    i = 0
    start = time.time()
    while True:
        if time.time() - start > 180:
            print("Tam dung tranh spam...")
            time.sleep(15)
            start = time.time()

        # Giới hạn cầu thủ
        if i == numRow:
            i = 0
            os.system('cls')

        # Kiểm tra tới giờ reset chưa ?
        print(f"⚽ Cầu thủ #{i + 1}: ")
        if resetTime and resetTime[i]:
            resetAt = isResetTime_v2(startHourType= resetTime[i]['startHourType'],startMinute= resetTime[i]['starMinute'],endHourType= resetTime[i]['endHourType'],endMinute= resetTime[i]['endMinute'])

            if resetAt != True:
                print(f'Reset vào lúc: {resetAt}')

                isReset[i] = False
                prevPrice[i] = False

                i+=1
                continue

        # Kiểm tra trong đợt reset này, cầu thủ đã reset chưa ?
        if isReset[i]:
            print("Cập nhật rồi !")
            
            i+=1
            continue

        # Mở modal và chờ
        single_click(TARGET_WINDOW, 1000, 212 + i * 42, hover=True)

        isOpened = waitModal(typeModal=typeModal)
        if not isOpened:
            saveImage(capture_window(TARGET_WINDOW), f'timeout_{time.time()}.png')

            # error = checkSpamError()            
            # if error:
            #     time.sleep(60)
            continue

        
        # Chức năng chính
        prevPrice[i], isReset[i] = action(prevPrice[i])

        # Tắt modal
        if typeModal == 'buy':
            single_click(TARGET_WINDOW, 971, 587)
        else:
            single_click(TARGET_WINDOW,  908, 617)
           
        waitModal(typeModal= typeModal, status='close')

        i+=1

def buyMaxOnTransaction(prevPrice):
    resetFlag = False

    currentPrice = capture_window_region(TARGET_WINDOW, 962, 281, 77, 54)

    if prevPrice:
        if compareImage(imageToArr(prevPrice), imageToArr(currentPrice), threshold=100, showDiff=False):
        # if True:
            isAvailable = isAvailableBuySlot()
            print(f'còn slot' if isAvailable else f'hết slot')
            if isAvailable:
                updateBuy()
                print('cap nhat thanh cong')
            else:
                saveImage(capture_window(TARGET_WINDOW), f'failed_{time.time()}.png')
            
            resetFlag = True

        else:
            print("Chưa reset giá")
    
    else:
        isAvailable = isAvailableBuySlot()
        print(f'còn slot' if isAvailable else f'hết slot')
        if isAvailable:
            updateBuy()
            print('cap nhat thanh cong')

            resetFlag = True

    
    return currentPrice, resetFlag


def sellMinOnTransaction(prevPrice):
    resetFlag = False

    currentPrice = capture_window_region(TARGET_WINDOW, 962, 315, 77, 54)

    if prevPrice:
        if compareImage(imageToArr(prevPrice), imageToArr(currentPrice), threshold=100, showDiff=False):
        # if True:
            isAvailable = isAvailableSellSlot()
            print(f'còn slot' if isAvailable else f'hết slot')
            if isAvailable:
                single_click(TARGET_WINDOW, 773, 619)
                print('cap nhat gia ban')
            else:
                saveImage(capture_window(TARGET_WINDOW), f'failed_{time.time()}.png')
            
            resetFlag = True

        else:
            print("Chưa reset giá")
    
    else:
        isAvailable = isAvailableSellSlot()
        print(f'còn slot' if isAvailable else f'hết slot')
        if isAvailable:
            single_click(TARGET_WINDOW, 773, 619)
            print('cap nhat gia ban')

            resetFlag = True

    
    return currentPrice, resetFlag


def buyMaxOnFavorite(prevPrice):
    currentPrice = capture_window_region(TARGET_WINDOW, 962, 281, 77, 54)

    if prevPrice:
        if compareImage(imageToArr(prevPrice), imageToArr(currentPrice), showDiff=False):
        # if True:
            res = isAvailableBuySlot()
            print(f'còn slot' if res else f'hết slot')
            if res:
                buy(quantity=2)

        else:
            print("Chưa reset giá")
    
    else:
        res = isAvailableBuySlot()
        print(f'còn slot' if res else f'hết slot')
        if res:
            buy(quantity=2)

    
    return currentPrice


def updateCurrentPlayerBySwitchTab(row=0, prevPlayer=None):
    single_click(TARGET_WINDOW, 269, 205 + row * 32)
    time.sleep(0.1)

    currentPlayer, timeout = waitForChangePlayer(prevPlayer)
    if timeout:
        return currentPlayer, True
    # time.sleep(0.5)
        
    single_click(TARGET_WINDOW, 669, 149)
    time.sleep(0.1)
    single_click(TARGET_WINDOW, 530, 148)
    time.sleep(1)

    return currentPlayer, False


def waitForChangePlayer(prevPlayer, timeout=10):
    start = time.time()

    currentPlayer = capture_window_region(TARGET_WINDOW, 716, 202, 104, 21)

    while prevPlayer and not compareImage(imageToArr(currentPlayer), imageToArr(prevPlayer)):
        if time.time() - start >= timeout:
            return None, True
        
        currentPlayer = capture_window_region(TARGET_WINDOW, 716, 202, 104, 21)
    
    return currentPlayer, False


# avatar_row = [191, 234, 276, 317, 359, 400, 441, 483, 524, 565, 607]
# def findRowByAvatar(currentAvatar):
#     for i in range(8):
#         avatarAtCurrentRow = capture_window_region(TARGET_WINDOW, 240, avatar_row[i] + 5, 32, 24)

#         saveImage(currentAvatar ,'currentAvatar.png')
#         saveImage(avatarAtCurrentRow ,'avatarAtCurrentRow.png')

#         # exit(0)
#         if not compareImage(imageToArr(currentAvatar), imageToArr(avatarAtCurrentRow), threshold=150):
#             return i


# def getStatusModal(typeModal = 'buy'):
#     if typeModal == 'buy':
#         return 'close' if compareImage(BUY_MODAL_IMAGE, imageToArr(capture_window_region(TARGET_WINDOW, 847, 257, 27, 17)), threshold=30, showDiff=False) else 'open'
#     else:
#         return 'close' if compareImage(SELL_MODAL_IMAGE, imageToArr(capture_window_region(TARGET_WINDOW,  848, 290, 27, 17)), threshold=30, showDiff=False) else 'open'

 
def waitModal_v3(status='open', timeout = 20):
    start = time.time()

    while True:
        if time.time() - start >= timeout:
            return False
        
        if status == 'open':
            if not compareImage(BUY_MODAL_IMAGE, imageToArr(capture_window_region(TARGET_WINDOW, 847, 257, 27, 17)), threshold=30, showDiff=False):
                return 'buy'
            if not compareImage(SELL_MODAL_IMAGE, imageToArr(capture_window_region(TARGET_WINDOW,  848, 290, 27, 17)), threshold=30, showDiff=False):
                return 'sell'
            
        elif status == 'close':
            if not compareImage(CLOSE_MODAL_IMAGE, imageToArr(capture_window_region(TARGET_WINDOW, 636, 142, 20, 13)), threshold=30, showDiff=False):
                return True
            
    # time.sleep(0.25)

    return True

def findPlayerIndex(playerName, players):
    for i in range(len(players)):
        if players[i]:
            if not compareImage(imageToArr(players[i]['name']), playerName, threshold=100):
                return i
    return -1


def buyMaxOnTransaction_v3(prevPrice):
    resetFlag = False

    currentPrice = capture_window_region(TARGET_WINDOW, 962, 281, 77, 54)

    if prevPrice:
        if compareImage(imageToArr(prevPrice), imageToArr(currentPrice), threshold=100, showDiff=False):
        # if True:
            isAvailable = isAvailableBuySlot()
            print(f'còn slot' if isAvailable else f'hết slot')
            if isAvailable:
                updateBuy()
                print('Cập nhật thành công !!')
            else:
                saveImage(capture_window(TARGET_WINDOW), f'failed_{time.time()}.png')
                single_click(TARGET_WINDOW, 971, 587)
            
            resetFlag = True

        else:
            print("Chưa reset giá")
    
    else:
        isAvailable = isAvailableBuySlot()
        print(f'còn slot' if isAvailable else f'hết slot')
        if isAvailable:
            updateBuy()
            print('Cập nhật thành công !!')

            resetFlag = True

    
    return currentPrice, resetFlag


def sellMinOnTransaction_v3(prevPrice):
    resetFlag = False

    currentPrice = capture_window_region(TARGET_WINDOW, 962, 315, 77, 54)

    if prevPrice:
        if compareImage(imageToArr(prevPrice), imageToArr(currentPrice), threshold=100, showDiff=False):
        # if True:
            isAvailable = isAvailableSellSlot()
            print(f'còn slot' if isAvailable else f'hết slot')
            if isAvailable:
                single_click(TARGET_WINDOW, 773, 619)
                print('Cập nhật thành công !!')
            else:
                saveImage(capture_window(TARGET_WINDOW), f'failed_{time.time()}.png')
                single_click(TARGET_WINDOW,  908, 617)
            
            resetFlag = True

        else:
            print("Chưa reset giá")
    
    else:
        isAvailable = isAvailableSellSlot()
        print(f'còn slot' if isAvailable else f'hết slot')
        if isAvailable:
            single_click(TARGET_WINDOW, 773, 619)
            print('Cập nhật thành công !!')

            resetFlag = True

    return currentPrice, resetFlag


def runOnTransactions_v3(numRow=2, resetTime=None):
    players = []
    # countdown = time.time()

    i = 0
    while True:
        # if time.time() - countdown >= 180:
        #     time.sleep(10)
        #     countdown = time.time()

        # Giới hạn cầu thủ
        if i == numRow:
            i = 0
            os.system('cls')

        # Kiểm tra tới giờ reset chưa ?

        # Kiểm tra trong đợt reset này, cầu thủ đã reset chưa ?

        # Mở modal và chờ
        single_click(TARGET_WINDOW, 1000, 212 + i * 42, hover=True)
        modalType = waitModal_v3(status='open')

        if not modalType:
            saveImage(capture_window(TARGET_WINDOW), f'timeout_{time.time()}.png')
            # error = checkSpamError()            
            # if error:
            #     time.sleep(60)
            continue
        

        # Tìm cầu thủ trong danh sách
        playerName = imageToArr(capture_window_region(TARGET_WINDOW, 300, 345, 77, 14)) 
        playerIndex = findPlayerIndex(playerName, players)
        # print(f"Cầu thủ được lưu tại index: {playerIndex}")
        if playerIndex == -1:
            players.append({'name': playerName, 'prevPrice': False, 'isReset': False})
            playerIndex = len(players) - 1
        

        # Thực hiện chức năng chính và đóng modal
        if  modalType == 'buy':
            print(f"💵 Mua cầu thủ #{i+1}")
            players[playerIndex]['prevPrice'], players[playerIndex]['isReset'] = buyMaxOnTransaction_v3(players[playerIndex]['prevPrice'])

            if not players[playerIndex]['isReset']:
                single_click(TARGET_WINDOW, 971, 587)
        else:
            print(f"🤑 Bán cầu thủ #{i+1}")
            players[playerIndex]['prevPrice'], players[playerIndex]['isReset'] = sellMinOnTransaction_v3(players[playerIndex]['prevPrice'])

            if not players[playerIndex]['isReset']:
                single_click(TARGET_WINDOW,  908, 617)

           
        # Chờ đóng modal
        isClosed = waitModal_v3(status='close')
        if not isClosed:
            saveImage(capture_window(TARGET_WINDOW), f'timeout_{time.time()}.png')
            if modalType == 'buy':
                if not players[playerIndex]['isReset']:
                    single_click(TARGET_WINDOW, 971, 587)
            else:
                if not players[playerIndex]['isReset']:
                    single_click(TARGET_WINDOW,  908, 617)
            waitModal_v3(status='close')

        # time.sleep(0.5)
        i+=1







def main():
    # resetTime = [toResetTime("Chẵn 05 - Chẵn 25"), toResetTime("Chẵn 41 - Lẻ 01"), toResetTime("Chẵn 11 - Chẵn 31"), toResetTime("Chẵn 18 - Chẵn 38"), toResetTime("Chẵn 06 - Chẵn 26")]
    # runOnTransactions_v2(buyMaxOnTransaction, 'buy', len(resetTime), resetTime)

    # playerName = capture_window_region(TARGET_WINDOW, 300, 345, 77, 14)

    # closeModal = capture_window_region(TARGET_WINDOW, 636, 142, 20, 13)
    # saveImage(closeModal, 'close_modal.png')

    runOnTransactions_v3(numRow=3)


if __name__ == '__main__':
    main()


# CAPTURE
# HYPHEN 576, 377, 80, 16
# 2 GIO (MUA) 847, 257, 27, 17
# 2 GIO (BAN) 848, 290, 27, 17
# TOTAL 930, 500, 106, 30

# CLICK
# MUA CAU THU 886, 671
# MUA CAU THU (MODAL) 831, 586
# SO LUONG MUA 1004, 453

# HUY 971, 587

# MAXPRICE (BUY MODAL) 1031, 322

# CAU THU YEU THICH 530, 148
# DS CUA BAN 669, 149
# DANH SACH YEU THICH 269, 205 (cach nhau y = 32)