from neo4j import GraphDatabase, Result
import pandas as pd
import mysql_utils

#neo4j query to get count of faculty and publication sharing a user interest:
def getFacAndPubCountsByInterest():
    address="neo4j://localhost:7687"
    auth=('neo4j', "ilovecs411")
    driver = GraphDatabase.driver(address, auth=auth)

    interestList = mysql_utils.getIntrestList("root", "root_user", "127.0.0.1")["Interest"].to_list()
    query = """MATCH (faculty:FACULTY)-[interest:INTERESTED_IN]->(keyword:KEYWORD)<-[label:LABEL_BY]-(pub:PUBLICATION)
    WHERE keyword.name IN $interestList
    RETURN keyword.name AS Interest, COUNT(DISTINCT faculty) AS NumberOfFaculty, COUNT(DISTINCT pub) AS NumberOfPublications
    ORDER BY NumberOfFaculty DESC"""
    df = driver.execute_query(query, interestList = interestList, database_ = "academicworld", 
    result_transformer_=Result.to_df)
    return df
