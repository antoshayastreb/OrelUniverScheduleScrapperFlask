from datetime import datetime
import time


# текущее время в миллисекундах
def current_milli_time():
    return round(time.time() * 1000)


# В js дни недели считаются с вс(0) и заканчиваются сб(6), в питоне с пн(0) и вс(6).
# Таким образом переводим дни недели python в дни недели js.
def get_current_weekday():
    weekday = datetime.now().weekday()
    if weekday == 6:
        return 0
    else:
        return weekday + 1


# Переписанная с JS функция получения времени, я не стал рзбираться как она точно высчитывает и просто переписал на
# Python.
def current_week_start_ms():
    current_week_start = current_milli_time() + 86400000 - 86400000 * get_current_weekday()
    current_week_start = (current_week_start - (utc_offset() * 60000)) - \
                          (3600 * datetime.now().hour + 60 * datetime.now().minute + (1 * datetime.now().second)) * 1000
    return current_week_start


# Возвращает разницу с UTC в минутах
def utc_offset():
    ts = time.time()
    utc_offset = int((datetime.fromtimestamp(ts) -
                      datetime.utcfromtimestamp(ts)).total_seconds() / 60)
    return utc_offset
