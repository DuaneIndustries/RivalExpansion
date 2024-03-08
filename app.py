#IMPORTS
import pandas as pd
import plotly
import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input,Output
from dash import dash_table
import io
import requests
from datetime import datetime, timedelta

url='https://raw.githubusercontent.com/DuaneIndustries/RivalExpansion/main/RIval_Project_Calendar_v7.csv'
s=requests.get(url).content
df=pd.read_csv(io.StringIO(s.decode('utf-8')))

# df = pd.read_csv("/Users/caseyleo/Desktop/RIval_Project_Calendar.csv")



df['Start Date'] = pd.to_datetime(df['Start Date'], format="%m/%d/%y")
df['End Date'] = pd.to_datetime(df['End Date'], format="%m/%d/%y")
df['Start Date'] = df['Start Date'].dt.normalize()
df['End Date'] = df['End Date'].dt.normalize()
df['Completion PCT'] = df['Completion PCT'].str.replace("%","").astype(float)

df = df.sort_values(by='Start Date',ascending=False)
dff = df

# Determine the start of each week
start_dates = pd.date_range(start='2024-02-26', end='2024-04-26', freq='W-MON')

# Create a DataFrame with start dates of each week
week_markers = pd.DataFrame({'Start Date': start_dates, 'Week_Start': True})

app = dash.Dash(__name__)
server=app.server

app.layout = html.Div([
    html.H1('Rival Roastery Expansion', style={'color': 'darkgoldenrod', 'fontSize': 40,'textAlign': 'center'}),
    html.Div(children=[
        dcc.Dropdown([x for x in sorted(dff['Project Section'].unique())],
                              value=['Green Bean System','Post Roast','Roaster','Buildout'],
                             clearable=False,
                             multi=True,
                             style={'width':'65%'},
                             id='section-dropdown'),
    ]),
    html.H3('hover over bars for additional detail', style={'color': 'dimgray', 'fontSize': 15,}),
    html.Div([
        dcc.RadioItems(
        id='week-selector',
        options=[
            {'label': 'All Weeks', 'value': 0},
            {'label': '2/12', 'value': 1},
            {'label': '2/26', 'value': 2},
            {'label': '3/4', 'value': 3},
            {'label': '3/11', 'value': 4},
            {'label': '3/18', 'value': 5},
            {'label': '3/25', 'value': 6},
            {'label': '4/1', 'value': 7},
            {'label': '4/8', 'value': 8},
            {'label': '4/15', 'value': 9},
        ],
        value=0,
        labelStyle={'display': 'inline-block'},
        inputStyle={"margin-left": "10px"},
    )]),
    html.Br(),
    html.Div(id='gantt-container'),
    html.Br(),
    html.Div([
        dash_table.DataTable(
            id='datatable-interactivity',
            data=dff.to_dict('records'),
            columns=[
                {"name": i, "id": i, "deletable": False, "selectable": False} for i in dff.columns
            ],
            editable=False,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            row_selectable="multi",
            row_deletable=False,
            selected_rows=[],
            page_action="native",
            page_current= 0,
            page_size= 6,
        )
    ]),
],className='row')


@app.callback(
    Output('datatable-interactivity', 'data'),
    [Input('section-dropdown', 'value'),
     Input('week-selector', 'value')]
)
def update_table(sect_v, selected_week):
    dff = df.copy()
    # Filter by section dropdown
    if sect_v:
        dff = dff[dff['Project Section'].isin(sect_v)]

    # Filter by week selector
    if selected_week == 0:
        return dff.to_dict('records')
    else:
        start_date = datetime.strptime('2024-02-16', '%Y-%m-%d') + timedelta(days=(int(selected_week) - 1) * 7)
        end_date = start_date + timedelta(days=6)
        filtered_df = dff[(dff['Start Date'] >= start_date) & (dff['Start Date'] <= end_date)]
        return filtered_df.to_dict('records')
        
