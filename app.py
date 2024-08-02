from dash import Dash, html, dash_table, dcc, callback, Output, Input, ctx, dash_table
import pandas as pd
import plotly.express as px
import mysql_utils
import neo4j_utils
import mongo_utils
import time

app = Dash(__name__)
user = 'root'
password = 'root_user'
port = '127.0.0.1'


def getFavoriteFacutlyDivList(dbuser, dbpassword, port):
    df = mysql_utils.getFavoriteFacultyDf(dbuser, dbpassword, port)
    divList = []
    divList.append(html.Div(className = "row_item", children = [
            html.Div(className = "column_item", children = html.H2("Photo")),
            html.Div(className = "column_item", children = html.H2("Name")),
            html.Div(className = "column_item", children = html.H2("Email")),
            html.Div(className = "column_item", children = html.H2("Univeristy")),
    ]))
    for i in df.index:
        divList.append(html.Div(className = "row_item", children = [
            html.Div(className = "column_item", children=[html.Img(className = 'row_image', src = df["facultyPhoto"][i])]),
            html.Div(className = "column_item", children = [df["Name"][i]]),
            html.Div(className = "column_item", children = [df["Email"][i]]),
            html.Div(className = "column_item", children = [html.Img(className = 'row_image', src = df["universityPhoto"][i])]),
            ]))
    return divList

app.layout = html.Div([
    html.Div(children = [html.H1("Interest Tracker"), html.P("Welcome to Interest Tracker, and app to add your academic interests and find faculty, publications, or univerisities that match your interests.")]),
    
    html.Br(),
    
    
    #Widget 1: Form for adding or deleting intrests, which displays the current interests in a table
    html.Div(className = "widget", children = [
        html.Div(className = 'widget_header', children = [html.H1("Interest List"), html.P("Enter and remove interests here. These interests will be used to help make connections in the academic world.")]),
        html.Div(className = 'widget_2_component', children = [
            html.Div(children = [

            html.Div(children = "Enter an interest:"),
            dcc.Input(id="new_interest", type="text", placeholder=""),
            html.Button("Submit", id="submitNewInterest"),
            html.Div(children = "Remove an interest:"),
            dcc.Input(id="removeInterest", type="text", placeholder=""),
            html.Button("Delete", id="deleteInterest"),

            ]),

            html.Div(id="interestList"),
        ]),
    ]),

    #Widget 2: Graph of intresets and number of associated faculty and number of associated publications
    html.Div(className = 'widget', children = [
        html.Div(className = 'widget_header', children = [html.H1("Most Popular Interests"), html.P("Choose to see a graph of number of faculty who share an intrest or publications about an interest")]),
        html.Div(className = 'widget_2_component', children = [
            html.Div(children = [dcc.RadioItems(options = ["NumberOfFaculty", "NumberOfPublications"],
            value = "NumberOfFaculty", id = "faculty_or_pubs_items")]),
            html.Div(id = "faculty_or_pubs_graph")
        ]),
    ]),

    #Widget 3: Table of faculty also interested in the selected intesest
    html.Div(className = 'widget', children = [
        html.Div(className = 'widget_header', children = [html.H1("Top Faculty"), html.P("Choose an intersest to see top rated faculty in that field.")]),
        html.Div(className = 'widget_2_component', children = [
            html.Div(children = [dcc.RadioItems(options = mysql_utils.getIntrestList(user, password, port)["Interest"].to_list(),
            value = mysql_utils.getIntrestList(user, password, port)["Interest"].to_list()[0], id = "interest_radio_items")], 
            id = "faculty_by_interests_radioitems"),

            html.Div(id = "top_faculty_by_interest_table")
        ]),
    ]),

    #Widget 4: Tracks favorite faculty and their contact info
    html.Div(className = 'widget', children = [
        html.Div(className = 'widget_header', children = [html.H1("Faculty Tracker"), html.P('Enter a faculty name to save there info.')]),
        html.Div(className = 'widget_2_component', children = [
            html.Div([
            html.Div(children = "Favorite Faculty"),
            html.Div(children = "Add favorite faculty by name:"),
            dcc.Input(id="new_faculty", type="text", placeholder=""),
            html.Button("Submit", id="submitNewFaculty"),
            html.Div(children = "Remove faculty:"),
            dcc.Input(id="removeFaculty", type="text", placeholder=""),
            html.Button("Delete", id="deleteFaculty"),
            html.Br(),
            ]),
            html.Div(getFavoriteFacutlyDivList(user, password, port), id = "list_of_favorite_faculty"),
        ]),
    ]),

    #Widget 5: publication list with radio items to select most recent or most relevant
    html.Div(className = 'widget', children = [
        html.Div(className = 'widget_header', children = [html.H1("Top Publications"), html.P("See most recent or most relevant publications related to your interests.")]),
        html.Div(className = 'widget_2_component', children = [
            html.Div(children = [dcc.RadioItems(options = ["Most Recent", "Most Relevant"],
            value = "Most Recent", id = "pubs_by_year_or_score")]),
            html.Div(id = "pubs_by_year_or_score_table")
        ]),
    ]),

    #Widget 6: graph of universities with most faculty sharing user interests
    html.Div(className = 'widget', children = [
        html.Div(className = 'widget_header', children = [html.H1("Top Universities"), html.P("See which universities have the most faculty that share at least one of your interests.")]),
        html.Div(id = "graph_of_universities", children = [dcc.Graph(figure=px.histogram(mysql_utils.getUniversityDf(user, password, port), x="University", y="FacultyNumber" ))]),
    ]),

    



])

