import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd
import warnings,os
import gunicorn

warnings.filterwarnings('ignore')
location_data=pd.read_pickle("final_reduced_df.pkl")

name_options = [dict(label=name, value=name) for name in location_data['person'].unique()]
year_options = [dict(label=year, value=year) for year in location_data['year'].unique()]
initial_year = list(range(min(location_data['year']),max(location_data['year'])))

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.layout = html.Div([

    html.Div([
        html.H1('Google Location History')
    ], className='Title'),

    html.Div([

        html.Div([
            html.Label('Person'),
            dcc.Dropdown(
                id='person_drop',
                options=name_options,
                value=['Ben','Carolina','Leo','Pedro'],
                multi=True
            ),

            html.Br(),

            html.Label('Year Choice'),
            dcc.Slider(
                id='year-slider',
                min=location_data['year'].min(),
                max=location_data['year'].max(),
                value=location_data['year'].min(),
                marks={str(year): str(year) for year in location_data['year'].unique()},
                step=None
            )

        ], className='column1 pretty'),
        html.Div([dcc.Graph(id='graph-with-slider')], className='column2 pretty')
    ], className='row'),

    html.Div([
        html.Div([dcc.Graph(id='bar-graph')], className='column1 pretty'),
        html.Br(),
        html.Div([dcc.Graph(id='heatmap')], className='column3 pretty')

    ], className='row'),

])

@app.callback(
    [Output('graph-with-slider', 'figure'),
     Output('heatmap','figure'),
     Output('bar-graph','figure')],
    [Input('year-slider', 'value'),
     Input('person_drop','value')])

def update_figure(selected_year,person_selected):
    filtered_df = location_data[location_data.year == selected_year]
    traces = []
    lines = []
    filtered_df=filtered_df[filtered_df.person.isin(person_selected)]
    filtered_people_df = location_data.copy(deep=True)
    filtered_people_df['location'] = filtered_people_df['latitude'].map(str) + filtered_people_df['longitude'].map(str)
    filtered_people_df.drop(['latitude', 'longitude'], axis=1, inplace=True)
    df_line = pd.DataFrame(filtered_people_df.groupby(['year','person'])['location'].nunique()).reset_index()
    for i in filtered_df.person.unique():
        df_by_person= filtered_df[filtered_df['person'] == i]
        df_by_person_line = df_line[df_line['person'] == i]
        if i =='Leo':
            color_person='blue'
        elif i=='Pedro':
            color_person='purple'
        elif i=='Carolina':
            color_person='red'
        else:
            color_person='green'
        traces.append(dict(type='scattermapbox',
                         mode="markers",
                         lon = df_by_person['longitude'],
                         lat = df_by_person['latitude'],
                         marker=dict(
                         size =10,
                         # size=df_by_person.groupby(['longitude','latitude'])['datetime'].count(),
                         sizeref=0.9,
                         color=color_person,
                         opacity=0.9),
                         name=i,
                         legendgroup =i
                           )
                        )
        lines.append(dict(
            x=df_by_person_line['year'],
            y=df_by_person_line['location'],
            mode='markers+lines',
            opacity=0.7,
            marker={
                'size': 5,
                'line': {'width': 0.5, 'color': color_person}
            },
            name=i
        ))

    fig = go.Figure(go.Densitymapbox(lat=filtered_df['latitude'], lon=filtered_df['longitude'],
                                     radius=10))
    fig.update_layout(mapbox_style="stamen-terrain", mapbox_center_lon=180)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return [{
        'data': traces,
        'layout': dict(margin ={'l':0,'t':0,'b':0,'r':0},
                        mapbox = {
                        'center': {'lon': 10, 'lat': 10},
                        'style': "stamen-terrain",
                        'center': {'lon': -20, 'lat': -20},
                        'zoom': 1},
                        legend = dict(bordercolor='rgb(100,100,100)',
                                      borderwidth=2,
                                      itemclick='toggleothers', # when you are clicking an item in legend all that are not in the same group are hidden
                                      x=0.91,
                                      y=1)
    )
    },
        fig,
        {
        'data': lines,
        'layout': dict(
            xaxis={'title': 'Year'},
            yaxis={'title': 'Locations'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1}
        )
    }]

if __name__ == '__main__':
    app.run_server(debug=True)
