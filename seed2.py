

import mysql.connector
import yaml
import re


class FixtureQuery:
  GET = 'get'  # A get query selects a record by a primary key
  SET = 'set'  # A set query inserts a record


class Fixture:
  def __init__(self):
    self.fixture = {}  # the fixture as loaded from the .yml file
    self.queries = {}  # queries for fetching/loading entities

    # stores the primary key values for each record if needed by some other entity
    self.record_keys = {}

    # store the list of table names as parsed from the .yml file top level keys
    self.fixture_table_names = []

  def connect(self, user=None, db=None, password=None):
    """
    Establishes a database connection.
    """
    self.connection = mysql.connector.connect(
        user=user, database=db, password=password)  # connect to a database

    # create cursor with dictionary=True to get results as a dictionary
    self.cursor = self.connection.cursor(dictionary=True)

    # for convenience, autocommit all operations
    self.connection.autocommit = True

  def register_fixture(self, file):
    """
    Registers a fixture file for which we can load its data into the database.
    """
    with open(file, 'r') as fixture_file:
      self.fixture = yaml.safe_load(fixture_file)

  def execute_query(self, query, data=None, verbose=True):
    """
    Executes a query using the cursor. Prints message if verbose.
    """

    print("Running:", query, data if data else '') if verbose else None

    if data:
      self.cursor.execute(query, data)
    else:
      self.cursor.execute(query)

  def fetch_named_record(self, table_name, record_name):
    """
    Given a record name in the fixture, fetches the data for that record using the record's
    primary key.
    """
    # find the select query for the table we are working with
    select_query = self.get_query(table_name, FixtureQuery.GET)

    # print a warning if there was no select_query that was registered
    if not select_query:
      print(
          f"Warning: No select_query found for table: {table_name}. Skipping select record: {record_name}")
      return

    record_key_dict = self.record_keys[table_name.lower()][record_name]

    self.execute_query(select_query, record_key_dict)

    # ideally only one result expected
    results = self.cursor.fetchall()

    if len(results) > 1:
      print(
          f"Warning: Found multiple results for: {record_name}, in {table_name}! Using first one, but this could be problematic.")

    fetched_record = results[0]

    return {k.lower(): v for k, v in fetched_record.items()}

  def find_table_primary_key(self, table_name):
    """
    Given a table name, finds the primary key column for the table.
    """
    self.execute_query(
        f"SHOW KEYS FROM {table_name} WHERE key_name = 'PRIMARY'", verbose=False)

    keys_result = self.cursor.fetchone()
    key_column = keys_result['Column_name']
    return key_column.lower()

  def update_last_inserted_record_key_value(self, table_name, record_name):
    """
    Given a record_name and the table it belongs to, gets the last inserted row on that table
    and then sets the primary key and value for the record_name.
    """
    key_value = self.cursor.lastrowid
    key_column = self.find_table_primary_key(table_name)

    table_name = table_name.lower()
    self.record_keys.setdefault(table_name, {}).setdefault(record_name, {})

    self.record_keys[table_name][record_name][key_column] = key_value

  def get_query(self, table_name, kind):
    return self.queries.get(table_name.lower(), {}).get(kind)

  def insert_named_record(self, table_name, record_name):
    """
    Given a table and a record_name that exists with the fixture,
    it inserts the record into the correct database table.
    """
    print(f'Inserting Record: {record_name}')

    table_fixture = self.fixture.get(table_name)
    record_fixture = table_fixture.get(record_name)
    relations = table_fixture.get('$relations')

    insert_query = self.get_query(table_name, FixtureQuery.SET)

    if not insert_query:
      print(
          f"Warning: No insert_query found for table: {table_name}. Skipping insert record: {record_name}")
      return

    populated_record = record_fixture.copy()

    # populate all foreign key relations
    for field, value in record_fixture.items():
      relation_match = re.search(r'^\$(\w+)_?', field)
      relation_table = relation_match.group(1).split('_')[0] if relation_match else None

      if (not relation_table) or (relation_table not in self.fixture_table_names):
        continue

      relation_record = self.fetch_named_record(relation_table, value)

      if not relation_record:
        print(
            f'Error: Could not find associated record: {value}, for table: {table_name}. Aborting insert.')
        return

      table_fixture_relation = relations[relation_table]

      if isinstance(table_fixture_relation, list):
        table_fixture_relation = next(
            t for t in table_fixture_relation if t['alias'] == field)

      pk_field = table_fixture_relation['pk'].lower()
      fk_field = table_fixture_relation['fk'].lower()

      populated_record[fk_field] = relation_record[pk_field]

    populated_record = {k.lower(): v for k, v in populated_record.items()}

    self.execute_query(insert_query, populated_record)
    self.update_last_inserted_record_key_value(table_name, record_name)

    print('--------')

  def register_queries(self, queries):
    """
    Registers the fixture set and get queries
    """
    for table_name, queryset in queries.items():
      for kind, query in queryset.items():
        self.register_query(table_name, kind, query)

  def register_query(self, table_name, kind, query):
    self.queries.setdefault(table_name.lower(), {})[kind] = query.lower()

  def unsafe_delete_all_table_rows(self, table_name):
    self.execute_query("SET SQL_SAFE_UPDATES = 0;", verbose=False)
    self.execute_query(f"DELETE FROM {table_name};", verbose=False)
    self.execute_query("SET SQL_SAFE_UPDATES = 1;", verbose=False)

  def load(self):
    """
    Loads the fixture data from the registered .yml file into the 
    database
    """
    self.fixture_table_names = [k for k in self.fixture.keys()]

    for table_name, table_records in self.fixture.items():
      self.unsafe_delete_all_table_rows(table_name)

      for record_name in table_records.keys():
        if record_name.startswith('$'):
          # It is a special key, such as '$relations' that will be parsed separately
          continue

        self.insert_named_record(table_name, record_name)