#callback funciton to update and delete interests for Widget 1
@callback(
    Output("interestList", "children"),
    Input("new_interest", "value"),
    Input("removeInterest", "value"),
    Input("submitNewInterest", "n_clicks"),
    Input("deleteInterest", "n_clicks")
)
def add_interest(new_interest, removeInterest, n_clicks, deleteClicks):
    if n_clicks is None and deleteClicks is None:
        
        interestDf = mysql_utils.getIntrestList(user, password, port)
        return html.Div([dash_table.DataTable(data=interestDf.to_dict('records'), style_cell={'textAlign':'left'})])

    changed_id = [p['prop_id'] for p in ctx.triggered][0]
    if 'submitNewInterest' in changed_id:
        mysql_utils.update_interest(user, password, port, new_interest)
        print(f'{new_interest} add as an interest!')
        interestDf = mysql_utils.getIntrestList(user, password, port)
        return html.Div([dash_table.DataTable(data=interestDf.to_dict('records'), style_cell={'textAlign':'left'})])
    if 'deleteInterest' in changed_id:
        if mysql_utils.checkIfInterestExists(user, password, port, removeInterest):
            mysql_utils.deleteInterest(user, password, port, removeInterest)
            print(f'{new_interest} deleted')
        interestDf = mysql_utils.getIntrestList(user, password, port)
        return html.Div([dash_table.DataTable(data=interestDf.to_dict('records'), style_cell={'textAlign':'left'})])

#callback to update the interest radio items as interests are added or deleted for Widget 3:
@callback(
    Output("faculty_by_interests_radioitems", "children"),
    Input("submitNewInterest", "n_clicks"),
    Input("deleteInterest", "n_clicks")
)
def updateInterstRadioItems(n_clicks, deleteClicks):
    changed_id = [p['prop_id'] for p in ctx.triggered][0]
    time.sleep(1)
    if n_clicks is None:
        return html.Div(children = [dcc.RadioItems(options = mysql_utils.getIntrestList(user, password, port)["Interest"].to_list(),
    value = mysql_utils.getIntrestList(user, password, port)["Interest"].to_list()[0], id = "interest_radio_items")], 
    id = "faculty_by_interests_radioitems")
    if 'submitNewInterest' in changed_id:
        return html.Div(children = [dcc.RadioItems(options = mysql_utils.getIntrestList(user, password, port)["Interest"].to_list(),
    value = mysql_utils.getIntrestList(user, password, port)["Interest"].to_list()[0], id = "interest_radio_items")], 
    id = "faculty_by_interests_radioitems")
    if 'deleteInterest' in changed_id:
        return html.Div(children = [dcc.RadioItems(options = mysql_utils.getIntrestList(user, password, port)["Interest"].to_list(),
    value = mysql_utils.getIntrestList(user, password, port)["Interest"].to_list()[0], id = "interest_radio_items")], 
    id = "faculty_by_interests_radioitems")


