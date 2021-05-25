import flask

from app import app, db, google_calendar, google_auth
from app import oreluniverAPI as ouAPI
from flask import render_template, request, jsonify, make_response, redirect, url_for, session
from app import datetimecalc as dtc
import json
from flask_login import current_user, login_user, login_required, logout_user
from app.tasks import add_schedule_event
from app.models import User, Group, Notification


@app.route('/')
@app.route('/index')
def index():
    session['current_weekstart'] = dtc.current_week_start_ms()

    divisions = ouAPI.get_divisionlist()

    res = make_response(render_template('index.html', divisions=divisions))

    res.set_cookie('weekstart', str(dtc.current_week_start_ms()), max_age=60 * 60 * 24)

    if google_auth.is_logged_in() and not current_user.is_anonymous:
        dbGroup = Group.query.filter_by(user_id=current_user.id).first()
        if dbGroup is not None:
            res.set_cookie('group', str(dbGroup.idGroup), max_age=60 * 60 * 24)
            res.set_cookie('subgroup', str(dbGroup.subGroup), max_age=60 * 60 * 24)

    return res


@app.route('/get_divisionlist', methods=['GET'])
def get_divisionlist():
    divisions = ouAPI.get_divisionlist()
    res = make_response(jsonify({'data': render_template('personal_divisionlist.html', divisions=divisions,
                                                         user_division=current_user.division)}))
    return res


@app.route('/get_personalkurslist', methods=['POST'])
def get_personalkurslist():
    division_id = request.form['division_id']
    kurslist = ouAPI.get_kurslist(division_id)
    res = make_response(jsonify({'data': render_template('personal_kurslist.html', kurslist=kurslist,
                                                         user_kurs=current_user.kurs)}))
    res.set_cookie('division_id', division_id, max_age=60 * 60 * 24)
    return res


@app.route('/get_personalgrouplist', methods=['POST', 'GET'])
def get_personalgrouplist():
    division_id = request.cookies.get('division_id')
    kurs = request.form['kurs']
    grouplist = ouAPI.get_grouplist(division_id, kurs)
    dbGroup = Group.query.filter_by(user_id=current_user.id).first()
    if dbGroup is not None:
        res = make_response(jsonify({'data': render_template('personal_grouplist.html', grouplist=grouplist,
                                                             user_group=dbGroup.idGroup)}))
    else:
        res = make_response(jsonify({'data': render_template('personal_grouplist.html', grouplist=grouplist)}))
    return res


@app.route('/get_kurslist', methods=['POST'])
def get_kourselist():
    division_id = request.form['division_id']
    kurslist_response = ouAPI.get_kurslist(division_id)
    res = make_response(jsonify({'data': render_template('kurslist.html', kurs_list=kurslist_response)}))
    res.delete_cookie('division_id')
    res.delete_cookie('kurs')
    res.delete_cookie('group')
    res.set_cookie('division_id', division_id, max_age=60 * 60 * 24)
    return res


@app.route('/get_grouplist', methods=['POST'])
def get_grouplist():
    division_id = request.cookies.get('division_id')
    kurs = request.form['kurs']
    grouplist_response = ouAPI.get_grouplist(division_id, kurs)
    res = make_response(jsonify({'data': render_template('grouplist.html', group_list=grouplist_response)}))
    res.set_cookie('kurs', kurs, max_age=60 * 60 * 24)
    return res


@app.route('/print_student_schedule', methods=['POST'])
def print_student_schedule():
    group = request.form['group']
    weekstart = session.get('current_weekstart')

    weekstart_date = dtc.convert_back_local(weekstart)
    weekend_date = dtc.get_week_end(weekstart_date)
    week_day1 = (str(weekstart_date).split())[0]
    week_day2 = (str(dtc.increment_by_days(weekstart_date, 1)).split())[0]
    week_day3 = (str(dtc.increment_by_days(weekstart_date, 2)).split())[0]
    week_day4 = (str(dtc.increment_by_days(weekstart_date, 3)).split())[0]
    week_day5 = (str(dtc.increment_by_days(weekstart_date, 4)).split())[0]
    week_day6 = (str(dtc.increment_by_days(weekstart_date, 5)).split())[0]
    week_day7 = (str(weekend_date).split())[0]

    schedule_exercises = ouAPI.get_list_of_exercises(group, weekstart)

    res = make_response(jsonify({'data': render_template('table.html', schedule=schedule_exercises, week_day1=week_day1,
                                                         week_day2=week_day2, week_day3=week_day3, week_day4=week_day4,
                                                         week_day5=week_day5, week_day6=week_day6,
                                                         week_day7=week_day7, group=group,
                                                         weekstart_cookie=weekstart)}))
    res.set_cookie('group', group, max_age=60 * 60 * 24)
    res.set_cookie('weekstart', str(weekstart), max_age=60 * 60 * 24)
    return res


