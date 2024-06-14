import autoit
import keyboard

from python_imagesearch.imagesearch import *




def get_mouse_relative_coordinates(window_title):
    prev_x = None
    prev_y = None
    while True:
        # Lấy vị trí của chuột
        mouse_x, mouse_y = pyautogui.position()

        # Lấy thông tin về cửa sổ hiện tại
        window_info = autoit.win_get_pos(window_title)

        if window_info:
            # Tính toán vị trí tương đối
            relative_x = mouse_x - window_info[0]
            relative_y = mouse_y - window_info[1]

            if keyboard.is_pressed('F1'):
                # In vị trí tương đối
                print(f"TUYỆT ĐỐI: {mouse_x}, {mouse_y}")

                if not prev_x:
                    print(f"TƯƠNG ĐỐI: {relative_x}, {relative_y}")
                else:
                    print(f"TƯƠNG ĐỐI: {relative_x}, {relative_y},{relative_x - prev_x}, {relative_y - prev_y}")
                
                prev_x = relative_x
                prev_y = relative_y

                print("\n")

                time.sleep(0.5)


get_mouse_relative_coordinates("FC ONLINE")