#Callback that returns the top faculty based on therest selected from radio menu in Wdiget 3
@callback(
    Output("top_faculty_by_interest_table", "children"),
    Input("interest_radio_items", "value")
)
def updateFacultyByInterest(selectedValue):
    topFacultyDf = mysql_utils.getTopFacultyByInterest(user, password, port, selectedValue)
    return html.Div(children = [dash_table.DataTable(data = topFacultyDf.to_dict('records'), page_size=10)])

#callback to update widget 2 when a radio item is changed
@callback(
    Output("faculty_or_pubs_graph", "children"),
    Input("faculty_or_pubs_items", "value")
)
def updateFacultyOfPubGraph(selection):
    df = neo4j_utils.getFacAndPubCountsByInterest()

    return html.Div([dcc.Graph(figure=px.histogram(df, x="Interest", y=selection))])

#callback to get the list of intersting publications as interest cahnges
@callback(
    Output("pubs_by_year_or_score_table", "children"),
    Input("pubs_by_year_or_score", "value")
)
def getTableOfPubsByYearOrScore(selection):
    interestList = mysql_utils.getIntrestList(user, password, port)["Interest"].to_list()
    if selection == "Most Recent":
        df = mongo_utils.getPubsByYear(interestList)
        return html.Div(children = [dash_table.DataTable(data = df.to_dict('records'), style_cell={"text_align":"left", "whiteSpace":"normal"})])
    elif selection == "Most Relevant":
        df = mongo_utils.getPubsByScore(interestList)
        return html.Div(children = [dash_table.DataTable(data = df.to_dict('records'), style_cell={"text_align":"left", "whiteSpace":"normal"})])

#Callback for widget 5 to add or remove faculty
@callback(
    Output("list_of_favorite_faculty", "children"),
    Input("new_faculty", "value"),
    Input("removeFaculty", "value"),
    Input("submitNewFaculty", "n_clicks"),
    Input("deleteFaculty", "n_clicks")
)
def add_interest(new_faculty, removeFaculty, n_clicks, deleteClicks):
    if n_clicks is None:
        
        return getFavoriteFacutlyDivList(user, password, port)
        

    changed_id = [p['prop_id'] for p in ctx.triggered][0]
    if 'submitNewFaculty' in changed_id:
        mysql_utils.addFavoriteFaculty(user, password, port, new_faculty)
        return getFavoriteFacutlyDivList(user, password, port)
    if 'deleteFaculty' in changed_id:
        mysql_utils.removeFavoriteFacaulty(user, password, port, removeFaculty)
        return getFavoriteFacutlyDivList(user, password, port)

@callback(
    Output("graph_of_universities", "children"),
    Input("submitNewInterest", "n_clicks"),
    Input("deleteInterest", "n_clicks")
)
def getUniversityGraph(n_clicks, deleteClicks):

    if n_clicks is None and deleteClicks is None:
        df = mysql_utils.getUniversityDf(user, password, port)
        return html.Div(id = "graph_of_universities", children = [dcc.Graph(figure=px.histogram(df, x="University", y="FacultyNumber"))])
    changed_id = [p['prop_id'] for p in ctx.triggered][0]
    if 'submitNewInterest' in changed_id:
        df = mysql_utils.getUniversityDf(user, password, port)
        return html.Div(id = "graph_of_universities", children = [dcc.Graph(figure=px.histogram(df, x="University", y="FacultyNumber"))])
    if 'deleteInterest' in changed_id:
        df = mysql_utils.getUniversityDf(user, password, port)
        return html.Div(id = "graph_of_universities", children = [dcc.Graph(figure=px.histogram(df, x="University", y="FacultyNumber"))])

if __name__ == '__main__':
    app.run(debug = True)
    