import cv2

# ---------------------------------------------------------------- TEMPLATES ----------------------------------------------------------------
# MODAL
BUY_MODAL_IMAGE = cv2.imread('./templates/buy_modal.png') 
SELL_MODAL_IMAGE = cv2.imread('./templates/sell_modal.png') 
BOUGHT_MODAL_IMAGE = cv2.imread('./templates/bought_modal.png')
SOLD_MODAL_IMAGE = cv2.imread('./templates/sold_modal.png')
SOLD_MULTI_MODAL_IMAGE = cv2.imread('./templates/sold_multi_modal.png')
CLOSE_MODAL_IMAGE = cv2.imread('./templates/close_modal.png') 
# RESET_MODAL_IMAGE = cv2.imread('./templates/reset_modal.png') 
# CANCEL_MODAL_IMAGE = cv2.imread('./templates/cancel_modal.png') 

# TRANSACTIONS
HYPHEN_IMAGE = cv2.imread('./templates/hyphen.png') 




# ----------------------------------------------------------------  CAPTURE POSITIONS ----------------------------------------------------------------
# TRANSACTIONS
TRANSACTION_POS = [276, 191, 103, 459]

# ORDER TABLE
ORDER_ROW_POS = [377, 361, 344, 327, 310, 294, 277, 260]

# MODAL STATUS
BUY_MODAL_POS = [847, 257, 27, 17]
SELL_MODAL_POS = [850, 295, 22, 14]
BOUGHT_MODAL_POS = [615, 414, 36, 16]
SOLD_MODAL_POS = [402, 184, 68, 17]
SOLD_MULTI_MODAL_POS = [197, 128, 61, 19]

CLOSE_MODAL_POS = [636, 142, 20, 13]

# PRICE
MAX_PRICE_POS = [896, 312, 142, 20]
MIN_PRICE_POS = [900, 320, 142, 22]


# IN MODAL
IN_BUY_MODAL_NAME_POS = 300, 345, 77, 14
IN_SELL_MODAL_NAME_POS = 300, 375, 77, 14


# ---------------------------------------------------------------- ... ----------------------------------------------------------------