if __name__ == '__main__':
  fixture = Fixture()

  fixture.connect(user='root', password='mysqladmin', db='airline_db')

  fixture.register_fixture('airline.yml')

  fixture.register_queries({
      "Airport": {
          FixtureQuery.GET: 'SELECT * FROM Airport WHERE Id=%(Id)s;',
          FixtureQuery.SET: 'INSERT INTO Airport (Abbreviation, City, State) VALUES (%(Abbreviation)s, %(City)s, %(State)s);'
      },
      "Terminal": {
          FixtureQuery.GET: 'SELECT * FROM Terminal WHERE Id=%(Id)s;',
          FixtureQuery.SET: 'INSERT INTO Terminal (Airport_Id, Name) VALUES (%(Airport_Id)s, %(Name)s);'
      },
      "Gate": {
          FixtureQuery.GET: 'SELECT * FROM Gate WHERE Id=%(Id)s;',
          FixtureQuery.SET: 'INSERT INTO Gate (Terminal_Id, Name) VALUES (%(Terminal_Id)s, %(Name)s);'
      },
      "Airline": {
          FixtureQuery.GET: 'SELECT * FROM Airline WHERE Id=%(Id)s;',
          FixtureQuery.SET: 'INSERT INTO Airline (Name, Code) VALUES (%(Name)s, %(Code)s);'
      },
      "Class": {
          FixtureQuery.GET: 'SELECT * FROM Class WHERE Id=%(Id)s;',
          FixtureQuery.SET: 'INSERT INTO Class (Airline_Id, Name, Tier) VALUES (%(Airline_Id)s, %(Name)s, %(Tier)s);'
      },
      "Flight": {
          FixtureQuery.GET: 'SELECT * FROM Flight WHERE Id=%(Id)s;',
          FixtureQuery.SET: 'INSERT INTO Flight' +
          '(Name, Airline_Id, DepartureGate_Id, ArrivalGate_Id, ArrivalDate, DepartureDate) VALUES' +
          '(%(Name)s, %(Airline_Id)s, %(DepartureGate_Id)s, %(ArrivalGate_Id)s, %(ArrivalDate)s, %(DepartureDate)s);'
      },
      "Aircraft": {
          FixtureQuery.GET: 'SELECT * FROM Aircraft WHERE Id=%(Id)s;',
          FixtureQuery.SET: 'INSERT INTO Aircraft' +
          '(Name, Airline_Id, Model, Capacity) VALUES' +
          '(%(Name)s, %(Airline_Id)s, %(Model)s, %(Capacity)s);'
      },
      "Seat": {
          FixtureQuery.GET: 'SELECT * FROM Seat WHERE Id=%(Id)s;',
          FixtureQuery.SET: 'INSERT INTO Seat' +
          '(Name, Aircraft_Id, Class_Id) VALUES' +
          '(%(Name)s, %(Aircraft_Id)s, %(Class_Id)s);'
      },
  })

  fixture.load()
