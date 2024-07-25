from pymongo import MongoClient
import pandas as pd

def getDatabase(): 
    CONN_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.5"
    client = MongoClient(CONN_STRING)
    return client["academicworld"]

if __name__ == "__main__":
    db = getDatabase()
    for item in db.faculty.find():
        print(item)
