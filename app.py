from dash import Dash, html, dash_table, dcc, callback, Output, Input, ctx, dash_table
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px
import mysql
import mysql_utils
import neo4j_utils
import mongo_utils
import time

app = Dash()
user = 'root'
password = 'root_user'
port = '127.0.0.1'

app.layout = html.Div([
    html.Div(children = 'Title'),
    
    html.Br(),
    
    #form for adding or deleting records
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

    #graph of intresets by number of associated faculty and number of associated publications
    html.Div([
        html.Div(children = [dcc.RadioItems(options = ["NumberOfFaculty", "NumberOfPublications"],
        value = "NumberOfFaculty", id = "faculty_or_pubs_items")]),
        html.Div(id = "faculty_or_pubs_graph")
    ]),

    #table of faculty also interested in the selected intesestt
    html.Div([
        html.Div(children = [dcc.RadioItems(options = mysql_utils.getIntrestList(user, password, port)["Interest"].to_list(),
        value = mysql_utils.getIntrestList(user, password, port)["Interest"].to_list()[0], id = "interest_radio_items")], 
        id = "faculty_by_interests_radioitems"),

        html.Div(id = "top_faculty_by_interest_table")
    ]),

    #publication list with radio items to select most recent or most relevant
    html.Div([
        html.Div(children = [dcc.RadioItems(options = ["Most Recent", "Most Relevant"],
        value = "Most Recent", id = "pubs_by_year_or_score")]),
        html.Div(id = "pubs_by_year_or_score_table")
    ]),



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
        
        interestDf = mysql_utils.getIntrestList(user, password, port)
        return html.Div([dash_table.DataTable(data=interestDf.to_dict('records'))])

    changed_id = [p['prop_id'] for p in ctx.triggered][0]
    if 'submitNewInterest' in changed_id:
        mysql_utils.update_interest(user, password, port, new_interest)
        print(f'{new_interest} add as an interest!')
        interestDf = mysql_utils.getIntrestList(user, password, port)
        return html.Div([dash_table.DataTable(data=interestDf.to_dict('records'))])
    if 'deleteInterest' in changed_id:
        if mysql_utils.checkIfInterestExists(user, password, port, removeInterest):
            mysql_utils.deleteInterest(user, password, port, removeInterest)
            print(f'{new_interest} deleted')
        interestDf = mysql_utils.getIntrestList(user, password, port)
        return html.Div([dash_table.DataTable(data=interestDf.to_dict('records'))])

@callback(
    Output("faculty_by_interests_radioitems", "children"),
    Input("submitNewInterest", "n_clicks"),
    Input("deleteInterest", "n_clicks")
)
def updateInterstRadioItems(n_clicks, deleteClicks):
    changed_id = [p['prop_id'] for p in ctx.triggered][0]
    time.sleep(1)
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


@callback(
    Output("faculty_or_pubs_graph", "children"),
    Input("faculty_or_pubs_items", "value")
)
def updateFacultyOfPubGraph(selection):
    df = neo4j_utils.getFacAndPubCountsByInterest()

    return html.Div([dcc.Graph(figure=px.histogram(df, x="Interest", y=selection))])

@callback(
    Output("pubs_by_year_or_score_table", "children"),
    Input("pubs_by_year_or_score", "value")
)
def getTableOfPubsByYearOrScore(selection):
    interestList = mysql_utils.getIntrestList(user, password, port)["Interest"].to_list()
    if selection == "Most Recent":
        df = mongo_utils.getPubsByYear(interestList)
        return html.Div(children = [dash_table.DataTable(data = df.to_dict('records'))])
    elif selection == "Most Relevant":
        df = mongo_utils.getPubsByScore(interestList)
        return html.Div(children = [dash_table.DataTable(data = df.to_dict('records'))])


if __name__ == '__main__':
    mysql_utils.initialize_database(user, password, port)
    app.run(debug=True)