import os
import yaml
import collections

import numpy as np
import pandas as pd

from datetime import date, timedelta, datetime
import glob
import json 

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objs as go
import dash_table

from IPython.display import display, Markdown, Latex, HTML

ENV_FILE = '../env.yaml'
with open(ENV_FILE) as f:
    params = yaml.load(f, Loader=yaml.FullLoader)

# Initialisation des chemins vers les fichiers
ROOT_DIR = os.path.dirname(os.path.abspath(ENV_FILE))
DATA_JSON_FILE = os.path.join(ROOT_DIR,
                              params['directories']['question_answering'],
                              params['files']['cord19_answers'])

# Read the data (JSON and CSV files)
with open(DATA_JSON_FILE, mode='r') as file:
     cord19_answers_json = json.loads(file.read())

tasks_questions = {
    tq['task']: {q['question'] for q in tq['questions']} for tq in cord19_answers_json['data']
}

DATA_CSV_FILE = os.path.join(ROOT_DIR,
                              params['directories']['question_answering'],
                              params['files']['results_answers'])

results_answers = pd.read_csv(DATA_CSV_FILE,
                              dtype={'task':str,'question':str,'context':str,'answer':str,'reference':str})


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    html.Label("Select a task", style={'color': 'darkgreen', 'fontSize': 25}),
    dcc.Dropdown(
        id='tasks_dropdown',
        style={'color': 'darkgreen', 'fontSize': 20},
        options=[{'label': k, 'value': k} for k in tasks_questions.keys()],
        disabled=False,
        value='What do we know about non-pharmaceutical interventions?'
    ),

    html.Hr(),
    html.Label("Select a question", style={'color': 'darkblue', 'fontSize': 25}),
    dcc.Dropdown(
        id='questions_dropdown',
        style={'color': 'darkblue', 'fontSize': 20}
    ),

    html.Hr(),
    html.Div([
        html.Div(
            id='display-selected-values',
            style={
                'justify':'center',
                'align':'center',
                'margin-left': 45,
                'margin-right':45,
                'color':'white',
                'fontSize': 19,
                'backgroundColor':'#3aacb2',
            }
        ),
        #html.P(id='display_context')
    ])
])

@app.callback(
    Output('questions_dropdown', 'options'),
    [Input('tasks_dropdown', 'value')])
def set_questions_options(selected_task):
    return [{'label': i, 'value': i} for i in tasks_questions[selected_task]]


@app.callback(
    Output('questions_dropdown', 'value'),
    [Input('questions_dropdown', 'options')])
def set_questions_value(available_options):
    return available_options[0]['value']


@app.callback(
    Output('display-selected-values','children'),
    [Input('tasks_dropdown', 'value'),
     Input('questions_dropdown', 'value')
    ])
def set_display_children(selected_task, selected_question):
    return results_answers[(results_answers.task== selected_task) &
                           (results_answers.question==selected_question)]['context']


if __name__ == '__main__':
    app.run_server(debug=True)

# https://dash.plotly.com/basic-callbacks