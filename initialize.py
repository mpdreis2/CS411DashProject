import mysql_utils

user = "root"
password = "root_user"
port = "127.0.0.1"

if __name__ == "__main__":
    mysql_utils.initialize_database(user, password, port)