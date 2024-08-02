import mysql.connector
import pandas as pd

#function to check if the modifications to the academic world db have been created already
def initialize_database(dbuser, dbpassword, dbport):
    cxn = mysql.connector.connect(user=dbuser, password=dbpassword, host = dbport, database = 'academicworld')
    cursor = cxn.cursor()

    cursor.execute("SHOW TABLES")
    result = cursor.fetchall()
    
    # if "user_interests" not in [table[0] for table in result]:
    createTableQuery = """ CREATE TABLE user_interests (
    id INT NOT NULL,
    name VARCHAR(256) NOT NULL,
    PRIMARY KEY (id));
    """
    cursor.execute(createTableQuery)

    query = "INSERT INTO user_interests VALUES (%s, %s)"
    cursor.execute(query, (0, "databases"))

    createTableQuery = """CREATE TABLE favorite_faculty (
        id INT NOT NULL,
        faculty_id int NOT NULL,
        PRIMARY KEY (ID),
        FOREIGN KEY (faculty_id) REFERENCES faculty(id));"""
    
    cursor.execute(createTableQuery)

    query = "CREATE INDEX keyword_index on keyword(name);"
    cursor.execute(query)

    query = """CREATE VIEW faculty_info AS
    SELECT faculty.id, faculty.name as Name, faculty.position as Position, faculty.email as Email, university.name as Intstitution, faculty.photo_url as facultyPhoto, university.photo_url as universityPhoto
    FROM faculty, university
    WHERE faculty.university_id = university.id;"""

    cursor.execute(query)
    
    cxn.commit()
    cursor.close()
    cxn.close()

    return True

#fxn to add an interst to the user_interest table:
def update_interest(dbuser, dbpassword, dbport, interest):
    cxn = mysql.connector.connect(user=dbuser, password=dbpassword, host = dbport, database = 'academicworld')
    cursor = cxn.cursor()
    query = "SELECT max(id) FROM user_interests"
    cursor.execute(query)
    nextID = cursor.fetchall()[0][0]
    if nextID == None:
        nextID = 0
    else:
        nextID += 1
    
    query = 'INSERT INTO user_interests (id, name) VALUES (%s, %s)'
    cursor.execute(query, (nextID, interest))
    cxn.commit()
    cursor.close()
    cxn.close()

#fxn to retrun datafram consiting of the user_interests
def getIntrestList(dbuser, dbpassword, dbport):
    cxn = mysql.connector.connect(user=dbuser, password=dbpassword, host = dbport, database = 'academicworld')
    cursor = cxn.cursor()
    query = "SELECT name AS Interest FROM user_interests"
    interestDf = pd.read_sql(query, cxn)
    
    return interestDf

#fxn to check if an interest exists before attempting to delete:
def checkIfInterestExists(dbuser, dbpassword, dbport, interest):
    cxn = mysql.connector.connect(user=dbuser, password=dbpassword, host = dbport, database = 'academicworld')
    cursor = cxn.cursor()
    query = 'SELECT name FROM user_interests WHERE name = "' + interest + '"'
    cursor.execute(query)
    if len(cursor.fetchall()) > 0:
        cursor.close()
        cxn.close()
        return True
    
#fxn to delete interest from user_interests
def deleteInterest(dbuser, dbpassword, dbport, interest):
    cxn = mysql.connector.connect(user=dbuser, password=dbpassword, host = dbport, database = 'academicworld')
    cursor = cxn.cursor()
    query = 'DELETE FROM user_interests WHERE name = %s'
    cursor.execute(query, (interest,))
    cxn.commit()
    cursor.close()
    cxn.close()

#returns as datafram of faculty with associated user interst, ranked by score, as well as count of publications:
def getTopFacultyByInterest(dbuser, dbpassword, dbport, interest):
    cxn = mysql.connector.connect(user=dbuser, password=dbpassword, host = dbport, database = 'academicworld')
    
    query = ''' SELECT faculty.name as Name, AVG(faculty_keyword.score) as Score, count(publication.title) as Publication_count
    FROM faculty, faculty_keyword, keyword, faculty_publication, publication
    WHERE faculty.id = faculty_keyword.faculty_id AND faculty_keyword.keyword_id = keyword.id
    AND faculty.id = faculty_publication.faculty_id AND faculty_publication.publication_id = publication.id
    AND keyword.name = "''' + interest + '''" GROUP BY Name ORDER BY Score DESC;
    '''
    facultyByInterst = pd.read_sql(query, cxn)
    cxn.close()
    return facultyByInterst

#fxn to add a faculty to the favoreite_faculty table:
def addFavoriteFaculty(dbuser, dbpassword, dbport, facultyName):
    cxn = mysql.connector.connect(user=dbuser, password=dbpassword, host = dbport, database = 'academicworld')
    cursor = cxn.cursor()
    #fisr find faculty id from name:
    query = 'SELECT id FROM faculty WHERE name = "' + facultyName + '";'
    cursor.execute(query)
    newfacultyID = cursor.fetchall()[0][0]
    
    #get next id number:
    query = 'SELECT MAX(id) FROM favorite_faculty'
    cursor.execute(query)
    nextID = cursor.fetchall()[0][0]
    if nextID == None:
        nextID = 0
    else:
        nextID += 1
    
    #insert id and facutly_id into table:
    query = "INSERT INTO favorite_faculty VALUES (%s, %s)"
    cursor.execute(query, (nextID, newfacultyID))

    cxn.commit()
    cursor.close()
    cxn.close()

#get df of favorite facultyL
def getFavoriteFacultyDf(dbuser, dbpassword, dbport):
    cxn = mysql.connector.connect(user=dbuser, password=dbpassword, host = dbport, database = 'academicworld')
    cursor = cxn.cursor()
    query = "SELECT * FROM faculty_info WHERE faculty_info.id IN (SELECT faculty_id from favorite_faculty)"
    df = pd.read_sql(query, cxn)
    
    return df

#get df of universities and respective count fo faculty sharing an interest with the user:
def getUniversityDf(dbuser, dbpassword, dbport):
    cxn = mysql.connector.connect(user=dbuser, password=dbpassword, host = dbport, database = 'academicworld')
    cursor = cxn.cursor()
    query = """SELECT university.name AS University, COUNT(DISTINCT faculty.name) FacultyNumber
    FROM faculty, university, keyword, faculty_keyword
    WHERE faculty.id = faculty_keyword.faculty_id AND faculty.university_id = university.id
    AND faculty_keyword.keyword_id = keyword.id AND keyword.name IN (SELECT name FROM user_interests)
    GROUP BY University
    ORDER BY FacultyNumber DESC LIMIT 10;"""
    df = pd.read_sql(query, cxn)
    cursor.close()
    cxn.close()
    return df

#function to delete favorite faculty:
def removeFavoriteFacaulty(dbuser, dbpassword, dbport, facultyToDelete):
    cxn = mysql.connector.connect(user=dbuser, password=dbpassword, host = dbport, database = 'academicworld')
    cursor = cxn.cursor()

    query = "SELECT faculty.id FROM faculty WHERE faculty.name = %s"

    cursor.execute(query, (facultyToDelete,))
    facultyId = cursor.fetchall()[0][0]
    
    query = ("DELETE FROM favorite_faculty WHERE faculty_id = %s")
    cursor.execute(query, (facultyId,))
    cxn.commit()
    cursor.close()
    cxn.close()

