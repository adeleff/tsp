# -*- coding: utf-8 -*-
import time
import dash
import flask
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State


import app.components as comp
import app.file_handlers as fh
from app.helpers import parse_contents, prepare_data
from app.solvers import make_plot_data


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


def create_app():
    """
    Dash app factory and layout definition
    """
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    app.config['suppress_callback_exceptions'] = True

    app.layout = html.Div([
        dcc.Store(id='memory'),
        html.Div(children=[
            html.H3('Files upload', style={'margin-top': '40px'}),
            comp.vbar(),
            html.Table(children=[
                html.Tr(children=[
                    html.Td(children=[
                        comp.upload(idx='city-matrix-input', name='First upload city-matrix...'),
                        html.Div(id='output-city-matrix')],
                        style={'width': '33%', 'vertical-align': 'top'}),

                    html.Td(children=[
                        comp.upload(idx='coordinates-input', name='...now we need coordinates...'),
                        html.Div(id='output-coordinates')],
                        style={'width': '33%', 'vertical-align': 'top'}),

                    html.Td(children=[
                        comp.upload(idx='info-input', name='...finally add some info'),
                        html.Div(id='output-info')],
                        style={'width': '33%', 'vertical-align': 'top'}),
                ])
            ], style={'width': '100%', 'height': '100px'}),
            comp.button('solve-btn', 'solve'),
        ]),

        html.Div(children=[
            html.Div(id='save-prompt', children=[]),
            dcc.Loading([html.Div(id='tsp-solution', children=[])], color='#1EAEDB'),
            dcc.Loading([html.Div(id='tsp-graph', children=[])], color='#1EAEDB')
        ], style={'margin-top': '40px'})

    ], style={'width': '85%', 'margin-left': '7.5%'})

    @app.callback([Output('output-city-matrix', 'children')],
                  [Input('city-matrix-input', 'contents')],
                  [State('city-matrix-input', 'filename')])
    def upload_city_matrix(content, name):
        if content is not None:
            if '.csv' not in name:
                return html.Div(['Only .csv files ar supported!']),
            df = parse_contents(content)
            result = fh.validate_cities(df)
            if not result.status:
                return html.P(result.msg),

            return comp.upload_table(name, df),
        return None,

    @app.callback([Output('output-coordinates', 'children')],
                  [Input('coordinates-input', 'contents')],
                  [State('coordinates-input', 'filename')])
    def upload_coordinates(content, name):
        if content is not None:
            if '.csv' not in name:
                return html.Div(['Only .csv files ar supported!']),
            df = parse_contents(content)
            result = fh.validate_paths(df)
            if not result.status:
                return html.P(result.msg),

            return comp.upload_table(name, df),
        return None,

    @app.callback([Output('output-info', 'children')],
                  [Input('info-input', 'contents')],
                  [State('info-input', 'filename')])
    def upload_info(content, name):
        if content is not None:
            if '.csv' not in name:
                return [html.Div(['Only .csv files ar supported!']), {'visibility': 'hidden'}]
            df = parse_contents(content)
            result = fh.validate_time(df)
            if not result.status:
                return html.P(result.msg),

            return comp.upload_table(name, df),
        return None,

    @app.callback([Output('tsp-solution', 'children'), Output('memory', 'data')],
                  [Input('solve-btn', 'n_clicks'),
                   Input('city-matrix-input', 'contents'),
                   Input('coordinates-input', 'contents'),
                   Input('info-input', 'contents')],
                  [State('memory', 'data')])
    def generate_solution(n_clicks, city, coords, df_time, cache):
        if n_clicks and city and coords and df_time and n_clicks > 0:
            tic = time.time()

            df_time = parse_contents(df_time)
            solution, cities, edges = make_plot_data(cities=parse_contents(city),
                                                     paths=parse_contents(coords),
                                                     time=df_time)

            solving_time = time.time() - tic

            # Save solution
            fh.save_solution(solution, df_time.time.values[0])

            # Generate html elements
            output = [html.H3(children='The magic TSP graph'), comp.vbar()]
            output += comp.stats(solving_time, solution, cities)

            # Cache data
            cache = {'cities': prepare_data(cities), 'edges': list(edges)}

            return output, cache

        if n_clicks is not None and n_clicks > 0:
            return [html.P('no data')], dict()

        return None, dict()

    @app.callback([Output('tsp-graph', 'children')],
                  [Input('memory', 'data')],
                  [State('memory', 'data')])
    def show_plot(cache):
        if cache:
            cities, edges = cache.values()
            plot = comp.graph(cities, edges)
            return plot,
        return None,

    @app.callback([Output('save-prompt', 'children')],
                  [Input('save-btn', 'n_clicks')])
    def save_solution(n_clicks):
        if n_clicks and n_clicks > 0:
            print('saved')
            return [html.P('works')]

        return None,

    @app.server.route('/tmp/solution')
    def download_solution():
        return flask.send_file('tmp/solution.txt',
                               mimetype='text',
                               attachment_filename='solution.txt',
                               as_attachment=True)

    return app
