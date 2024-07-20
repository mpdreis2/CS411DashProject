from dash import Dash, html, dash_table, dcc, callback, Output, Input, ctx, dash_table
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px
import mysql
import mysql_utils

app = Dash()
user = 'root'
password = 'root_user'
port = '127.0.0.1'

app.layout = html.Div([
    html.Div(children = 'Title'),
    
    html.Br(),
    
    html.Div([
        html.Div(children = "Enter an interest:"),
        dcc.Input(id="new_interest", type="text", placeholder=""),
        html.Button("Submit", id="submitNewInterest"),
        html.Br(),
        html.Div(id="interestList")
    ]),
    
    html.Div([

    ])
    
    
])
@callback(
    Output("interestList", "children"),
    Input("new_interest", "value"),
    Input("submitNewInterest", "n_clicks")
)
def add_interest(new_interest, n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    # else:
    #     mysql_utils.update_interest(user, password, port, new_interest)
    #     raise PreventUpdate
    #     n_clicks = None
    changed_id = [p['prop_id'] for p in ctx.triggered][0]
    if 'submitNewInterest' in changed_id:
        mysql_utils.update_interest(user, password, port, new_interest)
        print(f'{new_interest} add as an interest!')
        interestDf = mysql_utils.getIntrestList(user, password, port)
        return html.Div([dash_table.DataTable(data=interestDf.to_dict('records'))])

if __name__ == '__main__':
    mysql_utils.initialize_database(user, password, port)
    app.run(debug=True)