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

url='https://raw.githubusercontent.com/DuaneIndustries/RivalExpansion/main/RIval_Expansion_Calendar_v1.csv'
s=requests.get(url).content
df=pd.read_csv(io.StringIO(s.decode('utf-8')))

# df = pd.read_csv("/Users/caseyleo/Desktop/RIval_Project_Calendar.csv")



df['Start Date'] = pd.to_datetime(df['Start Date'], format="%m/%d/%y")
df['End Date'] = pd.to_datetime(df['End Date'], format="%m/%d/%y")
df['Start Date'] = df['Start Date'].dt.normalize()
df['End Date'] = df['End Date'].dt.normalize()
df['Completion PCT'] = df['Completion PCT'].str.replace("%","").astype(float)

dff = df

app = dash.Dash(__name__)
server=app.server

app.layout = html.Div([
    html.H1('Rival Roastery Expansion', style={'color': 'darkgoldenrod', 'fontSize': 40,'textAlign': 'center'}),
    html.Div(children=[
        dcc.Dropdown([x for x in sorted(dff['Project Section'].unique())],
                              value=[],
                             clearable=False,
                             multi=True,
                             style={'width':'65%'},
                             id='section-dropdown'),
    ]),
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
    Output('datatable-interactivity','data'),
    Input("section-dropdown", "value")
)

def filter_table(sect_v):
    dff = df.copy()
    if sect_v :
        dff = dff[dff["Project Section"].isin(sect_v)]
        return dff.to_dict('records')
    else :
        return dff.to_dict('records')
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
            opacity=.5
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
