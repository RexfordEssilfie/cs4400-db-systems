# cs4400-db-systems



# Instructions

## Setup
First install requirements for the python project, using:
```commandline
pip3 install -r requirements.txt
```

You can set up the database as follows:
1. Copy the DDL from `airline_ddl.sql` and run it in workbench to create a new table.
2. Modify the script in `seeder.py` and `db.py` to use your username and password for you mysql database.


## Seeding
1. You can seed the database with existing fixtures from `airline.yml` as follows:

```commandline
python seeder.py
```


## Interactive
To have an interactive session with the terminal and to run some of the scripts we have setup,
you can run the `db.py` script in interactive mode as follows:

```commandline
python -i app/db.py
```

Some of the actions are available to you are the following:

```python
db.get_available_airlines() # fetch available airlines

db.create_user('John', 7, 'Doe', 'abc123', 'john@example.com') # create a user for airline no. 7

db.get_flights_from_to('ATL', 'JFK') # search flights from ATL to JFK OR
db.fetch_flights_between_airports_on_departure_date('ATL', 'JFK', '2022-09-12 12:30:00') # search flights from ATL to JFK on a specific date


db.get_available_tickets_by_flight_id(1) # Get a single flight by ID.


db.add_billing_detail(1, 1234, 'abcxyz') # Add billing details for user 1


db.create_passenger_from_user(1, 'asdfdsa') # Create a passenger entry for user 1

db.buy_single_ticket(1, 1, 1, 500, 'Success') # Buy a single ticket of price $500 with successful billing processor status
```


## Web App
To run the web app version, run the following script
```commandline
bash dev.sh
```
After this open the url from the terminal output. You can search for flights from 'ATL' to 'JFK',
which would have been seeded already in the previous stage.


