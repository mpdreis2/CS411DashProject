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

        createTableQuery = """CREATE TABLE favorite_faculty (
            id INT NOT NULL,
            faculty_id int NOT NULL,
            PRIMARY KEY (ID),
            FOREIGN KEY (faculty_id) REFERENCES faculty(id));"""
        
        cursor.execute(createTableQuery)
    
        query = "CREATE INDEX keyword_index on keyword(name);"
        cursor.execute(query)

        query = """CREATE VIEW faculty_info AS
        SELECT faculty.name as Name, faculty.position as Position, faculty.email as Email, university.name as Intstitution, faculty.photo_url as facultyPhoto, university.photo_url as universityPhoto
        FROM faculty, university
        WHERE faculty.university_id = university.id;"""

        cursor.execute(query)
        
    
    # query = "SHOW INDEX FROM user_interests"
    # cursor.execute(query)
    # data = cursor.fetchall()
    # indexExists = False
    # for row in data:
    #     if "keyword_index" in row:
    #         indexExists = True
    # if indexExists == False:
    #     query = "CREATE INDEX keyword_index on keyword(name);"
    #     cursor.execute(query)

    
    

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
    query = "SELECT name AS Interest FROM user_interests"
    interestDf = pd.read_sql(query, cxn)
    
    return interestDf

def checkIfInterestExists(dbuser, dbpassword, dbport, interest):
    cxn = mysql.connector.connect(user=dbuser, password=dbpassword, host = dbport, database = 'academicworld')
    cursor = cxn.cursor()
    query = 'SELECT name FROM user_interests WHERE name = "' + interest + '"'
    cursor.execute(query)
    if len(cursor.fetchall()) > 0:
        cursor.close()
        cxn.close()
        return True
    

def deleteInterest(dbuser, dbpassword, dbport, interest):
    cxn = mysql.connector.connect(user=dbuser, password=dbpassword, host = dbport, database = 'academicworld')
    cursor = cxn.cursor()
    query = 'DELETE FROM user_interests WHERE name = "' + interest + '"'
    cursor.execute(query)
    cxn.commit()
    cursor.close()
    cxn.close()

def getTopFacultyByInterest(dbuser, dbpassword, dbport, interest):
    cxn = mysql.connector.connect(user=dbuser, password=dbpassword, host = dbport, database = 'academicworld')
    
    query = ''' SELECT faculty.name as Name, AVG(faculty_keyword.score) as Score, count(publication.title) as Publicaction_count
    FROM faculty, faculty_keyword, keyword, faculty_publication, publication
    WHERE faculty.id = faculty_keyword.faculty_id AND faculty_keyword.keyword_id = keyword.id
    AND faculty.id = faculty_publication.faculty_id AND faculty_publication.publication_id = publication.id
    AND keyword.name = "''' + interest + '''" GROUP BY Name ORDER BY Score DESC;
    '''
    facultyByInterst = pd.read_sql(query, cxn)
    cxn.close()
    return facultyByInterst

def addFavoriteFaculty(dbuser, dbpassword, dbport, facultyName):
    cxn = mysql.connector.connect(user=dbuser, password=dbpassword, host = dbport, database = 'academicworld')
    cursor = cxn.cursor()
    query = 'SELECT id FROM faculty WHERE name = "' + facultyName + '";'
    cursor.execute(query)
    newfacultyID = cursor.fetchall()[0][0]
    print(newfacultyID)
    query = 'SELECT MAX(id) FROM favorite_faculty'
    cursor.execute(query)
    nextID = cursor.fetchall()[0][0]
    if nextID == None:
        nextID = 0
    else:
        nextID += 1
    query = "INSERT INTO favorite_faculty VALUES (%s, %s)"
    cursor.execute(query, (nextID, newfacultyID))

    cxn.commit()
    cursor.close()
    cxn.close()

def getFavoriteFacultyDf(dbuser, dbpassword, dbport):
    cxn = mysql.connector.connect(user=dbuser, password=dbpassword, host = dbport, database = 'academicworld')
    cursor = cxn.cursor()
    query = "SELECT * FROM faculty_info WHERE faculty_info.id IN (SELECT faculty_id from favorite_faculty)"
    df = pd.read_sql(query, cxn)
    
    return df


if __name__ == "__main__":

    getFavoriteFacultyDf("root", "root_user", "127.0.0.1")
