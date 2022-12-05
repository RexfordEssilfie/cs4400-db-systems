from datetime import date, datetime, timedelta
import mysql
import mysql.connector


def create_db_connection(user=None, password=None, db=None):
    cnx = mysql.connector.connect(user=user, database=db, password=password)
    return cnx


def create_airlines(cursor):

    cursor.execute("DELETE FROM Airline") #why ????

    create_airline_procedure = "CALL airline_db.create_airline(%s, %s,%s,%s);"
   #name,code,city,state
    airlines_data = [
        ("United Airlines","UA12" ,"Atlanta", "GA"),
        ("Alaska Airlines","AA12" ,"Alaska", "AL"),
        ("South West Airlines","SWA1" ,"Chicago", "IL"),
        ("Frontier","FA12" ,"New York", "NY")
    ]

    for data in airlines_data:
        cursor.execute(create_airline_procedure, data)

    return get_airlines(cursor) 


def get_airlines(cursor):
    cursor.execute("SELECT * FROM Airline")
    return cursor.fetchall()

######## AirCraft #######

def create_aircrafts( cursor):  #would it be (airline, cursor)? like you are doing for class?

    cursor.execute("DELETE FROM Aircraft")

    create_aircrafts_procedure = "CALL airline_db.create_aircrafts(%s,%s);"
    #airline_id, name, model, capacity
    aircrafts_data = [
        (9, "UA11"),
        ( 10, "Alaska12"),
        ( 11, "Ch13"),
        ( 12, "NY14")
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
        #user='root', password='mysqladmin', db='airline_db')
        user='root', password='root3069', db='airline_db')

    cursor = connection.cursor()
   
    #create_airlines(cursor)
    create_aircrafts(cursor)

    
    #create_classes_for_airline(cursor)

    # Make sure data is committed to the database
    connection.commit()
    cursor.close()
    connection.close()


if __name__ == '__main__':
    main()
