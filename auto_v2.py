import os
import time
import cv2
# import playsound

# my modules
from constants import *
from utils import *
from timeCheck import  isResetTime_v2, toResetTime


# ---------------------------------------------------------------- OTHERS ----------------------------------------------------------------
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


# def checkSpamError():
#     error = capture_window_region(TARGET_WINDOW, 562, 335, 485, 284)
    
#     if not compareImage(SPAM_ERROR_IMAGE, imageToArr(error), threshold=120):
#         time.sleep(120)
#         single_click(TARGET_WINDOW, 905, 590)
#         return True
    
#     return False


# ---------------------------------------------------------------- FAVORORITES FUNCTIONS ----------------------------------------------------------------
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


# ---------------------------------------------------------------- TRANSACTION FUNCTIONS ----------------------------------------------------------------
def waitModal_v3(status='open', timeout = 20):
    threshold = 25

    startCountdown = time.time()
    while True:
        if time.time() - startCountdown >= timeout:
            return False
        if status == 'open':
            if not compareImage(BUY_MODAL_IMAGE, imageToArr(capture_window_region(TARGET_WINDOW, BUY_MODAL_POS[0], BUY_MODAL_POS[1], BUY_MODAL_POS[2], BUY_MODAL_POS[3])), threshold=threshold, showDiff=False):
                return 'buy'
            if not compareImage(SELL_MODAL_IMAGE, imageToArr(capture_window_region(TARGET_WINDOW,  SELL_MODAL_POS[0], SELL_MODAL_POS[1], SELL_MODAL_POS[2], SELL_MODAL_POS[3])), threshold=threshold, showDiff=False):
                return 'sell'
            if not compareImage(BOUGHT_MODAL_IMAGE, imageToArr(capture_window_region(TARGET_WINDOW,  BOUGHT_MODAL_POS[0], BOUGHT_MODAL_POS[1], BOUGHT_MODAL_POS[2], BOUGHT_MODAL_POS[3])), threshold=threshold, showDiff=False):
                return 'bought'
            if not compareImage(SOLD_MODAL_IMAGE, imageToArr(capture_window_region(TARGET_WINDOW,  SOLD_MODAL_POS[0], SOLD_MODAL_POS[1], SOLD_MODAL_POS[2], SOLD_MODAL_POS[3])), threshold=threshold, showDiff=False) or not compareImage(SOLD_MULTI_MODAL_IMAGE, imageToArr(capture_window_region(TARGET_WINDOW,  SOLD_MULTI_MODAL_POS[0], SOLD_MULTI_MODAL_POS[1], SOLD_MULTI_MODAL_POS[2], SOLD_MULTI_MODAL_POS[3])), threshold=threshold, showDiff=False):
                return 'sold'
            
        elif status == 'close':
            if not compareImage(CLOSE_MODAL_IMAGE, imageToArr(capture_window_region(TARGET_WINDOW, CLOSE_MODAL_POS[0], CLOSE_MODAL_POS[1], CLOSE_MODAL_POS[2], CLOSE_MODAL_POS[3])), threshold=threshold, showDiff=False):
                return True  
    # time.sleep(0.25)


def reBuy():
    # Click vào giá
    single_click(TARGET_WINDOW, 1031, 322)

    # Click mua
    single_click(TARGET_WINDOW, 830, 586)

    # Lưu kết quả
    saveImage(capture_window(TARGET_WINDOW), f'updated_{time.time()}.png')


def findPlayerIndex(playerName, players):
    for i in range(len(players)):
        if players[i]:
            if not compareImage(imageToArr(players[i]['name']), imageToArr(playerName), threshold=100):
                return i
    return -1