@app.route('/print_student_schedule_prev', methods=['POST'])
def print_student_schedule_prev():
    group = request.cookies.get('group')
    weekstart = request.cookies.get('weekstart')
    weekstart = int(weekstart) - 604800000

    weekstart_date = dtc.convert_back_local(weekstart)
    weekend_date = dtc.get_week_end(weekstart_date)
    week_day1 = (str(weekstart_date).split())[0]
    week_day2 = (str(dtc.increment_by_days(weekstart_date, 1)).split())[0]
    week_day3 = (str(dtc.increment_by_days(weekstart_date, 2)).split())[0]
    week_day4 = (str(dtc.increment_by_days(weekstart_date, 3)).split())[0]
    week_day5 = (str(dtc.increment_by_days(weekstart_date, 4)).split())[0]
    week_day6 = (str(dtc.increment_by_days(weekstart_date, 5)).split())[0]
    week_day7 = (str(weekend_date).split())[0]

    schedule_exercises = ouAPI.get_list_of_exercises(group, weekstart)

    res = make_response(jsonify({'data': render_template('table.html', schedule=schedule_exercises, week_day1=week_day1,
                                                         week_day2=week_day2, week_day3=week_day3, week_day4=week_day4,
                                                         week_day5=week_day5, week_day6=week_day6,
                                                         week_day7=week_day7, group=group,
                                                         weekstart_cookie=weekstart)}))
    res.set_cookie('weekstart', str(weekstart), max_age=60 * 60 * 24)
    return res


@app.route('/print_student_schedule_next', methods=['POST'])
def print_student_schedule_next():
    group = request.cookies.get('group')
    weekstart = request.cookies.get('weekstart')
    weekstart = int(weekstart) + 604800000

    weekstart_date = dtc.convert_back_local(weekstart)
    weekend_date = dtc.get_week_end(weekstart_date)
    week_day1 = (str(weekstart_date).split())[0]
    week_day2 = (str(dtc.increment_by_days(weekstart_date, 1)).split())[0]
    week_day3 = (str(dtc.increment_by_days(weekstart_date, 2)).split())[0]
    week_day4 = (str(dtc.increment_by_days(weekstart_date, 3)).split())[0]
    week_day5 = (str(dtc.increment_by_days(weekstart_date, 4)).split())[0]
    week_day6 = (str(dtc.increment_by_days(weekstart_date, 5)).split())[0]
    week_day7 = (str(weekend_date).split())[0]

    schedule_exercises = ouAPI.get_list_of_exercises(group, weekstart)

    res = make_response(jsonify({'data': render_template('table.html', schedule=schedule_exercises, week_day1=week_day1,
                                                         week_day2=week_day2, week_day3=week_day3, week_day4=week_day4,
                                                         week_day5=week_day5, week_day6=week_day6,
                                                         week_day7=week_day7, group=group,
                                                         weekstart_cookie=weekstart)}))
    res.set_cookie('weekstart', str(weekstart), max_age=60 * 60 * 24)
    return res


