import autoit
import pyautogui
import pytesseract
import time
import os

from PIL import ImageGrab, Image
from datetime import datetime, timedelta
from python_imagesearch.imagesearch import *
from playsound import playsound

TRANSACTION_RECT_RELATIVE = (930, 300, 1320, 525)
ORDER_RECT_RELATIVE = (627, 240, 910, 720)
RECEIVE_MONEY_RECT_RELATIVE = (1196, 232, 1382, 282)


def logNotification(emoji, message):
    print(f'{emoji} {message} !')


def logError(message):
    print(f'🔴 {message} !')


def displayWindowInfo(title):
    window_info = autoit.win_get_pos(title)

    # In thông tin vị trí và kích thước cửa sổ
    print(f"Vị trí cửa sổ: {window_info[0]}, {window_info[1]}")
    print(f"Kích thước cửa sổ: {window_info[2]}x{window_info[3]}")


def image_search_relative(img, rect):
    window_info = autoit.win_get_pos("FC ONLINE")
    pos = imagesearcharea(img, rect[0], rect[1], rect[2], rect[3])
    
    if pos[0] != -1:
        # Lấy thông tin về cửa sổ hiện tại
        return (rect[0] + pos[0]  - window_info[0], rect[1] + pos[1] - window_info[1])
    else:
        # print("Không thể lấy thông tin cửa sổ.")
        return False
    

def click_relative(x_relative, y_relative, speed=2):
    # Lấy thông tin về cửa sổ hiện tại
    window_info = autoit.win_get_pos("FC ONLINE")

    if window_info:
        # Tính toán tọa độ tương đối dựa trên vị trí hiện tại của cửa sổ
        x_absolute = window_info[0] + x_relative
        y_absolute = window_info[1] + y_relative

        # Sử dụng mouse_click để click vào tọa độ tương đối
        autoit.mouse_move(0, 0, speed=speed)
        autoit.mouse_click("left", x_absolute, y_absolute, speed=speed)
    else:
        print("Không thể lấy thông tin cửa sổ.")


def ocr_at_position(x_relative, y_relative, width, height, scale = False, currency = True):
    # Lấy thông tin về cửa sổ hiện tại
    window_info = autoit.win_get_pos("FC ONLINE")

    if window_info:
        # Tính toán tọa độ tương đối dựa trên vị trí hiện tại của cửa sổ
        x_absolute = window_info[0] + x_relative
        y_absolute = window_info[1] + y_relative

        # Chụp vùng quanh con trỏ chuột
        screenshot = pyautogui.screenshot(region=(x_absolute, y_absolute, width, height))
        
        if scale != False:
            screenshot = screenshot.resize((round(width * scale), round(height * scale)))

        # screenshot.save('ocr_screenshot.png')

        # Sử dụng pytesseract để chuyển đổi ảnh thành text
        if currency:
            extracted_text = pytesseract.image_to_string(screenshot, lang="eng").strip()
        else:
            extracted_text = pytesseract.image_to_string(screenshot, lang="eng", config='--psm 6 outputbase digits').strip()
        # print(extracted_text)
        
        if not extracted_text:
            return False

        if currency and extracted_text.endswith('8'):
            extracted_text = (extracted_text[:-1] + 'B') 
        return extracted_text.strip()
    else:
        return False


def doubleOCRCheck(x1, y1, w, h, scale = False, currency = True, checkNum = 2):
    results = []

    for _ in range(checkNum):
        result = ocr_at_position(x1, y1, w, h, currency=currency, scale=scale)
        # print(f'Lần ocr {_}: {result}')
        if not result:
            return False
        results.append(result)
    
    for r in results:
        if r != results[0]:
            return False
    
    return results[0]


def convert2AbsRect(rect):
    window_position =  autoit.win_get_pos("FC ONLINE")
    x1 = window_position[0] + rect[0]
    y1 = window_position[1] + rect[1]
    x2 = window_position[0] + rect[2]
    y2 = window_position[1] + rect[3]

    return window_position, (x1, y1, x2, y2)
  

def cleanPriceStr(priceText, padding = False):
    if not padding:
        return  priceText.replace('M','').replace('B','').replace(',','').strip()
    
    return priceText.replace('M','').replace('B','').replace(',','').strip().ljust(3, '0')


def priceStr2Number(priceStr):
    # Loại bỏ ký tự "B" nếu có
    priceStr = cleanPriceStr(priceStr)
    # Chuyển đổi chuỗi thành số
    try:
        priceNumber = float(priceStr)
        return priceNumber
    except ValueError:
        raise Exception('Khong the chuyen doi so')


def takeScreenShot(prefix="", region=(0, 0, 1920, 1080)):
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Tạo tên tệp với thời gian hiện tại
    filename = f"{prefix}_{current_time}.png"
    
    x1, y1, x2, y2 = region[0], region[1], region[2], region[3]
        
    # Chụp khu vực cụ thể
    screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))

    # Lưu ảnh chụp
    screenshot.save(filename)