def buyMaxOnTransaction_v3(prevPrice):
    resetFlag = False

    currentPrice = capture_window_region(TARGET_WINDOW, MAX_PRICE_POS[0], MAX_PRICE_POS[1], MAX_PRICE_POS[2], MAX_PRICE_POS[3])

    if prevPrice:
        # print('Thay đổi giá: ')
        # print(compareImage(imageToArr(prevPrice), imageToArr(currentPrice), threshold=100, showDiff=False))
        # time.sleep(5)
        
        if compareImage(imageToArr(prevPrice), imageToArr(currentPrice), threshold=100, showDiff=False):
        # if True:
            isAvailable = isAvailableBuySlot()
            print(f'còn slot' if isAvailable else f'hết slot')
            if isAvailable:
                reBuy()
                print('Cập nhật thành công !!')
            else:
                saveImage(capture_window(TARGET_WINDOW), f'failed_{time.time()}.png')
                single_click(TARGET_WINDOW, 971, 587)
            
            # resetFlag = True

        else:
            print("Chưa reset giá")
    
    else:
        isAvailable = isAvailableBuySlot()
        print(f'còn slot' if isAvailable else f'hết slot')
        if isAvailable:
            reBuy()
            print('Cập nhật thành công !!')

            # resetFlag = True

    
    return currentPrice, resetFlag


def sellMinOnTransaction_v3(prevPrice):
    resetFlag = False

    currentPrice = capture_window_region(TARGET_WINDOW, MIN_PRICE_POS[0], MIN_PRICE_POS[1], MIN_PRICE_POS[2], MIN_PRICE_POS[3])

    if prevPrice:
        # print('Thay đổi giá: ')
        # res = compareImage(imageToArr(prevPrice), imageToArr(currentPrice), threshold=100, showDiff=True)
        # print(res)

        # if res:
        #     saveImage(prevPrice, 'prevPrice.png')
        #     saveImage(prevPrice, 'currentPrice.png')
        #     exit()
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
            
            # resetFlag = True

        else:
            print("Chưa reset giá")
    
    else:
        isAvailable = isAvailableSellSlot()
        print(f'còn slot' if isAvailable else f'hết slot')
        if isAvailable:
            single_click(TARGET_WINDOW, 773, 619)
            print('Cập nhật thành công !!')

            # resetFlag = True

    return currentPrice, resetFlag


def isTransactionChanged(prevTransactions):
    currentTransactions = capture_window_region(TARGET_WINDOW, TRANSACTION_POS[0], TRANSACTION_POS[1], TRANSACTION_POS[2], TRANSACTION_POS[3])
    if prevTransactions == False or compareImage(imageToArr(prevTransactions), imageToArr(currentTransactions), showDiff=False):
        return True, currentTransactions
    return False, currentTransactions


def genTransactionData(numRow):
    newTransactions = []
    changeArr = []

    i = 0
    while i < numRow:
        # Cancel timeout modal đợt trước
        # send_key(TARGET_WINDOW, KEY_CODES['ESC'])
        # time.sleep(0.5)
        
        # Click đăng ký lại và xác định loại modal
        single_click(TARGET_WINDOW, 1000, 212 + i * 42, hover=True)
        modalType = waitModal_v3(status='open')

        if not modalType:
            # saveImage(capture_window(TARGET_WINDOW), f'timeout_{time.time()}.png')
            # error = checkSpamError()            
            # if error:
            #     time.sleep(60)
            continue
        
        # xác định vị trí player name của loại modal hiện tại
        if modalType == 'buy':
            prevPrice, isReset = buyMaxOnTransaction_v3(False)
            newTransactions.append({'prevPrice': prevPrice,'isReset': isReset, 'resetTime': False})
    
        elif modalType =='sell':
            prevPrice, isReset = sellMinOnTransaction_v3(False)
            newTransactions.append({'prevPrice': prevPrice,'isReset': isReset, 'resetTime': False})
        else:
            newTransactions.append(False)
        
        # ĐÓNG MODAL
        if modalType == 'buy':
            single_click(TARGET_WINDOW, 971, 587)
        elif modalType == 'sell':
            single_click(TARGET_WINDOW,  908, 617)
        else:
            send_key(TARGET_WINDOW, KEY_CODES['ESC'])
        

        # CHỜ ĐÓNG MODAL
        isClosed = waitModal_v3(status='close')
        if not isClosed:
            saveImage(capture_window(TARGET_WINDOW), f'timeout_{time.time()}.png')
            if modalType == 'buy':
                if not newTransactions[i]['isReset']:
                    single_click(TARGET_WINDOW, 971, 587)
            else:
                if not newTransactions[i]['isReset']:
                    single_click(TARGET_WINDOW,  908, 617)
            waitModal_v3(status='close')
        time.sleep(0.25)
        i+=1

    # print('TRACKING')
    # print(changeArr)
    return newTransactions


