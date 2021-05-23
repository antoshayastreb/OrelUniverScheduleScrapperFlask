from .celery import app
from app import datetimecalc as dtc
from app import google_calendar
from app import db
from app.models import User, Group
from app.oreluniverAPI import get_schedule_response


@app.task
def add_schedule_event(calendarID, schedule_exercises, oauth2_tokens, overwrite, user_id, islogin,
                       weekstart, subgroup):
    if not schedule_exercises:
        return
    week_start = dtc.convert_back_utc(weekstart)
    week_end = dtc.get_week_end(week_start)
    if calendarID == "new":
        calendar = {
            'summary': 'Расписание занятий',
            'timeZone': 'Europe/Moscow'
        }

        created_calendar = google_calendar.build_calendar_api_token(oauth2_tokens).calendars().insert(
            body=calendar).execute()
        calendarID = created_calendar['id']

    if overwrite:
        page_token = None
        while True:
            events = google_calendar.build_calendar_api_token(oauth2_tokens).events().list(
                calendarId=calendarID,
                timeMin=dtc.get_iso_format(
                    week_start),
                timeMax=dtc.get_iso_format(
                    week_end),
                pageToken=page_token).execute()
            page_token = events.get('nextPageToken')
            if not page_token:
                break

        for event in events['items']:
            if '(занятие)' in event['summary']:
                google_calendar.build_calendar_api_token(oauth2_tokens).events().delete(
                    calendarId=calendarID,
                    eventId=event[
                        'id']).execute()
    count = 0
    for exercise, value in schedule_exercises.items():
        count += 1
        if int(value['NumberSubGruop']) != 0 and int(value['NumberSubGruop']) != int(subgroup):
            pass
        else:
            print(value['TitleSubject'])
            description = ''
            if check_value(value['TypeLesson']):
                description += '(' + str(value['TypeLesson']) + ')\n'
            if check_value(value['NumberSubGruop']) and value['NumberSubGruop'] == int(subgroup):
                description += 'подгруппа: ' + str(value['NumberSubGruop']) + '\n'
            if check_value(value['Family']) or check_value(value['Name']) or check_value(value['SecondName']):
                description += 'преподаватель: '
                if check_value(value['Family']):
                    description += str(value['Family']) + ' '
                if check_value(value['Name']):
                    description += str(value['Name']) + ' '
                if check_value(value['SecondName']):
                    description += str(value['SecondName'])
                description += '\n'
            if check_value(value['Korpus']) and check_value(value['NumberRoom']):
                description += str(value['Korpus']) + '-' + str(value['NumberRoom']) + '\n'
            elif check_value(value['NumberRoom']):
                description += str(value['NumberRoom']) + '\n'
            elif check_value(value['Korpus']):
                description += str(value['Korpus']) + '\n'
            if check_value(value['link']):
                description += 'ссылка: ' + str(value['link']) + '\n'
            if check_value(value['pass']):
                description += 'пароль: ' + str(value['pass']) + '\n'
            if check_value(value['zoom_link']):
                description += 'ссылка_zoom: ' + str(value['zoom_link']) + '\n'
            if check_value(value['zoom_password']):
                description += 'пароль_zoom: ' + str(value['zoom_password']) + '\n'

            event = {
                'summary': '(занятие) ' + str(value['TitleSubject']),
                'description': description,
                'start': {
                    'dateTime': str(value['DateLesson']) + str(dtc.start_time[int(value['NumberLesson'])]),
                    'timeZone': 'Europe/Moscow',
                },
                'end': {
                    'dateTime': str(value['DateLesson']) + str(dtc.end_time[int(value['NumberLesson'])]),
                    'timeZone': 'Europe/Moscow',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }
            event = google_calendar.build_calendar_api_token(oauth2_tokens).events().insert(
                calendarId=calendarID,
                body=event).execute()

    if islogin:
        current_user = User.query.filter_by(id=user_id).first()
        if current_user:
            current_user.add_notification('Успешный экспорт!', "Успешно добавлено" + str(count) + "событий: \n")
            db.session.commit()

    return {'status': 'Все события созданы!'}


@app.task()
def add_schedule_periodic():
    users = User.query.filter_by(auto_insert=True).all()

    if users:
        for user in users:
            if db.session.query(db.session.query(Group).filter_by(user_id=user.id).exists()).scalar():
                dbgroup = Group.query.filter_by(user_id=user.id).first()
                weekstart = dtc.current_week_start_ms()
                schedule_exercises = get_schedule_response(dbgroup.idGroup, weekstart)
                if schedule_exercises:
                    task = add_schedule_event.delay(user.lastCalendarID, schedule_exercises, user.oauth2_tokens,
                                                    True, user.id, False, weekstart,
                                                    dbgroup.subGroup)


# @app.on_after_configure.connect
# def on_after_finalize(sender, **kwargs):
#     sender.add_periodic_task(60.0, add_schedule_periodic.s(), expires=10)

# # Executes every Monday morning at 7:30 a.m.
# sender.add_periodic_task(
#     crontab(hour=7, minute=30, day_of_week=1),
#     test.s('Happy Mondays!'),
# )


def check_value(value):
    return True if value != 'None' and value != '' and value != ' ' and value != 'null' and value is not None else False