# @app.callback(
#     Output('datatable-interactivity','data'),
#     Input("section-dropdown", "value")
# )

# def filter_table(sect_v):
#     dff = df.copy()
#     if sect_v :
#         dff = dff[dff["Project Section"].isin(sect_v)]
#         return dff.to_dict('records')
#     else :
#         return dff.to_dict('records')
#Gantt Chart

@app.callback(
#     Output('ganttchart', 'children'),
#     Input('datatable_id', 'selected_rows'),
#     Input("section-dropdown", "value")
     Output(component_id='gantt-container', component_property='children'),
     [Input(component_id='datatable-interactivity', component_property="derived_virtual_data"),
      Input(component_id='datatable-interactivity', component_property='derived_virtual_selected_rows'),
      Input(component_id='datatable-interactivity', component_property='derived_virtual_selected_row_ids'),
      Input(component_id='datatable-interactivity', component_property='selected_rows'),
      Input(component_id='datatable-interactivity', component_property='derived_virtual_indices'),
      Input(component_id='datatable-interactivity', component_property='derived_virtual_row_ids'),
      Input(component_id='datatable-interactivity', component_property='active_cell'),
      Input(component_id='datatable-interactivity', component_property='selected_cells'),
      ]
 )

def update_gantt(all_rows_data, slctd_row_indices, slct_rows_names, slctd_rows,
               order_of_rows_indices, order_of_rows_names, actv_cell, slctd_cell):

    print('***************************************************************************')
    print('Data across all pages pre or post filtering: {}'.format(all_rows_data))
    print('---------------------------------------------')
    print("Indices of selected rows if part of table after filtering:{}".format(slctd_row_indices))
    print("Names of selected rows if part of table after filtering: {}".format(slct_rows_names))
    print("Indices of selected rows regardless of filtering results: {}".format(slctd_rows))
    print('---------------------------------------------')
    print("Indices of all rows pre or post filtering: {}".format(order_of_rows_indices))
    print("Names of all rows pre or post filtering: {}".format(order_of_rows_names))
    print("---------------------------------------------")
    print("Complete data of active cell: {}".format(actv_cell))
    print("Complete data of all selected cells: {}".format(slctd_cell))

    dff = pd.DataFrame(all_rows_data)
    # dff.dropna(subset=['Start'], inplace=True)
    # dff['Budget Number'] = dff["Budget Number"].astype(float)
    # dff['Cost to Date'] = dff["Cost to Date"].astype(float)
    # dff['Progress'] = dff["Progress"].astype(float)
    dff['Pattern'] = dff['Completion PCT'].apply(lambda x: 'solid' if 0 < x < 100 else 'none')

    return [
        dcc.Graph(id='gantt-chart', figure=px.timeline(
            data_frame=dff,
            x_start="Start Date",
            x_end="End Date",
            y="Task",
            color='Completion PCT',
            hover_name='Task',
            hover_data='Crew',
            category_orders={"Project Section": ["Buildout", "Green Bean System", "Roaster", "Post Roast"]},
            color_continuous_scale='blackbody',
            color_continuous_midpoint=50,
            opacity=.5,
            pattern_shape='Pattern'
        ).update_layout(
            paper_bgcolor='whitesmoke',
            plot_bgcolor='whitesmoke',
            hovermode="closest",
            xaxis_title="Schedule",
            yaxis_title="Task",
            title_font_size=24,
            font_color='dimgray',
            hoverlabel=dict(
                bgcolor='gold',
                font_size=9,)
        ))

    ]



# def update_data(chosen_rows):
#     if len(chosen_rows)==0:
#         df_filterd = df[df['Project / Customer Name'].isin(['White Coffee','Cadillac Coffee','Rival','Stack Street - Yehuda'])]
#     else:
#         print(chosen_rows)
#         df_filterd = dff[dff.index.isin(chosen_rows)]


if __name__ == '__main__':
    app.run_server(debug=True)
