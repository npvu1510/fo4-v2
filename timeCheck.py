import datetime

def getTypeHour(hour):
    return 'chẵn' if hour % 2 == 0 else 'lẻ' 

def adjust_minute(minute, offset, is_start):
    if is_start:
        # Điều chỉnh startMinute lùi lại offset phút
        new_minute = (minute - offset) % 60
        # Kiểm tra nếu đã lùi về giờ trước
        return new_minute, new_minute > minute
    else:
        # Điều chỉnh endMinute tiến lên offset phút
        new_minute = (minute + offset) % 60
        # Kiểm tra nếu đã tiến lên giờ sau
        return new_minute, new_minute < minute



# def isResetTime(startHourType, startMinute, endHourType, endMinute, offset = 0):
#     startMinute, isStartChanged = adjust_minute(startMinute, offset, True)
#     endMinute, isEndChanged = adjust_minute(endMinute, offset, False)

#     if isStartChanged:
#         startHourType = 'chẵn' if startHourType == 'lẻ' else 'lẻ'
#     if isEndChanged:
#         endHourType = 'chẵn' if endHourType == 'lẻ' else 'lẻ'
    
#     # print(f'New resetTime (+-{offset}): {startHourType}-{startMinute} {endHourType}-{endMinute}')

#     # Lấy thời gian hiện tại
#     currentTime = datetime.datetime.now()
#     current_hour = currentTime.hour
#     current_minute = currentTime.minute

#     # Kiểm tra khoảng thời gian
#     # Trường hợp thông thường: startMinute nhỏ hơn hoặc bằng endMinute
#     if startMinute <= endMinute:
#         if getTypeHour(current_hour) == startHourType:
#             return startMinute <= current_minute <= endMinute 

#     # Trường hợp đặc biệt: startMinute lớn hơn endMinute (qua nửa đêm)
#     else:
#         if getTypeHour(current_hour) == startHourType:
#             return current_minute >= startMinute
#         if getTypeHour(current_hour) == endHourType:
#             return current_minute <= endMinute
            
#     return False


def isResetTime_v2(startHourType, startMinute, endHourType, endMinute, offset = 10):
    startMinute, isStartChanged = adjust_minute(startMinute, offset, True)
    endMinute, isEndChanged = adjust_minute(endMinute, offset, False)

    if isStartChanged:
        startHourType = 'chẵn' if startHourType == 'lẻ' else 'lẻ'
    if isEndChanged:
        endHourType = 'chẵn' if endHourType == 'lẻ' else 'lẻ'
    
    # print(f'New resetTime (+-{offset}): {startHourType}-{startMinute} {endHourType}-{endMinute}')

    # Lấy thời gian hiện tại
    currentTime = datetime.datetime.now()
    current_hour = currentTime.hour
    current_minute = currentTime.minute

    # current_hour = 23
    # current_minute = 4

    # Kiểm tra khoảng thời gian
    message = ''
    # Trường hợp thông thường: startMinute nhỏ hơn hoặc bằng endMinute
    # if startMinute <= endMinute:
    if startHourType == endHourType:
        if getTypeHour(current_hour) == startHourType:
            # Chưa tới giờ
            if current_minute < startMinute:
                message = message + f"{current_hour}:{startMinute}"

            # Đã qua giờ
            elif current_minute > endMinute:
                message = message + f"{(current_hour + 2) % 24}:{startMinute}"

            # Đang trong giờ
            else:
                return True
        else:
            message = message + f"{(current_hour + 1) % 24}:{startMinute}"


    # Trường hợp đặc biệt: startMinute lớn hơn endMinute (qua nửa đêm)
    else:
        if getTypeHour(current_hour) == startHourType:
            if current_minute < startMinute:
                message = message + f"{current_hour}:{startMinute}"
            else:
                return True
        
        if getTypeHour(current_hour) == endHourType:
            if current_minute > endMinute:
                message = message + f"{(current_hour + 1) % 24}:{startMinute}"
            else:
                return True
    
    return message

def toResetTime(resetStr):
    split_parts = resetStr.split(' ')
    if len(split_parts) == 2:
        startMinute = int(split_parts[-1].split('-')[0])
        endMinute = int(split_parts[-1].split('-')[1])
        return {'startHourType': split_parts[0].lower(), 'starMinute':  startMinute, 'endHourType': split_parts[0].lower(),  'endMinute': endMinute}
    else:        
        return {'startHourType': split_parts[0].lower(), 'starMinute':  int(split_parts[1]), 'endHourType': split_parts[3].lower(),  'endMinute': int(split_parts[-1])}


