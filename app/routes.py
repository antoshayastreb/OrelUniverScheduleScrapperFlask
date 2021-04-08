from app import app
from flask import render_template, request, jsonify
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
    return jsonify({'data': render_template('kurslist.html', kurs_list=kurslist_response)})


@app.route('/get_grouplist', methods=['POST'])
def get_grouplist():
    division_id = request.form['division_id']
    kurs = request.form['kurs']
    grouplist_request = base_request + str(division_id) + '/' + str(kurs) + '/' + 'grouplist'
    grouplist_response = ast.literal_eval(requests.get(grouplist_request).text)
    return jsonify({'data': render_template('grouplist.html', group_list=grouplist_response)})


def get_divisionlist():
    divisions_request = base_request + 'divisionlistforstuds'

    divisions_response = ast.literal_eval(requests.get(divisions_request).text)

    return divisions_response
