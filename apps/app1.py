import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import json
import pandas as pd

from navbar import Navbar
from app import app
import plotly.graph_objs as go
from plotly.subplots import make_subplots

nav = Navbar()

# read in data
file = open("./data/phase-02.geojson")
tiles_geojson = json.load(file)
df = pd.read_csv("./data/m.csv", dtype={"id": str})

mapbox_token = 'pk.eyJ1IjoibWFoZXNoeCIsImEiOiJjazJsNnlwcmQwNDFjM2xtdWNoM244emU4In0.YBO8xPG8Iw-BfL8sxSkpTw'

# aggregate data over tiles
df_sum = df.groupby(['id'])['harvested'].sum()
df_sum = df_sum.to_frame()
df_sum.columns = ['harvested']
print(max(df_sum))
print(min(df_sum))
print(df_sum.head())
print(df_sum)

# choropleth map
map = go.Figure(go.Choroplethmapbox(geojson=tiles_geojson, 
                                     locations=df_sum.index, 
                                     z=df_sum.harvested,
                                     colorscale="Viridis", 
                                     zmin=17443,
                                     zmax=2962745,
                                     marker_opacity=0.5, 
                                     marker_line_width=0))

map.update_layout(title = "Harvested Sugar Cane Area (ha) by Tile",
                   mapbox_style="satellite",
                   mapbox_accesstoken=mapbox_token,
                   mapbox_zoom=7.5, 
                   mapbox_center = {"lat": -20.4168, "lon": 148.356})

# convert to hectares
df['harvested'] = df['harvested'] * 100 / 10000
print(max(df['harvested']))
print(min(df['harvested']))
df = df[df['cc_p80_perc'] < 35]
df = df.reset_index()
df['cc_p80_perc'] = df['cc_p80_perc']/100 

# dropdown options
tiles = df.tile.unique()
opts = [{'label' : i, 'value' : i} for i in tiles]

# Step 3. Create a plotly figure
print("label %s" % opts[0]['label'])
print("label type %s" % type(df.tile[0]))
initial_tile = opts[0]['label']

# time series line graphs
def create_graph(value):    
    df2 = df[(df.tile == value)]
    	
    trace_1 = go.Scatter(x = df2.date, y = df2['ndvi'],
                        name = 'NDVI (vegetation index)',
                        mode = 'lines+markers',
                        line = dict(width = 2, color = 'rgb(0, 255, 0)'))
                
    trace_2 = go.Scatter(x = df2.date, y = df2['cc_p80_perc'],
                        name = 'Cloud Cover (P > 0.8)',
                        mode = 'lines+markers',
                        line = dict(width = 2, color = 'gray', dash = 'dash'))
     
    trace_3 = go.Scatter(x = df2.date, y = df2['harvested'],
                        name = 'Harvested (ha.)',
                        mode = 'lines+markers',
                        line = dict(width = 2, color = 'rgb(0, 0, 255)'))
    
    app_layout = go.Layout(title = 'Time Series Plot', hovermode = 'closest')
    
    graph = go.Figure(data = [], layout = app_layout)
    graph = make_subplots(specs=[[{"secondary_y": True}]])
    graph.update_layout(title=f"Tile={value}")

    # Set axes titles
    #graph.update_xaxes(title_text="<b>Month</b>")
    graph.update_yaxes(title_text="<b>ndvi & cloud cover</b>", secondary_y=False)
    graph.update_yaxes(title_text="<b>harvested</b>", secondary_y=True)

    graph.add_trace(go.Scatter(trace_1), secondary_y=False,)
    graph.add_trace(go.Scatter(trace_2), secondary_y=False,)
    graph.add_trace(go.Scatter(trace_3), secondary_y=True,)
    graph.update_layout(legend_orientation="h")
                                  
    return graph

graph = create_graph(initial_tile)

body = dbc.Container([
    html.Div([dcc.Graph(id='plot1', figure = map)], 
       	     style={'width':"50%", 'display':'inline-block'}),
    html.Div([dcc.Graph(id = 'plot2', figure = graph)], 
       	     style = {'width': "50%", 'display': 'inline-block'}),
    html.Div([dcc.Dropdown(id = 'opt', options = opts),
             html.Div(id='text1'),]
             , style={'display': 'none'}),
])                                       
    
layout = html.Div([nav, body])        

@app.callback(Output('opt', 'value'), 
	         [Input('plot1', 'hoverData')] )
def text_callback(hoverData):
    if hoverData is None:
        print(initial_tile)
        return initial_tile
    else:                                                         
        print(hoverData)                           
        x = hoverData["points"][0]["location"]
        y = df.loc[df['id'] == x, 'tile'].iloc[0]
        return y
              
@app.callback(Output('plot2', 'figure'),
             [Input('opt', 'value')])                             
def update_graph(value):
    if value == None:
        value = initial_tile

    print("Value: %s" % value)
    
    graph = create_graph(value)
    return(graph)
    
    
