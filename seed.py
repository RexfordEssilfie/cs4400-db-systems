from datetime import date, datetime, timedelta
import mysql.connector


def create_db_connection(user=None, password=None, db=None):
    cnx = mysql.connector.connect(user=user, database=db, password=password)
    return cnx


def create_airlines(cursor):

    cursor.execute("DELETE FROM Airline")

    create_airline_procedure = "CALL airline_db.create_airline(%s, %s,%s);"

    airlines_data = [
        ("United Airlines", "Atlanta", "GA"),
        ("Alaska Airlines", "Alaska", "AL"),
        ("South West Airlines", "Chicago", "IL"),
        ("Frontier", "New York", "NY")
    ]

    for data in airlines_data:
        cursor.execute(create_airline_procedure, data)

    return get_airlines(cursor)


def get_airlines(cursor):
    cursor.execute("SELECT * FROM Airline")
    return cursor.fetchall()


def create_classes_for_airline(airline, cursor):
    pass


def main():
    connection = create_db_connection(
        user='root', password='mysqladmin', db='airline_db')

    cursor = connection.cursor()

    airlines = create_airlines(cursor)

    for airline in airlines:
        create_classes_for_airline(airline)

    # Make sure data is committed to the database
    connection.commit()
    cursor.close()
    connection.close()


if __name__ == '__main__':
    main()
