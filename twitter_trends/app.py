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

# Style sheet and Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUMEN])

# Dash layout
app.layout = html.Div([
    dcc.Dropdown(id='tree-map-dropdown',
                 placeholder='Select Country(-ies)',
                 options=options,
                 multi=True),
    dbc.Button(id='button', children='Submit',
               n_clicks=0, color='dark'),
    html.Div(dcc.Loading([
        dcc.Graph(id='chart',
                  figure=go.Figure({'layout':
                                        {'paper_bgcolor': '#eeeeee',
                                         'plot_bgcolor': '#eeeeee',
                                         'template': 'none'}},
                                   {'config': {'displayModeBar': False}}),
                  config={'displayModeBar': False})
    ]))])


@app.callback(Output('chart', 'figure'),
              [Input('button', 'n_clicks')],
              [State('tree-map-dropdown', 'value')])
def treemap_table(n_clicks, locations):
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
                             color_continuous_scale='RdBu')

        fig.add_trace(sub_fig.to_dict()['data'][0], row=index + 1, col=1)

        fig.layout.height = 400 * n_countries
        fig.layout.template = 'none'
        fig.layout.margin = {'t': 40, 'b': 40}
        fig.layout.paper_bgcolor = '#eeeeee'
        fig.layout.plot_bgcolor = '#eeeeee'

    return fig.to_dict()


if __name__ == '__main__':
    app.run_server()
