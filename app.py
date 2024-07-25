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
        html.Div(children = "Remove an interest:"),
        dcc.Input(id="removeInterest", type="text", placeholder=""),
        html.Button("Delete", id="deleteInterest"),
        html.Br(),
        html.Div(id="interestList")
    ]),
    
    html.Div(children = [dcc.RadioItems(options = mysql_utils.getIntrestList(user, password, port)["Interest"].to_list(),
    value = mysql_utils.getIntrestList(user, password, port)["Interest"].to_list()[0], id = "interest_radio_items")], 
    id = "faculty_by_interests_radioitems"),

    html.Div(id = "top_faculty_by_interest_table")

])
@callback(
    Output("interestList", "children"),
    Input("new_interest", "value"),
    Input("removeInterest", "value"),
    Input("submitNewInterest", "n_clicks"),
    Input("deleteInterest", "n_clicks")
)
def add_interest(new_interest, removeInterest, n_clicks, deleteClicks):
    if n_clicks is None:
        raise PreventUpdate

    changed_id = [p['prop_id'] for p in ctx.triggered][0]
    if 'submitNewInterest' in changed_id:
        mysql_utils.update_interest(user, password, port, new_interest)
        print(f'{new_interest} add as an interest!')
        interestDf = mysql_utils.getIntrestList(user, password, port)
        return html.Div([dash_table.DataTable(data=interestDf.to_dict('records'))])
    if 'deleteInterest' in changed_id:
        if mysql_utils.checkIfInterestExists(user, password, port, removeInterest):
            mysql_utils.deleteInterest(user,password, port, removeInterest)
        interestDf = mysql_utils.getIntrestList(user, password, port)
        return html.Div([dash_table.DataTable(data=interestDf.to_dict('records'))])

@callback(
    Output("faculty_by_interests_radioitems", "children"),
    Input("submitNewInterest", "n_clicks"),
    Input("deleteInterest", "n_clicks")
)
def updateInterstRadioItems(n_clicks, deleteClicks):
    changed_id = [p['prop_id'] for p in ctx.triggered][0]
    if 'submitNewInterest' in changed_id:
        return html.Div(children = [dcc.RadioItems(options = mysql_utils.getIntrestList(user, password, port)["Interest"].to_list(),
    value = mysql_utils.getIntrestList(user, password, port)["Interest"].to_list()[0], id = "interest_radio_items")], 
    id = "faculty_by_interests_radioitems")
    if 'deleteInterest' in changed_id:
        return html.Div(children = [dcc.RadioItems(options = mysql_utils.getIntrestList(user, password, port)["Interest"].to_list(),
    value = mysql_utils.getIntrestList(user, password, port)["Interest"].to_list()[0], id = "interest_radio_items")], 
    id = "faculty_by_interests_radioitems")


@callback(
    Output("top_faculty_by_interest_table", "children"),
    Input("interest_radio_items", "value")
)
def updateFacultyByInterest(selectedValue):
    topFacultyDf = mysql_utils.getTopFacultyByInterest(user, password, port, selectedValue)
    return html.Div(children = [dash_table.DataTable(data = topFacultyDf.to_dict('records'))])



if __name__ == '__main__':
    mysql_utils.initialize_database(user, password, port)
    app.run(debug=True)