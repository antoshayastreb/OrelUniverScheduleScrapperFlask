import flask

from app import app, db, google_calendar, google_auth
from flask import render_template, request, jsonify, make_response, redirect, url_for, session
import ast
import requests
from app import datetimecalc as dtc
import json
from flask_login import current_user, login_user, login_required, logout_user
from app.models import User

base_request = 'http://oreluniver.ru/schedule/'


@app.route('/')
@app.route('/index')
def index():
    # if google_auth.is_logged_in() and not current_user.is_anonymous:
    #     calendar = {
    #         'summary': 'Расписание занятий',
    #         'timeZone': 'Europe/Moscow'
    #     }
    #     created_calendar = google_calendar.build_calendar_api().calendars().insert(body=calendar).execute()
    #     print(created_calendar['id'])
    #     calendar_list = google_calendar.build_calendar_api().calendarList().list().execute()
    #     for calendar_list_entry in calendar_list['items']:
    #         print(calendar_list_entry['summary'])
    session['current_weekstart'] = dtc.current_week_start_ms()

    return render_template('index.html', divisions=get_divisionlist())


@app.route('/get_kurslist', methods=['POST'])
def get_kourselist():
    division_id = request.form['division_id']
    kurslist_request = base_request + str(division_id) + '/' + 'kurslist'
    kurslist_response = ast.literal_eval(requests.get(kurslist_request).text)
    res = make_response(jsonify({'data': render_template('kurslist.html', kurs_list=kurslist_response)}))
    res.delete_cookie('division_id')
    res.delete_cookie('kurs')
    res.delete_cookie('group')
    res.set_cookie('division_id', division_id)
    return res


@app.route('/get_grouplist', methods=['POST'])
def get_grouplist():
    division_id = request.cookies.get('division_id')
    kurs = request.form['kurs']
    grouplist_request = base_request + str(division_id) + '/' + str(kurs) + '/' + 'grouplist'
    grouplist_response = ast.literal_eval(requests.get(grouplist_request).text)
    res = make_response(jsonify({'data': render_template('grouplist.html', group_list=grouplist_response)}))
    res.set_cookie('kurs', kurs)
    return res


@app.route('/print_student_schedule', methods=['POST'])
def print_student_schedule():
    group = request.form['group']
    weekstart = session.get('current_weekstart')
    schedule_request = base_request + '/' + str(group) + '///' + str(weekstart) + '/printschedule'
    schedule_response = requests.get(schedule_request).json()
    res = make_response(jsonify({'data': render_template('table.html', schedule=schedule_response)}))
    res.set_cookie('group', group)
    return res


def get_divisionlist():
    divisions_request = base_request + 'divisionlistforstuds'

    divisions_response = ast.literal_eval(requests.get(divisions_request).text)

    return divisions_response


@app.route('/write_schedule_to_calendar')
@login_required
def write_schedule_to_calendar():
    if not google_auth.is_logged_in() and not current_user.is_anonymous:
        raise Exception('User must be logged in')

    weekstart = session.get('current_weekstart')
    group = request.cookies.get('group')

    calendar_name = 'Расписание занятий'

    calendar_list = google_calendar.build_calendar_api().calendarList().list().execute()
    calendar = next((item for item in calendar_list['items'] if item['summary'] == calendar_name), None)
    if calendar:
        print(calendar['id'])
    else:
        new_calendar = {
            'summary': calendar_name,
            'timeZone': 'Europe/Moscow'
        }
        calendar = google_calendar.build_calendar_api().calendars().insert(body=new_calendar).execute()
        print(calendar['id'])
    schedule_request = base_request + '/' + str(group) + '///' + str(weekstart) + '/printschedule'
    schedule_response = requests.get(schedule_request).json()

    schedule_exercises = []

    for iteration, schedule_item in schedule_response.items():
        if iteration == 'Authorization':
            pass
        else:
            filtered = ['TitleSubject', 'TypeLesson', 'NumberLesson', 'DateLesson', 'Korpus',
                        'NumberRoom', 'Family', 'Name', 'SecondName', 'link', 'pass', 'zoom_link',
                        'zoom_password']
            res = [schedule_item[key] for key in filtered]
            schedule_exercise = Exercise(res[0], res[1], res[2], res[3], res[4], res[5], res[6],
                                         res[7], res[8], res[9], res[10], res[11], res[12])
            schedule_exercises.append(schedule_exercise)

    for exercise in schedule_exercises:
        event = {
            'summary': exercise.TitleSubject,
            'description': '(' + exercise.TypeLesson + ')\nпреподаватель: ' + exercise.Family + ' '
                           + exercise.Name + ' ' + exercise.SecondName + '\n' + exercise.Korpus + '-' + exercise.NumberRoom +
                           '\nссылка: ' + exercise.link + '\nпароль: ' + exercise.pas + '\nссылка_zoom: ' + exercise.zoom_link +
                           '\nпароль_zoom: ' + exercise.zoom_password,
            'start': {
                'dateTime': exercise.startDateTime,
                'timeZone': 'Europe/Moscow',
            },
            'end': {
                'dateTime': exercise.endDateTime,
                'timeZone': 'Europe/Moscow',
            },
            'reminders': {
                'useDefault': True
            },
        }

        event = google_calendar.build_calendar_api().events().insert(calendarId=calendar['id'], body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))