def waitModalOpen(timeout=30):
    _, transaction_rect_abs = convert2AbsRect(TRANSACTION_RECT_RELATIVE)

    start = time.time()
    while not image_search_relative('transaction-num.png', transaction_rect_abs):
        if time.time() - start >= timeout:
            logNotification('⏰','Timeout !')
            return False
        time.sleep(0.05)

    return True


def waitModalClose(timeout=30):
    _, transaction_rect_abs = convert2AbsRect(TRANSACTION_RECT_RELATIVE)

    start = time.time()
    while image_search_relative('transaction-num.png', transaction_rect_abs):
        if time.time() - start >= timeout:
            logNotification('⏰','Timeout !')
            return False
        time.sleep(0.05)
    return True


def waitForUpdatePrice(timeout = 10):
    time.sleep(0.5)

    start = time.time()
    while True:
        currentPrice =  ocr_at_position(884, 377, 1011-884, 413-377)
        if currentPrice:
            time.sleep(0.15)
            return currentPrice

        if time.time() - start >= timeout:
            logNotification('⏰','Timeout !')
            return False


def isBuy(playerIdx):
    buy = ocr_at_position(1158, 244 + playerIdx * 50 + playerIdx * 2, 35, 37, currency=True)
    if buy == "mua":
        print (f"🔃 MUA cầu thủ thứ #{playerIdx + 1}...")
        return True
    elif buy == "ban":
        print (f"🔃 BÁN cầu thủ thứ #{playerIdx + 1}...")
        return False
    else:
        return -1


def getMaxPrice(buy = True):
    if buy:
        maxPrice = ocr_at_position(1195, 378, 120, 32)
        # print(priceStr2Number(maxPrice))
        # maxPrice = doubleOCRCheck(1195, 378, 120, 32)
    else:
        maxPrice = ocr_at_position(1200, 424, 120, 32)
        # maxPrice = doubleOCRCheck(1200, 424, 120, 32)
    
    if not maxPrice:
        return False
    # print(f"💴 MAX: {maxPrice}".replace('\n', ''))

    try:
        return priceStr2Number(maxPrice)
    except:
        return False


def getMinPrice(buy = False):
    if buy:
        minPrice = ocr_at_position(1192, 345, 105, 32)
        # minPrice = doubleOCRCheck(1192, 345, 105, 32)
    else:
        minPrice = ocr_at_position(1198, 391, 105, 32)
        # minPrice = doubleOCRCheck(1198, 391, 105, 32)
  
    if not minPrice:
        return False
    
    # print(f"💷 MIN: {minPrice}".replace('\n', ''))

    try:
        return priceStr2Number(minPrice)
    except:
        return False
    

def getTotal(buy = True):
    total = ''
    if buy:
        total = ocr_at_position(1148, 616, 128, 42, currency=False)
    else:
        total = ocr_at_position(1220, 586, 69, 25, currency=False)
        # total = doubleOCRCheck(1220, 586, 85, 25, scale=2)

    if not total:
        return False
    return priceStr2Number(total)


def getOrderNum():
    num = ocr_at_position(1170, 709, 26, 18, currency=False)
    return priceStr2Number(num)


def traverseMaxCheck(maxPrice, num):
    logNotification('🔔', 'Vì tổng và giá tối đa bằng nhau, thực hiện vét cạn')
    
    autoit.send('0')
    time.sleep(0.1)
    autoit.send("{BACKSPACE}")


    total = False
    i = 7
    while i >= 0:
        click_relative(770, i * 21 + 326)
        time.sleep(0.15)

        total = getTotal(True)

        # print(num, maxPrice)
        # print(maxPrice * num)
        # print(round(total * num, 3), round(maxPrice * num, 3))
        
        if total and round(total * num, 3) == round(maxPrice * num, 3):
            return False
        i-=1

    return True


def traverseMinCheck(minPrice, num):
    logNotification('🟰', 'Vì giá đề nghị và giá tối thiểu bằng nhau => vét cạn')

    click_relative(770, 532)
    time.sleep(0.15)

    total = getTotal(False)
    # print(total, minPrice)
    
    if total and round(total, 3) == round(num * minPrice, 3):
        return False
      
    return True


def isPriceChanged(prevPrice, currentPrice):
    if prevPrice:
        # print(prevPrice, currentPrice)
        if prevPrice == currentPrice:
            return False
        else:
            # prevPriceArr[row] = currentPrice
            return True
    else:
        logNotification('🥇', 'Chưa có thông tin giao dịch trước đó')
        return True


