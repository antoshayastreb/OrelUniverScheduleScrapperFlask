import ast
from app import datetimecalc as dtc
import requests

base_request = 'http://oreluniver.ru/schedule/'


def get_schedule_response(group, weekstart):
    schedule_request = base_request + '/' + str(group) + '///' + str(weekstart) + '/printschedule'
    schedule_response = requests.get(schedule_request).json()

    schedule_response.pop('Authorization', schedule_response)

    return schedule_response


def get_kurslist(division_id):
    kurslist_request = base_request + str(division_id) + '/' + 'kurslist'
    kurslist_response = ast.literal_eval(requests.get(kurslist_request).text)
    return kurslist_response


def get_grouplist(division_id, kurs):
    grouplist_request = base_request + str(division_id) + '/' + str(kurs) + '/' + 'grouplist'
    grouplist_response = ast.literal_eval(requests.get(grouplist_request).text)
    return grouplist_response


# Получает пары из ответа oreluniver'а
def get_list_of_exercises(group, weekstart):
    schedule_request = base_request + '/' + str(group) + '///' + str(weekstart) + '/printschedule'
    schedule_response = requests.get(schedule_request).json()

    schedule_exercises = []
    if not schedule_response:
        return schedule_exercises
    for iteration, schedule_item in schedule_response.items():
        if iteration == 'Authorization':
            pass
        else:
            filtered = ['TitleSubject', 'TypeLesson', 'NumberLesson', 'DateLesson', 'DayWeek', 'NumberSubGruop',
                        'Korpus', 'NumberRoom', 'Family', 'Name', 'SecondName', 'link', 'pass', 'zoom_link',
                        'zoom_password']
            res = [schedule_item[key] for key in filtered]
            schedule_exercise = Exercise(TitleSubject=res[0], TypeLesson=res[1], NumberLesson=res[2], DateLesson=res[3],
                                         Korpus=res[6], NumberRoom=res[7], Family=res[8], Name=res[9],
                                         SecondName=res[10], link=res[11],
                                         pas=res[12], zoom_link=res[13], zoom_password=res[14], DayWeek=res[4],
                                         NumberSubGruop=res[5])
            schedule_exercises.append(schedule_exercise)

    return schedule_exercises


def get_divisionlist():
    divisions_request = base_request + 'divisionlistforstuds'

    divisions_response = ast.literal_eval(requests.get(divisions_request).text)

    return divisions_response


class Exercise:
    endDateTime = None
    startDateTime = None
    zoom_link = None
    NumberRoom = None
    Korpus = None
    pas = None
    zoom_password = None
    link = None
    Name = None
    SecondName = None
    Family = None
    TypeLesson = None
    TitleSubject = None

    def __init__(self, TitleSubject, TypeLesson, NumberLesson, DateLesson, Korpus, NumberRoom, Family, Name,
                 SecondName, link, pas, zoom_link, zoom_password, DayWeek, NumberSubGruop):
        self.TitleSubject = TitleSubject if TitleSubject is not None else ''
        self.TypeLesson = TypeLesson if TypeLesson is not None else ''
        self.startDateTime = DateLesson + dtc.start_time[NumberLesson]
        self.endDateTime = DateLesson + dtc.end_time[NumberLesson]
        self.Korpus = Korpus if Korpus is not None else ''
        self.NumberRoom = NumberRoom if NumberRoom is not None else ''
        self.Family = Family if Family is not None else ''
        self.Name = Name if Name is not None else ''
        self.SecondName = SecondName if SecondName is not None else ''
        self.link = link if link is not None else ''
        self.pas = pas if pas is not None else ''
        self.zoom_link = zoom_link if zoom_link is not None else ''
        self.zoom_password = zoom_password if zoom_password is not None else ''
        self.NumberLesson = NumberLesson if NumberLesson is not None else ''
        self.DayWeek = DayWeek if DayWeek is not None else ''
        self.NumberSubGruop = NumberSubGruop