@app.route('/check_events')
def chek_events():
    weekstart = session.get('current_weekstart')
    calendar_list = google_calendar.build_calendar_api().calendarList().list().execute()
    calendar = next((item for item in calendar_list['items'] if item['summary'] == 'Расписание занятий'), None)
    get_week_events(calendar['id'], weekstart)
    print('aboba')


@app.route('/prepare_calendar_list', methods=['GET'])
@login_required
def prepare_calendar_list():
    page_token = None
    calendar_data = []
    while True:
        calendar_list = google_calendar.build_calendar_api().calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            if '@gmail.com' in calendar_list_entry['summary']:
                calendar_list_entry['summary'] = "Основной"
            calendar_data.append(calendar_list_entry)
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
    if not next((item for item in calendar_list['items'] if item['summary'] == "Расписание занятий"), None):
        new_calendar_entry = {'summary': 'Расписание занятий(Создать новый)'}
        calendar_data.append(new_calendar_entry)
    res = make_response(jsonify({'data': render_template('calendar_select.html', calendar_list=calendar_data)}))
    return res


@app.route('/prepare_for_export', methods=['GET'])
@login_required
def prepare_for_export():
    weekstart = session.get('current_weekstart')
    group = request.cookies.get('group')

    schedule_request = base_request + '/' + str(group) + '///' + str(weekstart) + '/printschedule'
    schedule_response = requests.get(schedule_request).json()

    schedule_exercises = []

    for iteration, schedule_item in schedule_response.items():
        if iteration == 'Authorization':
            pass
        else:
            filtered = ['TitleSubject', 'TypeLesson', 'NumberLesson', 'DateLesson', 'Korpus',
                        'NumberRoom', 'Family', 'Name', 'SecondName', 'link', 'pass', 'zoom_link',
                        'zoom_password']
            res = [schedule_item[key] for key in filtered]
            schedule_exercise = Exercise(res[0], res[1], res[2], res[3], res[4], res[5], res[6],
                                         res[7], res[8], res[9], res[10], res[11], res[12])
            schedule_exercises.append(schedule_exercise)

    response = make_response(
        jsonify({'data': render_template('modal_table.html', calendar_len=len(schedule_exercises))}))
    return response


def get_week_events(calendar_id, week_start):
    week_start = dtc.convert_backUTC(week_start)
    week_end = dtc.get_week_end(week_start)
    print(dtc.get_iso_format(week_start))

    page_token = None
    while True:
        events = google_calendar.build_calendar_api().events().list(calendarId=calendar_id,
                                                                    timeMin=dtc.get_iso_format(week_start),
                                                                    timeMax=dtc.get_iso_format(week_end),
                                                                    pageToken=page_token).execute()
        page_token = events.get('nextPageToken')
        if not page_token:
            break
    return events


class Exercise:
    def __init__(self, TitleSubject, TypeLesson, NumberLesson, DateLesson, Korpus, NumberRoom, Family, Name,
                 SecondName, link, pas, zoom_link, zoom_password):
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
