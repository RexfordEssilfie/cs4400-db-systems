from datetime import date, datetime, timedelta
import mysql.connector


def create_db_connection(user=None, password=None, db=None):
    cnx = mysql.connector.connect(user=user, database=db, password=password)
    return cnx


def create_airlines(cursor):

    cursor.execute("DELETE FROM Airline") #why ????

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

######## AirCraft #######

def create_aircrafts(airline, cursor):  #would it be (airline, cursor)? like you are doing for class?

    cursor.execute("DELETE FROM Aircraft")

    create_aircrafts_procedure = "CALL airline_db.Aircraft(%s,%s,%d);"
    #airline_id, name, model, capacity
    aircrafts_data = [
        ("UA", "UA11", 100),
        ( "AA", "Alaska12", 120),
        ( "SW", "Ch13", 130),
        ( "Frontier", "NY14", 180)
    ]

    for data in aircrafts_data:
        cursor.execute(create_aircrafts_procedure, data)

    return get_airlines(cursor) 


def get_aircrafts(cursor):
    cursor.execute("SELECT * FROM Aircraft")
    return cursor.fetchall()


###### Class #######

def create_classes_for_airline(cursor):
    create_class_procedure= "CALL airline_db.Class(%d,%s);"
    class_data=[(1,"First Class"),
                (2,"Business Class"),
                (3, "Economy Class")
    ]
    for data in class_data:
        cursor.execute(create_class_procedure, class_data)
        
    return get_classes(cursor)

def get_classes(cursor):
    cursor.execute("SELECT * FROM Class")
    return cursor.fetchall()

def main():
    connection = create_db_connection(
        user='root', password='mysqladmin', db='airline_db')

    cursor = connection.cursor()

    airlines = create_airlines(cursor)

    
    create_classes_for_airline(cursor)

    # Make sure data is committed to the database
    connection.commit()
    cursor.close()
    connection.close()


if __name__ == '__main__':
    main()
