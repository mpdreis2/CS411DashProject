import mysql.connector
import pandas as pd

#function to check if the modifications to the academic world db have been created already
def initialize_database(dbuser, dbpassword, dbport):
    cxn = mysql.connector.connect(user=dbuser, password=dbpassword, host = dbport, database = 'academicworld')
    cursor = cxn.cursor()

    cursor.execute("SHOW TABLES")
    result = cursor.fetchall()
    
    if "user_interests" not in [table[0] for table in result]:
        createTableQuery = """ CREATE TABLE user_interests (
        id INT NOT NULL,
        name VARCHAR(256) NOT NULL,
        PRIMARY KEY (id));
        """
        cursor.execute(createTableQuery)

    cursor.close()
    cxn.close()

def update_interest(dbuser, dbpassword, dbport, interest):
    cxn = mysql.connector.connect(user=dbuser, password=dbpassword, host = dbport, database = 'academicworld')
    cursor = cxn.cursor()
    query = 'INSERT INTO user_interests (id, name) VALUES ((SELECT max(id) + 1 FROM user_interests as i), "' + interest + '")'
    cursor.execute(query)
    cxn.commit()
    cursor.close()
    cxn.close()

def getIntrestList(dbuser, dbpassword, dbport):
    cxn = mysql.connector.connect(user=dbuser, password=dbpassword, host = dbport, database = 'academicworld')
    cursor = cxn.cursor()
    query = "SELECT name FROM user_interests"
    interestDf = pd.read_sql(query, cxn)
    
    return interestDf

if __name__ == "__main__":
    getIntrestList("root", "root_user", "127.0.0.1")
