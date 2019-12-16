import os
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from navbar import Navbar
from app import app

import pandas as pd
import json
import plotly.graph_objs as go

nav = Navbar()

mapbox_access_token = "pk.eyJ1IjoibWFoZXNoeCIsImEiOiJjazJsNnlwcmQwNDFjM2xtdWNoM244emU4In0.YBO8xPG8Iw-BfL8sxSkpTw"

# read in data
file = open("./data/phase-02.geojson")
tiles = json.load(file)

m = pd.read_csv("./data/m.csv", dtype={"id": str})
m['harvested'] = m['harvested'] * 100 / 10000
#https://community.plot.ly/t/solved-scattermapbox-callback-to-update-link-not-working/20318

dates = pd.read_csv("./data/dates.csv")
# show every 3rd row 
dates = dates.iloc[::3,:]
dates = dates.reset_index()
print(dates)

opts = [{'label' : i, 'value' : i} for i in dates['date']]

df_sum = m.groupby(['date'])['harvested'].sum()
df_sum = df_sum.to_frame()
df_sum.columns = ['harvested']
df_sum['date'] = df_sum.index



def create_fig():
    layout = go.Layout(title = "Total harvested area (ha) over time", hovermode = 'closest')
    fig = go.Figure(data = [dict(type = 'scatter', 
                                 mode = 'lines+markers', 
                                 x = df_sum['date'], 
                                 y = df_sum['harvested'])], layout = layout)
    return(fig)

fig2 = create_fig()
marks = {i: d[2:7] for i, d in enumerate(dates['date'].unique())}
print(marks)                          

body = dbc.Container([
    html.Div([
        dcc.Graph(id='graph-with-slider')
    ], style={'width':'800px', 'height':'400px'}
    ),
        html.Div([
            dcc.Slider(
                id='date-slider',
                min=0,
                max=dates.shape[0],
                value=0,
                step=1,
                marks={i: d[2:7] for i, d in enumerate(dates['date'].unique())}
            )
        ], style={'width':'800px', 'margin': 25}
        ),                                     
    html.Div([
       dcc.Graph(id='plot2', figure = fig2)     
    ], style= {'width': '800px'}),
    #html.Div([dcc.Dropdown(id = 'opt2', options = opts),
             #html.Div(id='text1'),]),
             #, style={'display': 'none'}),
])
    
layout = html.Div([nav, body])        

#@app.callback(Output('opt2', 'value'), 
#	         [Input('plot2', 'hoverData')] )
#def text_callback(hoverData):
#	return(hoverData)
"""
if hoverData is None:
    print(initial_tile)
    return initial_tile
else:
    print(hoverData)
    x = hoverData["points"][0]["location"]
    y = df.loc[df['id'] == x, 'tile'].iloc[0]
    return y
"""
                          
@app.callback(dash.dependencies.Output('graph-with-slider', 'figure'),
              [dash.dependencies.Input('date-slider', 'value')])
              #[dash.dependencies.Input('opt', 'value')])
def update_figure(selected_date):
#def update_figure(value):
    d = dates.loc[selected_date, 'date']
    fdf = m[m.date == d]
    map = go.Choroplethmapbox(geojson=tiles,
                        locations=fdf.id,
                        z=fdf.harvested,
                        colorscale="Viridis",
                        zmin=0,
                        zmax=1664.48,
                        text = fdf['tile'],
                        hovertemplate = '<b>Tile</b>: <b>%{text}</b>'+
                                        '<br><b> Harvested </b>: %{z}<br>',
                        marker_opacity=0.5,
                        marker_line_width=0.5,
                        name="sugar cane tile")
            
    return {
        'data': [map],
        'layout': go.Layout(title="Snapshot harvested area (ha) by tile over time",
                            mapbox_style="carto-positron",
                            mapbox_zoom=7.7,
                            mapbox_center = {"lat": -20.4168,
                                             "lon": 148.456},
                            margin={"r":0,"t":25,"l":0,"b":0},
                            width=800,
                            height=400
        )
    }

#https://community.plot.ly/t/adding-maps-without-using-mapbox/9584/5

