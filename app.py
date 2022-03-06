import dash

from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import plotly.express as px
import dash_daq as daq
import datetime
import requests
import json


energy_img = "https://www.pinclipart.com/picdir/big/105-1057895_green-my-life-app-eliminates-the-carbon-footprint.png"
earth_img = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSx-MftU146rqnu3qXiH1-PvbhqkBtqxln3nA&usqp=CAU"

now = datetime.datetime.now()
app = dash.Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP],
                meta_tags=[{'name':'viewport', 'content':'width = device-width, initial-scale = 1'}]
                )
app.title = 'SPARC'

# styling the sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# padding for the page content
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("About SPARC", className="display-4"),
        html.Hr(),
        dbc.Nav(
            [
                html.P('Schedule Power and Reduce Carbon')
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

pred_content = html.Div([

])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H3('SPARC - Schedule Power and Reduce Carbon'),

        ], width=8)
    ]),
    dbc.Row(dbc.Col([
            html.Img(src=app.get_asset_url('green-my-life-app.png'))
    ], width={'offset':2})),
    html.P(),
    dbc.Row([
        dbc.Col([
            html.P('I live in'),
        ], width = 2),

        dbc.Col([
            dcc.Dropdown(id = 'dropdown-state',options = [{'label':'California', 'value':'California'}],
                         value='California' )
        ], width=2)
    ]),
    dbc.Row([
        dbc.Col([
            html.P('I want to')
        ], width = 2),
        dbc.Col([
            dcc.Dropdown(id = 'dropdown-activity', multi=True,
                         options = [{'label':'A load of laundry', 'value':'laundry'},
                                    {'label':'Charge EV', 'value':'chargeEV'},
                                    {'label':'A hot shower',  'value':'hotshower'}],
                         value = ['chargeEV'], )
        ], width = 3),
    ]),

    dbc.Row([
       dbc.Col([
           html.P('Select a time window'),
           dcc.RangeSlider(0, 24, id = 'time-range',value=[int(now.hour), int(now.hour + 2)],
                           tooltip={"placement": "bottom", "always_visible": True})
       ])
    ]),
    html.Hr(),
    dbc.Row([
        dbc.Col([
            dbc.Button("Predict CO2", id = 'btn-co2-pred',  className="mb-2",)
        ])
    ]),

    dbc.Row([
        dbc.Col([
            daq.Gauge(
                label="Your Current Emission is",
                value=0, min = 0, max = 10,
                color={"gradient":True,"ranges": {"green": [0, 4], "yellow": [4, 7], "red": [7, 10]}}
            )
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id = 'pred-output-container')
        ])
    ])

], fluid=False, style = {'width': '100%', 'padding-top':'2%', 'padding-left':'8%',
            # 'display': 'flex',
            'align-items': 'center',
            'justify-content': 'center'
            })


@app.callback(
    Output('pred-output-container', 'children'),
    Input('btn-co2-pred', 'n_clicks')
)

def pred_co2(n_clicks):
    res = requests.get(f"https://sparc-cloud-run-hdyvu4kycq-uw.a.run.app/predict")
    # print('\n\n\nresult of call: ', res.text, '\n\n\n')
    res = json.loads(res.text)['result']
    df = pd.DataFrame(res).reset_index(drop=True)
    # print(df.head())
    # df.to_csv('testdf.csv')
    print(df.head(24))

    # if n_clicks:
    #     for col in df.columns:
    #         if 'total' not in col.lower():
    #             df


if __name__ == "__main__":
    app.run_server(debug=True, port = 8080, host='0.0.0.0')
