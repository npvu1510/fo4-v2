import os
import cv2

# my modules
from winAPi import *

def imageToArr(image):
    return np.array(image)

def saveImage(image, imageName):
    image.save(imageName)


# ---------------------------------------------------------------- CALCULATION FUNCTIONS ----------------------------------------------------------------
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


# ---------------------------------------------------------------- TEST FUNCTIONS ----------------------------------------------------------------
def captureTemplate(position, templateName):
    template = capture_window_region(TARGET_WINDOW, position[0], position[1], position[2], position[3])
    saveImage(template, f"./templates/{templateName}")


def testImage(position, template = None):
    threshold = 50
    prevImage = False

    while True:
        currentImage = capture_window_region(TARGET_WINDOW, position[0], position[1], position[2], position[3])
        # saveImage(currentImage, 'currentImage.png')
        if template.any():
            isAppear = not compareImage(template, imageToArr(currentImage), threshold=threshold, showDiff=False)
            if isAppear:
                print("Xuất hiện")
            else:
                print("Biến mất")

        else:
            if prevImage:
                isChange = compareImage(imageToArr(prevImage), imageToArr(currentImage), threshold=threshold, showDiff=False)
                if isChange:
                    print("Thay đổi")
                    time.sleep(2)
                    os.system('cls')
        
            prevImage = currentImage
        # time.sleep(0.15)
