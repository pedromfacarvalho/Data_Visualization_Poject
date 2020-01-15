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
# location_data=location_data.drop(['accuracy', 'activity', 'altitude','heading','timestamp', 'velocity', 'verticalAccuracy'],axis=1)
# location_data = location_data.groupby(['person', pd.Grouper(freq='D'),'latitude','longitude'],as_index=False,sort=False).size().reset_index(drop=False)
# #grouped_mean = location_data.groupby(['person', pd.Grouper(freq='D')],sort=False)['latitude','longitude'].mean().reset_index(drop=False)
# location_data=location_data.drop([0],axis=1)
# location_data['year'] = location_data['datetime'].dt.year

name_options = [dict(label=name, value=name) for name in location_data['person'].unique()]
year_options = [dict(label=year, value=year) for year in location_data['year'].unique()]
initial_year = list(range(min(location_data['year']),max(location_data['year'])))

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

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
        html.Br(),
        # html.Div([dcc.Graph(id='heatmap')], className='column1 pretty'),

        html.Div([dcc.Graph(id='heatmap')], className='column3 pretty')

    ], className='row'),

])

@app.callback(
    [Output('graph-with-slider', 'figure'),
    Output('heatmap','figure')],
    [Input('year-slider', 'value'),
     Input('person_drop','value')])

def update_figure(selected_year,person_selected):
    filtered_df = location_data[location_data.year == selected_year]
    traces = []
    filtered_df=filtered_df[filtered_df.person.isin(person_selected)]
    for i in filtered_df.person.unique():
        df_by_person= filtered_df[filtered_df['person'] == i]
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
                         opacity=0.9,
                         name=i,
                         labelgrup=i
                           )
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
    },fig]

if __name__ == '__main__':
    app.run_server(debug=True)
