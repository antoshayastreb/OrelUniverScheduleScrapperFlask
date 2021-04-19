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
    if google_auth.is_logged_in() and not current_user.is_anonymous:
        calendar = {
            'summary': 'Расписание занятий',
            'timeZone': 'Europe/Moscow'
        }
        created_calendar = google_calendar.build_calendar_api().calendars().insert(body=calendar).execute()
        print(created_calendar['id'])
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
    calendar = next(item for item in calendar_list['items'] if item['summary'] == calendar_name)
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
        # for key in schedule_item:
        #     schedule_exercise = Exercise(schedule_item['TitleSubject'], schedule_item['TypeLesson'],
        #                                  schedule_item['NumberLesson'], schedule_item['DateLesson'],
        #                                  schedule_item['Korpus'], schedule_item['NumberRoom'],
        #                                  schedule_item['Family'], schedule_item['Name'],
        #                                  schedule_item['SecondName'], schedule_item['link'],
        #                                  schedule_item['pass'], schedule_item['zoom_link'],
        #                                  schedule_item['zoom_password'], )
        #     schedule_exercises.append(schedule_exercise)
    print_student_schedule()


class Exercise:
    def __init__(self, TitleSubject, TypeLesson, NumberLesson, DateLesson, Korpus, NumberRoom, Family, Name,
                 SecondName, link, pas, zoom_link, zoom_password):
        self.TitleSubject = TitleSubject
        self.TypeLesson = TypeLesson
        self.startDateTime = DateLesson + dtc.start_time[NumberLesson]
        self.endDateTime = DateLesson + dtc.start_time[NumberLesson]
        self.Korpus = Korpus
        self.NumberRoom = NumberRoom
        self.Family = Family
        self.Name = Name
        self.SecondName = SecondName
        self.link = link
        self.pas = pas
        self.zoom_link = zoom_link
        self.zoom_password = zoom_password
