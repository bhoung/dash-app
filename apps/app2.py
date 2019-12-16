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
dates = dates.reset_index()
print(dates)
opts = [{'label' : i, 'value' : i} for i in dates['date']]

df_sum = m.groupby(['date'])['harvested'].sum()
df_sum = df_sum.to_frame()
df_sum.columns = ['harvested']
df_sum['date'] = df_sum.index

def create_map(d):
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
    layout = go.Layout(title="Snapshot harvested area (ha) by tile over time",
                            mapbox_style="carto-positron",
                            mapbox_zoom=7.7,
                            mapbox_center = {"lat": -20.4168,
                                             "lon": 148.456},
                            margin={"r":0,"t":25,"l":0,"b":0},
                            width=800,
                            height=400)
            
    return {'data': [map], 'layout': layout}

def create_graph():
    layout = go.Layout(title = "Total harvested area (ha) over time", hovermode = 'closest')
    graph = go.Figure(data = [dict(type = 'scatter', 
                                 mode = 'lines+markers', 
                                 x = df_sum['date'], 
                                 y = df_sum['harvested'])], layout = layout)
    graph.update_xaxes(title_text="*Hover over the harvested area time series to display the harvest area by tile at different points in time")
    return(graph)

graph = create_graph()
print(dates['date'][0])
map = create_map(dates['date'][0])

body = dbc.Container([               
    html.Div([dcc.Graph(id='app2_plot1', figure = graph)], style = {'width': '800px'}),
    html.Div([dcc.Dropdown(id = 'app2_opt', options = opts), html.Div(id='text1'),], style={'display': 'none'}),
    html.Div([dcc.Graph(id='app2_plot2', figure = map)], style = {'width': '800px', 'height':'400px'}),
])
    
layout = html.Div([nav, body])        

@app.callback(Output('app2_opt', 'value'), 
	         [Input('app2_plot1', 'hoverData')] )
def text_callback(hoverData):
    if hoverData is None: 
        print(dates['date'][0])
        return dates['date'][0]
    else:          
        print(hoverData)
        x = hoverData["points"][0]["x"]
        print(x)                                   
        return x  

@app.callback(Output('app2_plot2', 'figure'),
              [Input('app2_opt', 'value')])
def update_map(value):
	if value is None:
	    value = dates['date'][0]
	print(value)
	map2 = create_map(value)
	#print(map2)
	return(map2)


