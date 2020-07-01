from twitter_credentials import ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_SECRET, CONSUMER_KEY
from local_trends import TwitterAuthorization, TwitterClient, OAuthHandler
from tweepy import API

# import dash libraries and components
import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_table import DataTable
import dash_html_components as html
import dash_core_components as dcc
from plotly import express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from dash_table.FormatTemplate import Format

# import libraries for data processing
import pandas as pd
import numpy as np

# Instances for preprocessing
df_2 = pd.read_csv('twitter_trend_location.csv')
options = [{f'label': df_2['name_country'].values[index], 'value': df_2['woeid'].values[index]} for index in
           range(len(df_2['name_country'].values))]

# Twitter Client
auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

twitter_client = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

TABLE_COLS = ['name', 'city', 'country', 'tweet_volume']

# Style sheet and Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUMEN])

# Dash layout
app.layout = html.Div([html.Div([
    html.Br(), html.Div([html.H1('Twitter Trends by Country',
                                 style={'display': 'inline',
                                        'textAlign': 'center',
                                        'margin': 0,
                                        'width': '100px',
                                        'left': '50%'})],
                        style={'textAlign': 'center'}),
    html.Br(),
    html.Div([
        dcc.Dropdown(id='tree-map-dropdown',
                     placeholder='Select Country(-ies)',
                     options=options,
                     multi=True)],
        style={
            'verticalAlign': 'top',
            'left': '50%',
            'margin-left': '375px',
            'margin-right': '375px'}),
    html.Div([
        dbc.Button(id='button', children='Submit',
                   n_clicks=0, color='dark')],
        style={'verticalAlign': 'top',
               'left': '50%',
               'padding-top': '5px',
               'margin-left': '375px',
               'margin-right': '375px'})]),
    html.Br(),
    html.Div([dcc.Loading([
        dcc.Graph(id='chart',
                  figure=go.Figure({'layout':
                                        {'paper_bgcolor': '#eeeeee',
                                         'plot_bgcolor': '#eeeeee'}},
                                   {'config': {'displayModeBar': False}}, ),
                  config={'displayModeBar': False})
    ])]),
    html.Br(),
    html.Br(),
    dbc.Col(lg=10),
    html.Div([DataTable(
        id='table',
        style_header={'textAlign': 'center'},
        style_cell={'font-family': 'Source Sans Pro',
                    'minWidth': 100,
                    'textAlign': 'left'},
        export_format='csv',
        sort_action='native',
        columns=[{'name': i.title(), 'id': i,
                  'type': 'numeric' if i == 'Tweet Volume' else None,
                  'format': Format(group=',') if i == 'Tweet Volume' else None}
                 for i in TABLE_COLS],
        data=pd.DataFrame({
            k: ['' for i in range(10)] for k in TABLE_COLS}).to_dict('rows'),
    )]
        ,
    style={
        'margin-left': 50,
        'margin-right': 50
    }
    )
])


@app.callback([Output('table', 'data'),
               Output('chart', 'figure')],
              [Input('button', 'n_clicks')],
              [State('tree-map-dropdown', 'value')])
def treemap_table(n_clicks, locations):
    if not locations:
        locations = []
    else:
        pass

    # original dataframe for table data
    dataframe_for_table = pd.DataFrame(
        columns=['name', 'city', 'country', 'url', 'promoted_content', 'query', 'tweet_volume'])
    # country list
    countries = [df_2['name'][df_2['woeid'] == woeid].values[0] for woeid in locations]
    n_countries = len(countries)

    fig = make_subplots(rows=n_countries, cols=1,
                        subplot_titles=['Worldwide' if not c else c
                                        for c in countries],
                        specs=[[{'type': 'treemap'}]
                               for i in range(n_countries)],
                        vertical_spacing=0.05)

    for index, woeid in enumerate(locations):
        # Name of city
        name = df_2['name'][df_2['woeid'] == woeid].values[0]
        # Name of country
        country = df_2['country'][df_2['woeid'] == woeid].values[0]

        df_1 = pd.DataFrame(twitter_client.trends_place(woeid)[0]['trends'])

        # inserting woeid number
        df_1.insert(0, 'woeid', int(df_2[df_2['woeid'] == woeid]['woeid']))

        # Inserting city name
        df_1.insert(1, 'city', name)

        # Inserting country name
        df_1.insert(2, 'country', country)

        sub_fig = px.treemap(df_1,
                             path=['country', 'city', 'name'],
                             values='tweet_volume',
                             color='tweet_volume',
                             color_continuous_scale='RdBu',
                             hover_data=["name", "tweet_volume"])

        # hover data

        sub_fig.layout.margin = {'b': 5, 't': 5}
        sub_fig.data[0]['hovertemplate'] = '<b>%{label}</b><br>Tweet volume: %{value}'
        sub_fig.data[0][
            'texttemplate'] = '<b>%{label}</b><br><br>Tweet volume: %{value}<br>%{percentParent} of %{parent}'

        fig.add_trace(sub_fig.to_dict()['data'][0], row=index + 1, col=1)

        # Creating table

        dataframe_for_table = pd.concat([dataframe_for_table, df_1], axis=0).reset_index().drop('index', axis=1)
        dataframe_for_table = dataframe_for_table[TABLE_COLS]

    # layout for treemap

    fig.layout.height = 400 * n_countries
    fig.layout.template = 'none'
    fig.layout.margin = {'t': 40, 'b': 40}
    fig.layout.paper_bgcolor = '#eeeeee'
    fig.layout.plot_bgcolor = '#eeeeee'

    return dataframe_for_table.to_dict('rows'), fig.to_dict()


if __name__ == '__main__':
    app.run_server(port='8888')
