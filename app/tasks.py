from .celery import app
from app import datetimecalc as dtc
from app import google_calendar
from app import db
from app.models import User, Group
from app.oreluniverAPI import get_schedule_response


@app.task
def add_schedule_event(calendarID, schedule_exercises, oauth2_tokens, overwrite, user_id, islogin):
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
        event = google_calendar.build_calendar_api_token(oauth2_tokens).events().insert(calendarId=calendarID,
                                                                                        body=event).execute()
        if islogin:
            current_user = User.query.filter_by(id=user_id).first()
            if current_user:
                current_user.add_notification(event.get('summary'), "Успешно добавлено событие: \n"
                                              + event.get('htmlLink'))
                db.session.commit()

    return {'status': 'Все события созданы!'}


@app.task()
def add_schedule_periodic():
    users = db.session.query(User).all()

    if users:
        for user in users:
            if db.session.query(db.session.query(Group).filter_by(user_id=user.id).exists()).scalar():
                dbgroup = Group.query.filter_by(user_id=user.id).first()
                weekstart = dtc.current_week_start_ms()
                schedule_exercises = get_schedule_response(dbgroup.idGroup, weekstart)
                if schedule_exercises:
                    task = add_schedule_event.delay(user.lastCalendarID, schedule_exercises, user.oauth2_tokens, True)

# @app.on_after_configure.connect
# def on_after_finalize(sender, **kwargs):
#     sender.add_periodic_task(60.0, add_schedule_periodic.s(), expires=10)

# # Executes every Monday morning at 7:30 a.m.
# sender.add_periodic_task(
#     crontab(hour=7, minute=30, day_of_week=1),
#     test.s('Happy Mondays!'),
# )
