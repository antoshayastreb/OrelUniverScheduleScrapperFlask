from app import app
from flask import render_template, request, jsonify, make_response
import ast
import requests

base_request = 'http://oreluniver.ru/schedule/'


@app.route('/')
@app.route('/index')
def index():
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
    division_id = request.cookies.get('division_id')
    kurs = request.cookies.get('kurs')
    group = request.form['group']
    grouplist_request = base_request + str(division_id) + '/' + str(kurs) + '/' + 'grouplist'
    grouplist_response = ast.literal_eval(requests.get(grouplist_request).text)
    res = make_response(jsonify({'data': render_template('grouplist.html', group_list=grouplist_response)}))
    res.set_cookie('group', group)
    return res


def get_divisionlist():
    divisions_request = base_request + 'divisionlistforstuds'

    divisions_response = ast.literal_eval(requests.get(divisions_request).text)

    return divisions_response
