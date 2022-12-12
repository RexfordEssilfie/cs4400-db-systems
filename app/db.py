import mysql.connector


class DatabaseHelper:

    def __init__(self, user=None, db=None, password=None):
        """
        Establishes a database connection.
        """
        self.connection = mysql.connector.connect(
            user=user, database=db, password=password)  # connect to a database

        # create cursor with dictionary=True to get results as a dictionary
        self.cursor = self.connection.cursor(dictionary=True)

        # for convenience, autocommit all operations
        self.connection.autocommit = True

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

    def results(self):
        all_results = self.cursor.fetchall()
        return [{k.lower(): v for k, v in result.items()} for result in all_results] if isinstance(all_results,
                                                                                                   list) and len(
            all_results) > 0 else None

    def result(self):
        all_results = self.results()
        return all_results[0] if all_results and len(all_results) > 0 else None

    def get_flights_from_to(self, flight_from, flight_to):
        self.execute_query(
            "SELECT * FROM Flight_Populated WHERE DepartureAirport_Abbreviation=%s AND ArrivalAirport_Abbreviation=%s",
            [flight_from, flight_to])
        return self.results()

    def get_available_tickets_by_flight_id(self, flight_id):
        self.execute_query(
            "SELECT * FROM Ticket_Populated WHERE Flight_Id=%s AND Confirmation_Status IS NULL OR lower(Confirmation_Status) !=  'active'",
            [flight_id])
        return self.results()

    def get_ticket_by_id(self, ticket_id):
        self.execute_query(
            "SELECT * FROM Ticket_Populated WHERE Id=%s", [ticket_id])
        return self.result()

    def get_flight_by_id(self, flight_id):
        self.execute(
            "SELECT * FROM Flight_Populated WHERE Id=%s", [flight_id])
        return self.result()

    def buy_single_ticket(self, ticket_id=None, passenger_id=None, billing_detail_id=None, amount=None,
                          processor_status=None):
        result = self.execute_proc('buy_single_ticket',
                                   ('ticket_id', 'passenger_id', 'billing_detail_id', 'amount', 'payment_status'),
                                   ('id',),
                                   dict(ticket_id=ticket_id, passenger_id=passenger_id,
                                        billing_detail_id=billing_detail_id,
                                        amount=amount, payment_status=processor_status)
                                   )
        return result

    def update_flight_schedule(self, flight_id=None, departure_date=None, arrival_date=None):

        result = self.execute_proc('buy_single_ticket',
                                   ('flight_id', 'departure_date', 'arrival_date'),
                                   ('id',),
                                   dict(flight_id=flight_id, departure_date=departure_date, arrival_date=arrival_date))

        return result

    def create_user(self, first_name, airline_id, last_name, password, email):
        result = self.cursor.callproc('create_user', args=(first_name, airline_id, last_name, password, email))
        return result

    def user_login(self, email, password):
        result = self.cursor.callproc('user_login_in', args=(email, password))
        return result

    def add_billing_detail(self, userid, cardlastfour, cardtoken):
        result = self.cursor.callproc('add_billing_detail', args=(userid, cardlastfour, cardtoken))
        return result
