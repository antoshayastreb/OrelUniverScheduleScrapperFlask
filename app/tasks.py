from .celery import app
from app import datetimecalc as dtc
from app import google_calendar


@app.task
def add_schedule_event(calendarID, schedule_exercises, oauth2_tokens, overwrite):
    total = len(schedule_exercises)
    i = 0

    for exercise, value in schedule_exercises.items():
        print(value['TitleSubject'])
        event = {
            'summary': str(value['TitleSubject']),
            'description': '(' + str(value['TypeLesson']) + ')\nпреподаватель: ' + str(value['Family']) + ' '
                           + str(value['Name']) + ' ' + str(value['SecondName']) + '\n' + str(value['Korpus']) + '-' +
                           str(value['NumberRoom']) +
                           '\nссылка: ' + str(value['link']) + '\nпароль: ' + str(value['pass']) + '\nссылка_zoom: ' +
                           str(value['zoom_link']) +
                           '\nпароль_zoom: ' + str(value['zoom_password']),
            'start': {
                'dateTime': str(value['DateLesson']) + str(dtc.start_time[int(value['NumberLesson'])]),
                'timeZone': 'Europe/Moscow',
            },
            'end': {
                'dateTime': str(value['DateLesson']) + str(dtc.end_time[int(value['NumberLesson'])]),
                'timeZone': 'Europe/Moscow',
            },
            'reminders': {
                'useDefault': True
            },
        }
        event = google_calendar.build_calendar_api_token(oauth2_tokens).events().insert(calendarId=calendarID, body=event).execute()
        # self.update_state(state='PROGRESS',
        #                   meta={'current': i, 'total': total,
        #                         'status': 'Создано событие %s' % (event.get('htmlLink'))})
        i += 1
    return {'current': total, 'total': total, 'status': 'Все события созданы!'}