def isMaxAvailable():
    total = getTotal(True)
    maxPrice = getMaxPrice(True)

    if not total or not maxPrice:
        return (False, total, -1)

    if total != maxPrice:
        return (True, total)
    else:
        re = traverseMaxCheck(maxPrice)
        return (re, total)


def isMinAvailable(prevMinPrice, prevOrder):
    minPrice = getMaxPrice(False)
    total = getTotal(False)
    # print(prevMinPrice, minPrice, total)

    if not minPrice or not total:
        return (False, minPrice, total)
    
    # re = isPriceChanged(prevMinPrice, minPrice, total)
    if not isPriceChanged(prevOrder, total) and not isPriceChanged(prevMinPrice, minPrice):
        return (False, minPrice, total)
    
    if total != minPrice:
        return (True, minPrice, total)
    else:
        # return traverseMinCheck(minPrice)
        re = traverseMaxCheck(minPrice)
        return (re, minPrice, total)


def isNeedUpdate(prevOrder, buy = True, player = True):
    if buy:
        re = isMaxAvailable()
    else:
        re = isMinAvailable(prevOrder)
    return re


def isFirstSlot():
    num = getOrderNum()
    # print(type(num))

    if num == 1:
        return True
    elif num > 1:
        return False


def updateTransaction(buy=True, sound='alert.mp3'):
    # takeScreenShot("before")

    autoit.send('0')
    time.sleep(0.1)
    autoit.send("{BACKSPACE}")

    # Set giá
    if buy:
        click_relative(1292, 395, speed=1)
    else:
        click_relative(1292, 405, speed=1)

    time.sleep(0.1)
    autoit.send("{ENTER}")
    time.sleep(0.1)
    logNotification('✅', 'Cập nhật thành công')
    takeScreenShot("SUCCESS")

    # Các thao tác khác  
    time.sleep(0.5)
    waitModalClose()
    # playsound(sound)    
   

def cancelTransaction(delayAfterCancel = 0.25):
    logNotification('🚫', 'Tắt bảng cập nhật')

    autoit.send("{ESC}")
    time.sleep(delayAfterCancel)


def isFinishedTransaction(playerId):
    rect = (RECEIVE_MONEY_RECT_RELATIVE[0], RECEIVE_MONEY_RECT_RELATIVE[1] + playerId * 50, RECEIVE_MONEY_RECT_RELATIVE[2], RECEIVE_MONEY_RECT_RELATIVE[3] + playerId * 50)
    _, rect_abs = convert2AbsRect(rect)

    return image_search_relative('receive-money.png', rect_abs)


def reOpen(row, buy):
    autoit.send("{ESC}")
    waitModalClose()
    time.sleep(1)

    click_relative(1250, 255 + row * 50 + row * 2)

    if not waitModalOpen(30):
        logError('Mở bảng giao dịch không thành công')
        autoit.mouse_move(10,10)
    time.sleep(0.25)

    price = getMaxPrice(buy) if  buy else getMinPrice(buy)
    total = getTotal(buy)

    return price,total
    

def runOnList(numRow = 1, limit = 4):
    prevPrice = [False] * numRow
    prevTotal = [False] * numRow

    i = 0
    while True:

        # Tắtbảng giao dịch phiên trước nếu còn
        start = time.time()
        while time.time() - start < 0.25:
            # print('close modal')
            autoit.send("{ESC}")
        waitModalClose()
        time.sleep(0.25)

        # if i > 50:
        #     os.system("shutdown /s /t 1")
        

        # Kiểm tra đã giao dịch xong chưa
        if isFinishedTransaction(i):
            logNotification('💰', f"Cầu thủ #{i+1}: đã bán")
            i+=1
            continue

        # Kiểm tra giao dịch là bán hay mua
        buy = isBuy(i)
        if buy == -1:
            logError('Không tìm thấy cầu thủ')
            cancelTransaction()
            i=0
            os.system('cls')
            continue

        if i == limit:
            i=0
            os.system('cls')
            continue   

        # Mở bảng giao dịch
        click_relative(1250, 255 + i * 50 + i * 2)

        if not waitModalOpen(15):
            logError('Mở bảng giao dịch không thành công')
            autoit.mouse_move(10,10)
            continue
        time.sleep(0.25)
    
        try: 
            # numTransactions[i] = 1 if not buy else getNum()
            num = 1 if not buy else getNum()

            # Kiểm tra bảng giao dịch ?
            price = getMaxPrice(buy) if  buy else getMinPrice(buy)
            total = getTotal(buy)


            if not price or not total or not num:
                logError('Gặp lỗi khi lấy dữ liệu')
                continue
                

            if (not prevPrice[i] and not prevTotal[i]) or (prevPrice[i] and prevTotal[i] and prevPrice[i] != price and prevTotal[i] != total):

                price, total = reOpen(i, buy)

                if prevPrice[i] != price and prevTotal[i] != total:
                    print("SL: ", num)
                    print("GIÁ: ", price)    
                    print("TỔNG: ", total)

                    print("GIÁ TRƯỚC ĐÓ: ", prevPrice[i])
                    print("TỔNG TRƯỚC ĐÓ: ", prevTotal[i])
                    

                    if round(price * num, 3) != round(total, 3):
                        re = True
                    else:
                        re = traverseMaxCheck(price, num) if buy else traverseMinCheck(price, num)

                    if re:
                        updateTransaction(buy)

                    else:
                        if prevPrice[i] or prevTotal[i]:
                            takeScreenShot("FAILED")
                            cancelTransaction()

            prevPrice[i] = price
            prevTotal[i] = total

        except: 
            pass

        finally:
            time.sleep(0.1)
            cancelTransaction()

        i+= 1
        print("\n")



