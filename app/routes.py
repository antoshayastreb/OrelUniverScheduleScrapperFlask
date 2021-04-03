from app import app
from flask import render_template
import ast
import requests


@app.route('/')
@app.route('/index')
def index():
    base_request = 'http://oreluniver.ru/schedule/'
    divisions_request = base_request + 'divisionlistforstuds'

    divisions_response = ast.literal_eval(requests.get(divisions_request).text)

    context = {
        'divisions': divisions_response,
    }
    return render_template('index.html', divisions=divisions_response)