def runOnTransactions_v3(numRow=4, resetTime=None):
    prevTransactions = False
    transactions = []

    i = 0
    while True:
        # GIỚI HẠN SỐ LƯỢNG GIAO DỊCH
        if i == numRow:
            i = 0
            # print('SORTED TRANACTIONS')
            # print(transactions)

            # print('Đang chờ thay đổi transaction')
            # time.sleep(5)

            # transactions = sortTransactions(transactions)
            os.system('cls')
        
        # KIỂM TRA TRANSACTION CÓ XẢY RA THAY ĐỔI KHÔNG ?
        # SAU ĐÓ LƯU DỮ LIỆU TRANSACTION
        res, prevTransactions = isTransactionChanged(prevTransactions)
        if res:
            print("🔁 Đang cập nhật danh sách giao dịch..")
            transactions = genTransactionData(numRow)

            os.system('cls')

        # CHỈ CHO PHÉP MUA HOẶC BÁN
        if not transactions[i]:
            i+=1
            continue

        # KIỂM TRA TỚI GIỜ RESET CHƯA ?
        

        # KIỂM TRA CẦU THỦ ĐÃ RESET GIÁ TRONG ĐỢT RESET NÀY HAY CHƯA ?

        # ĐĂNG KÝ LẠI, CHỜ MODAL MỞ VÀ XÁC ĐỊNH LOẠI MODAL
        single_click(TARGET_WINDOW, 1000, 212 + i * 42, hover=True)
        modalType = waitModal_v3(status='open')
        # print(modalType)

        if not modalType:
            # saveImage(capture_window(TARGET_WINDOW), f'timeout_{time.time()}.png')
            continue
        
        # print(transactions)
        # Thực hiện chức năng chính và đóng modal
        if  modalType == 'buy':
            print(f"💵 Mua cầu thủ #{i+1}")
            transactions[i]['prevPrice'], transactions[i]['isReset'] = buyMaxOnTransaction_v3(transactions[i]['prevPrice'])

            if not transactions[i]['isReset']:
                single_click(TARGET_WINDOW, 971, 587)
        else:
            print(f"🤑 Bán cầu thủ #{i+1}")
            transactions[i]['prevPrice'], transactions[i]['isReset'] = sellMinOnTransaction_v3(transactions[i]['prevPrice'])

            if not transactions[i]['isReset']:
                single_click(TARGET_WINDOW,  908, 617)

        # ĐÓNG MODAL
        if modalType == 'buy':
            single_click(TARGET_WINDOW, 971, 587)
        elif modalType == 'sell':
            single_click(TARGET_WINDOW,  908, 617)
        else:
            send_key(TARGET_WINDOW, KEY_CODES['ESC'])
        

        # CHỜ ĐÓNG MODAL
        isClosed = waitModal_v3(status='close')
        if not isClosed:
            saveImage(capture_window(TARGET_WINDOW), f'timeout_{time.time()}.png')
            if modalType == 'buy':
                if not transactions[i]['isReset']:
                    single_click(TARGET_WINDOW, 971, 587)
            else:
                if not transactions[i]['isReset']:
                    single_click(TARGET_WINDOW,  908, 617)
            waitModal_v3(status='close')

        # print(transactions)
        # time.sleep(3)

        i+=1


def main():
    # resetTime = [toResetTime("Chẵn 05 - Chẵn 25"), toResetTime("Chẵn 41 - Lẻ 01"), toResetTime("Chẵn 11 - Chẵn 31"), toResetTime("Chẵn 18 - Chẵn 38"), toResetTime("Chẵn 06 - Chẵn 26")]
    # runOnTransactions_v2(buyMaxOnTransaction, 'buy', len(resetTime), resetTime)
    runOnTransactions_v3()

    # NEW TEMPLATE
    # captureTemplate([896, 312, 142, 20], 'max_price.png')
    # captureTemplate([900, 320, 142, 20], 'min_price.png')
    
    # TEST
    # testImage([962, 315, 77, 54], BUY_MODAL_IMAGE)

    
    pass


if __name__ == '__main__':
    main()
