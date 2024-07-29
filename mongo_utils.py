from pymongo import MongoClient
import pandas as pd
import mysql_utils

def getDatabase(): 
    CONN_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.5"
    client = MongoClient(CONN_STRING)
    return client["academicworld"]

def getPubsByYear(interestList):
    db = getDatabase()
    result = db.publications.aggregate([{ "$unwind": "$keywords" }, { "$match": { "keywords.name": { "$in": interestList } } }, { "$sort": { "year": -1 } }, { "$limit": 10 }, { "$project": { "_id": 0, "title": 1 , "year":1, "keywords.name":1 } }])
    df = pd.json_normalize(list(result))
    return df

def getPubsByScore(interestList):
    db = getDatabase()
    result = db.publications.aggregate([{ "$unwind": "$keywords" }, { "$match": { "keywords.name": { "$in": interestList } } }, { "$sort": { "keywords.score": -1 } }, { "$limit": 10 }, { "$project": { "_id": 0, "title": 1 , "keywords.score":1, "keywords.name":1 } }])
    df = pd.json_normalize(list(result))
    return df


if __name__ == "__main__":
    print(getPubsByScore(mysql_utils.getIntrestList("root", "root_user", "127.0.0.1")["Interest"].to_list()))