@app.route('/write_schedule_to_calendar', methods=['POST'])
@login_required
def write_schedule_to_calendar():
    if not google_auth.is_logged_in() and not current_user.is_anonymous:
        raise Exception('User must be logged in')

    oauth2_tokens = flask.session['auth_token']

    # weekstart = session.get('current_weekstart')
    weekstart = int(request.cookies.get('weekstart'))
    group = request.cookies.get('group')

    calendarID = request.form['calendarID']

    subgroup = request.form['subgroup']

    overwrite = True if 'overwrite' in request.form else False

    schedule_exercises = ouAPI.get_schedule_response(group, weekstart)

    dbUser = User.query.filter_by(id=current_user.id).first()
    dbGroup = Group.query.filter_by(user_id=current_user.id).first()

    if dbUser is not None:
        dbUser.lastCalendarID = calendarID
        dbUser.auto_insert = True
        dbUser.division = request.cookies.get('division_id')
        dbUser.kurs = request.cookies.get('kurs')
        db.session.commit()

    if dbGroup is None:
        dbGroup = Group(idGroup=group, subGroup=subgroup, user_id=current_user.id)
        db.session.add(dbGroup)
        db.session.commit()
    else:
        if dbGroup.idGroup != group:
            dbGroup.idGroup = group
            db.session.commit()
        if dbGroup.subGroup != subgroup:
            dbGroup.subGroup = subgroup
            db.session.commit()

    task = add_schedule_event.delay(calendarID, schedule_exercises, oauth2_tokens, overwrite,
                                    current_user.id,
                                    not current_user.is_anonymous, weekstart, subgroup)

    return redirect(url_for('index'))


@app.route('/check_events', methods=['POST', 'GET'])
def chek_events():
    weekstart = int(request.cookies.get('weekstart'))
    calendarID = request.form['calendarID']
    # group = request.cookies.get('group')

    events_from_calendar = get_week_events(calendarID, weekstart)

    c = sum([1 for item in events_from_calendar if
             'summary' in item and '(занятие)' in item['summary']]) if events_from_calendar else 0

    res = make_response(jsonify({'data': render_template('event_amount.html',
                                                         events_amount=c)}))

    return res


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


@app.route('/prepare_personalcalendar_list', methods=['GET'])
@login_required
def prepare_personalcalendar_list():
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
    res = make_response(jsonify({'data': render_template('personal_calendar.html', calendar_list=calendar_data,
                                                         lastcalendar=current_user.lastCalendarID)}))
    return res


@app.route('/status/')
def taskstatus(task_id):
    task = add_schedule_event.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


# @app.route('/prepare_for_export', methods=['GET'])
# @login_required
# def prepare_for_export():
#     weekstart = session.get('current_weekstart')
#     group = request.cookies.get('group')
#
#     schedule_request = base_request + '/' + str(group) + '///' + str(weekstart) + '/printschedule'
#     schedule_response = requests.get(schedule_request).json()
#
#     schedule_exercises = get_list_of_exercises(schedule_response)
#
#     response = make_response(
#         jsonify({'data': render_template('event_amount.html', calendar_len=len(schedule_exercises))}))
#     return response


# Получает ивенты из календаря, по началу недели.
def get_week_events(calendar_id, week_start):
    week_start = dtc.convert_back_utc(week_start)
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
    return events['items']


@app.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])


@app.route('/personal')
def personal():
    dbGroup = Group.query.filter_by(user_id=current_user.id).first()
    if dbGroup is not None:
        resp = make_response(
            render_template('personal.html', user_group=dbGroup.idGroup,
                            user_subgroup=dbGroup.subGroup))
    else:
        resp = make_response(
            render_template('personal.html'))

    return resp


@app.route('/save_personal', methods=['POST'])
def save_personal():
    division = request.form['personaldivision']
    kurs = request.form['personalkurs']
    group = request.form['personalgroup']
    subgroup = request.form['personalsubgroup']
    calendar = request.form['personalcalendar']
    if 'switch' in request.form:
        auto_insert = request.form['switch']
    else:
        auto_insert = False

    dbUser = User.query.filter_by(id=current_user.id).first()
    dbGroup = Group.query.filter_by(user_id=current_user.id).first()

    dbUser.division = division
    dbUser.kurs = kurs
    dbUser.lastCalendarID = calendar
    dbUser.auto_insert = auto_insert
    if dbGroup is not None:
        dbGroup.idGroup = group
        dbGroup.subGroup = subgroup
    else:
        dbGroup = Group(idGroup=group, subGroup=subgroup, user_id=current_user.id)
        db.session.add(dbGroup)

    current_user.add_notification('Данные обновленны', 'Успешно!')

    db.session.commit()

    return redirect(url_for('personal'))
