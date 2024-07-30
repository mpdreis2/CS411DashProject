import mysql.connector
import pandas as pd
from sqlalchemy import create_engine, text

def print_data():
    cnx = mysql.connector.connect(user='root', password='root_user', host = "127.0.0.1", database = 'academicworld')
    cursor = cnx.cursor()

    query = "SHOW INDEX FROM keyword"


    cursor.execute(query)
    data =cursor.fetchall()
    print(data[1])
    if "keyword_index" in data[1]:
        print('got it')
    

    
    
    cursor.close()
   # df = pd.read_sql("SELECT * FROM user_interests LIMIT 10", cnx)
    #print(df.head())

    cnx.close()

def sqlalchemy_connect():
    connection_string = 'mysql+mysqlconnector://root:root_user@127.0.0.1/academicworld'
    engine = create_engine(connection_string)
    t = text("SELECT name FROM faculty LIMIT 10")
    with engine.connect() as con:
        df = pd.read_sql(t, con)
    print(df.head())


if __name__ == "__main__":
    print_data()