def reloadMarket():
    autoit.send('{ESC}')
    time.sleep(0.2)

    click_relative(829, 182)
    time.sleep(0.2)

    click_relative(660, 181)
    time.sleep(0.2)


def getAvgPrice():
    currentPrice = waitForUpdatePrice()

    if currentPrice:
        return currentPrice.strip()
    
    return False


def openModalFromMarket():
    click_relative(1105, 830)
    modal = waitModalOpen(5)  

    if not modal:
        logError('Mở bảng giao dịch không thành công')
        autoit.mouse_move(10,10)
        return False

    time.sleep(0.15)
    return True


# Chuyển tab qua lại để biết giá đã reset chưa, không cần mở modal check, có kiểm tra danh sách order
def runModalWithCheck():
    prevPrice = False
    prevTotal = False
    reOpen = False

    while True:
        # Tải lại dữ liệu
        reloadMarket()

        # Chờ load giá cho chính xác
        waitForUpdatePrice()

        # Mở bảng giao dịch
        modal = openModalFromMarket()
        if not modal:
            continue

        # Kiểm tra bảng giao dịch ?
        maxPrice = getMaxPrice()
        total = getTotal()

        if (not prevPrice and not prevTotal) or (prevPrice != maxPrice or prevTotal != total):
            if total != maxPrice:
                re = True
            else:
                re = traverseMaxCheck(maxPrice)

            if re:
                if not reOpen:
                    # takeScreenShot("before")
                    print("Mở lại để chắc chắn dữ liệu là mới nhất")
                    reOpen = True
                    continue

                updateTransaction()
                reOpen = False

            else:
                if prevPrice and prevTotal:
                    takeScreenShot("FAILED")
                cancelTransaction()

            prevPrice = maxPrice
            prevTotal = total

        print(prevPrice, prevTotal, prevPrice)


def runSwitchTabWithoutCheck():
    buyList = []
    prevAvgPrice = False

    while True:
        # Tải lại dữ liệu
        reloadMarket()

        # Chờ cập nhật và kiểm tra giá trung bình
        avgPrice = getAvgPrice()
        # print(avgPrice, (not prevAvgPrice) or (prevAvgPrice != avgPrice))

        # if not prevAvgPrice or (prevAvgPrice and avgPrice not in buyList and prevAvgPrice != avgPrice):
        if prevAvgPrice and avgPrice not in buyList and prevAvgPrice != avgPrice:
            modal = openModalFromMarket()
            if not modal:
                continue            

            updateTransaction(sound='success.wav')
            buyList.append(avgPrice)
        
        prevAvgPrice = avgPrice
        print(prevAvgPrice)


# Không check danh sách order, cứ reset giá là mua
def runModalWithoutCheck():
    buyList = []
    prevPrice = False
    
    while True:
        # Reset
        autoit.send('{ESC}')
        time.sleep(0.1)

        # Mở bảng giao dịch
        modal = openModalFromMarket()
        if not modal:
            continue

        maxPrice = getMaxPrice()
        # print(maxPrice, prevPrice and maxPrice not in buyList and prevPrice != maxPrice)
        # if not prevPrice or (prevPrice and maxPrice not in buyList and prevPrice != maxPrice):
        if prevPrice and maxPrice not in buyList and prevPrice != maxPrice:
            updateTransaction(sound='success.wav')
            buyList.append(maxPrice)
        else:
            cancelTransaction(delayAfterCancel=0.1)
        print(prevPrice, maxPrice)

        prevPrice = maxPrice


def getNum():
    num = ocr_at_position(1220, 542, 48, 30, currency=False)

    if not num:
        return False
    return priceStr2Number(num)

time.sleep(1)
# runModalWithoutCheck()
# runModalWithCheck()
# runSwitchTabWithoutCheck()
runOnList(numRow=11)


# while True:
#     price = getMaxPrice()
#     print(price)

#     total = getTotal()
#     print(total)

#     num = getNum()
#     print(num)