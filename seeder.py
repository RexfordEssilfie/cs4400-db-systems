import mysql.connector
import yaml
import re


class Seeder:
    class Query:
        GET = 'get'  # A get query selects a record by a primary key
        SET = 'set'  # A set query inserts a record

        SET_PROC = 'set_proc'  # A proc name
        SET_PROC_IN = 'set_proc_in'
        SET_PROC_OUT = 'set_proc_out'
        SET_PROC_KEY = 'set_proc_key'



    def __init__(self):
        self.connection = None
        self.cursor = None
        self.fixture = {}  # the fixture as loaded from the .yml file
        self.queries = {}  # queries for fetching/loading entities

        # stores the primary key values for each record if needed by some other entity
        self.record_keys = {}

        # store the list of table names as parsed from the .yml file top level keys
        self.fixture_table_names = []

    def connect_db(self, user=None, db=None, password=None):
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


    def execute_proc(self, proc_name, proc_in_args, proc_out_args, data=None, verbose=True):
        print("Running Proc:", proc_name, data if data else '') if verbose else None

        proc_out_args = [k.lower() for k in proc_out_args]
        proc_in_args = [k.lower() for k in proc_in_args]

        in_args = tuple([data[k] for k in proc_in_args])
        out_args_placeholders = tuple([0 for _ in proc_out_args])

        args = (*in_args, *out_args_placeholders)

        print('args: ', args)
        proc_results = self.cursor.callproc(proc_name, args=args)

        out_args_pos = len(proc_in_args)
        out_query_result_keys = sorted(proc_results.keys())[out_args_pos:]

        out_arg_results = [proc_results[k] for k in out_query_result_keys]

        result = dict(zip(proc_out_args, out_arg_results))

        return result


    def execute_query(self, query, data=None, verbose=True):
        """
        Executes a query using the cursor. Prints message if verbose.
        """

        print("Running:", query, data if data else '') if verbose else None

        if data:
            self.cursor.execute(query, data)
        else:
            self.cursor.execute(query)

    def fetch_row_by_record_name(self, table_name, record_name):
        """
        Given a record name in the fixture, fetches the data for that record using the record's
        primary key.
        """
        # find the select query for the table we are working with
        select_query = self.get_query(table_name, Seeder.Query.GET)

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
                f"Warning: Found multiple results for: {record_name}, in {table_name}! "
                f"Using first one, but this could be problematic.")

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

    def update_inserted_record_key_value(self, table_name, record_name, inserted_id=None):
        """
        Given a record_name and the table it belongs to, gets the last inserted row on that table
        and then sets the primary key and value for the record_name.
        """

        if inserted_id:
            key_value = inserted_id
        else:
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

        proc_name = self.get_query(table_name, Seeder.Query.SET_PROC)

        insert_query = self.get_query(table_name, Seeder.Query.SET)

        if not insert_query:
            print(
                f"Warning: No insert_query found for table: {table_name}. Skipping insert record: {record_name}")
            return

        populated_record = record_fixture.copy()

        # populate all foreign key relations
        for field, value in record_fixture.items():
            relation_match = re.search(r'^\$(\w+)_?', field)
            relation_table = relation_match.group(1).split(
                '_')[0] if relation_match else None

            if (not relation_table) or (relation_table not in self.fixture_table_names):
                continue

            relation_row = self.fetch_row_by_record_name(relation_table, value)

            if not relation_row:
                print(
                    f'Error: Could not find associated record: {value}, for table: {table_name}. Aborting insert.')
                return

            if relation_table not in relations.keys():
                print(
                    f'Error: Missing $relation in fixture for table: {table_name}. Aborting insert.')
                return

            table_relation_info = relations[relation_table]

            if isinstance(table_relation_info, list):
                table_relation_info = next(
                    r for r in table_relation_info if r['alias'] == field)

            pk_field = table_relation_info['pk'].lower()
            fk_field = table_relation_info['fk'].lower()

            populated_record[fk_field] = relation_row[pk_field]

        populated_record = {k.lower(): v for k, v in populated_record.items()}


        last_insert_id = None
        if proc_name:
            proc_in_args = self.get_query(table_name, Seeder.Query.SET_PROC_IN)
            proc_out_args = self.get_query(table_name, Seeder.Query.SET_PROC_OUT)
            result = self.execute_proc(proc_name, proc_in_args, proc_out_args, populated_record)

            proc_insert_key = self.get_query(table_name, Seeder.Query.SET_PROC_KEY)
            last_insert_id = result[proc_insert_key.lower()]
        else:
            self.execute_query(insert_query, populated_record)

        self.update_inserted_record_key_value(table_name, record_name, last_insert_id)

        print('--------')

    def register_queries(self, queries):
        """
        Registers the fixture set and get queries
        """
        for table_name, queryset in queries.items():
            for kind, query in queryset.items():
                self.register_query(table_name, kind, query)

    def register_query(self, table_name, kind, query):
        self.queries.setdefault(table_name.lower(), {})[kind] = query.lower() if isinstance(query, str) else query

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
    seeder = Seeder()

    seeder.connect_db(user='root', password='mysqladmin', db='airline_db')

    seeder.register_fixture('airline.yml')

    seeder.register_queries({
        'Airport': {
            Seeder.Query.GET: 'SELECT * FROM Airport WHERE Id=%(Id)s;',
            Seeder.Query.SET: 'INSERT INTO Airport' +
                              '(Abbreviation, City, State, Name) ' +
                              'VALUES ' +
                              '(%(Abbreviation)s, %(City)s, %(State)s, %(Name)s);',

            Seeder.Query.SET_PROC: 'create_airport',
            Seeder.Query.SET_PROC_IN: ('Abbreviation', 'City', 'Name', 'State'),
            Seeder.Query.SET_PROC_OUT: ('Id',),
            Seeder.Query.SET_PROC_KEY: 'Id',
        },
        'Terminal': {
            Seeder.Query.GET: 'SELECT * FROM Terminal WHERE Id=%(Id)s;',
            Seeder.Query.SET: 'INSERT INTO Terminal' +
                              '(Airport_Id, Name) ' +
                              'VALUES ' +
                              '(%(Airport_Id)s, %(Name)s);',

            Seeder.Query.SET_PROC: 'create_terminal',
            Seeder.Query.SET_PROC_IN: ('Airport_Id', 'Name'),
            Seeder.Query.SET_PROC_OUT: ('Id',),
            Seeder.Query.SET_PROC_KEY: 'Id',

        },
        'Gate': {
            Seeder.Query.GET: 'SELECT * FROM Gate WHERE Id=%(Id)s;',
            Seeder.Query.SET: 'INSERT INTO Gate ' +
                              '(Terminal_Id, Name) ' +
                              'VALUES ' +
                              '(%(Terminal_Id)s, %(Name)s);'
        },
        'Airline': {
            Seeder.Query.GET: 'SELECT * FROM Airline WHERE Id=%(Id)s;',
            Seeder.Query.SET: 'INSERT INTO Airline ' +
                              '(Name, Code, City, State) ' +
                              'VALUES ' +
                              '(%(Name)s, %(Code)s, %(City)s,  %(State)s);',

            Seeder.Query.SET_PROC: 'create_airline',
            Seeder.Query.SET_PROC_IN: ('Name', 'Code', 'City', 'State'),
            Seeder.Query.SET_PROC_OUT: ('Id',),
            Seeder.Query.SET_PROC_KEY: 'Id',
            
            
        },
        'Class': {
            Seeder.Query.GET: 'SELECT * FROM Class WHERE Id=%(Id)s;',
            Seeder.Query.SET: 'INSERT INTO Class (Airline_Id, Name, Tier) ' +
                              'VALUES (%(Airline_Id)s, %(Name)s, %(Tier)s);',

            Seeder.Query.SET_PROC: 'create_class',
            Seeder.Query.SET_PROC_IN: ('Name', 'Tier', 'Airline_Id'),
            Seeder.Query.SET_PROC_OUT: ('Id',),
            Seeder.Query.SET_PROC_KEY: 'Id',
        },
        'Flight': {
            Seeder.Query.GET: 'SELECT * FROM Flight WHERE Id=%(Id)s;',
            Seeder.Query.SET: 'INSERT INTO Flight' +
                              '(Name, Aircraft_Id, DepartureGate_Id, ArrivalGate_Id, ArrivalDate, DepartureDate, Status) ' +
                              'VALUES' +
                              '(%(Name)s, %(Aircraft_Id)s, %(DepartureGate_Id)s, %(ArrivalGate_Id)s, ' +
                              '%(ArrivalDate)s, %(DepartureDate)s, %(Status)s);',

            Seeder.Query.SET_PROC: 'create_flight',
            Seeder.Query.SET_PROC_IN: ('Aircraft_Id', 'Name', 'DepartureGate_Id', 'ArrivalGate_Id', 'DepartureDate', 'ArrivalDate'),
            Seeder.Query.SET_PROC_OUT: ('Id',),
            Seeder.Query.SET_PROC_KEY: 'Id',
        },
        'Aircraft': {
            Seeder.Query.GET: 'SELECT * FROM Aircraft WHERE Id=%(Id)s;',
            Seeder.Query.SET: 'INSERT INTO Aircraft' +
                              '(Name, Airline_Id, Model, Capacity)'+ 'VALUES' +
                              '(%(Name)s, %(Airline_Id)s, %(Model)s, %(Capacity)s);',

            Seeder.Query.SET_PROC: 'create_aircraft',
            Seeder.Query.SET_PROC_IN: ('Airline_Id', 'Name'),
            Seeder.Query.SET_PROC_OUT: ('Id',),
            Seeder.Query.SET_PROC_KEY: 'Id',
        },
        'Seat': {
            Seeder.Query.GET: 'SELECT * FROM Seat WHERE Id=%(Id)s;',
            Seeder.Query.SET: 'INSERT INTO Seat' +
                              '(Name, Aircraft_Id, Class_Id)'+ 'VALUES' +
                              '(%(Name)s, %(Aircraft_Id)s, %(Class_Id)s);',

            Seeder.Query.SET_PROC: 'create_seat',
            Seeder.Query.SET_PROC_IN: ('Aircraft_Id', 'Class_Id', 'Name'),
            Seeder.Query.SET_PROC_OUT: ('Id',),
            Seeder.Query.SET_PROC_KEY: 'Id',
        },
        'Ticket': {
            Seeder.Query.GET: 'SELECT * FROM Ticket WHERE Id=%(Id)s;',
            Seeder.Query.SET: 'INSERT INTO Ticket' +
                              '(Price, Flight_Id, Seat_Id)'+ 'VALUES' +
                              '(%(Price)s, %(Flight_Id)s, %(Seat_Id)s);',

            Seeder.Query.SET_PROC: 'create_ticket',
            Seeder.Query.SET_PROC_IN: ('Flight_Id', 'Seat_Id', 'Price'),
            Seeder.Query.SET_PROC_OUT: ('Id',),
            Seeder.Query.SET_PROC_KEY: 'Id',
        },
        'User':{
            Seeder.Query.GET: 'SELECT * FROM User WHERE Id=%(Id)s;',
            Seeder.Query.SET: 'INSERT INTO User' +
                              '(Airline_Id, FirstName, LastName,Email,Password)'+ 'VALUES' +
                              '(%(Airline_Id)s, %(FirstName)s, %(LastName)s,%(Email)s,%(Password)s);',

            Seeder.Query.SET_PROC: 'create_user',
            Seeder.Query.SET_PROC_IN: ('FirstName', 'Airline_Id', 'LastName', 'Password', 'Email'),
            Seeder.Query.SET_PROC_OUT: ('Id',),
            Seeder.Query.SET_PROC_KEY: 'Id',
            },
        'Passenger':{
            Seeder.Query.GET: 'SELECT * FROM Passenger WHERE Id=%(Id)s;',
            Seeder.Query.SET: 'INSERT INTO Passenger' +
                              '(PassportNumber, FirstName, LastName,CountryCode,Email)'+ 'VALUES' +
                              '(%(PassportNumber)s, %(FirstName)s, %(LastName)s,%(CountryCode)s,%(Email)s);',

            Seeder.Query.SET_PROC: 'create_passenger',
            Seeder.Query.SET_PROC_IN: ('PassportNumber', 'FirstName', 'LastName', 'CountryCode', 'Email'),
            Seeder.Query.SET_PROC_OUT: ('Id',),
            Seeder.Query.SET_PROC_KEY: 'Id',
            },
        'Payment': {
            Seeder.Query.GET: 'SELECT * FROM Payment WHERE Id=%(Id)s;',
            Seeder.Query.SET: 'INSERT INTO Payment' +
                              '(Amount, DateCreated, BillingDetail_Id, Status)'+ 'VALUES' +
                              '(%(Amount)s, %(DateCreated)s, %(BillingDetail_Id)s, %(Status)s);',

            Seeder.Query.SET_PROC: 'create_payment',
            Seeder.Query.SET_PROC_IN: ('Amount', 'BillingDetail_Id'),
            Seeder.Query.SET_PROC_OUT: ('Id',),
            Seeder.Query.SET_PROC_KEY: 'Id',
        },
        'Ticket_Payment': {
            Seeder.Query.GET: 'SELECT * FROM Ticket_Payment WHERE Id=%(Id)s;',
            Seeder.Query.SET: 'INSERT INTO Ticket_Payment' +
                              '(Ticket_Id, Payment_Id)'+ 'VALUES' +
                              '(%(Ticket_Id)s, %(Payment_Id)s);',

            Seeder.Query.SET_PROC: 'create_ticket_payment',
            Seeder.Query.SET_PROC_IN: ('Ticket_Id', 'Payment_Id'),
            Seeder.Query.SET_PROC_OUT: ('Id',),
            Seeder.Query.SET_PROC_KEY: 'Id',
        },
        'BillingDetail': {
            Seeder.Query.GET: 'SELECT * FROM BillingDetail WHERE Id=%(Id)s;',
            Seeder.Query.SET: 'INSERT INTO BillingDetail' +
                              '(User_Id, CardNumberLastFourDigit, CardToken)' + 'VALUES' +
                              '((%(User_Id)s, %(CardNumberLastFourDigit)s, %(CardToken)s);',
            
            Seeder.Query.SET_PROC: 'add_billing_detail',
            Seeder.Query.SET_PROC_IN: ('User_Id', 'CardNumberLastFourDigit', 'CardToken'),
            Seeder.Query.SET_PROC_OUT: ('Id',),
            Seeder.Query.SET_PROC_KEY: 'Id',
        },
        'Refund': {
            Seeder.Query.GET: 'SELECT * FROM Refund WHERE Id=%(Id)s;',
            Seeder.Query.SET: 'INSERT INTO Refund' +
                              '(Payment_Id)'+ 'VALUES' +
                              '(%(Payment_Id)s);',
            
            Seeder.Query.SET_PROC: 'create_refund',
            Seeder.Query.SET_PROC_IN: ('Payment_Id',),
            Seeder.Query.SET_PROC_OUT: ('Id',),
            Seeder.Query.SET_PROC_KEY: 'Id',
        },
    })

    seeder.load()
