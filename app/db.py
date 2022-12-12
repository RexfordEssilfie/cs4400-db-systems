import mysql.connector


class DatabaseHelper:

    def __init__(self, user=None, db=None, password=None):
        """
        Establishes a database connection.
        """
        self.connection = mysql.connector.connect(
            user=user, database=db, password=password)

        self.cursor = self.connection.cursor(dictionary=True)

        self.connection.autocommit = True

    def execute(self, query, data=None, verbose=True):
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
        return [{k.lower(): v for k, v in result.items()} for result in all_results] if isinstance(all_results, list) and len(all_results) > 0 else None

    def result(self):
        all_results = self.results()
        return all_results[0] if all_results and len(all_results) > 0 else None

    def get_flights_from_to(self, flight_from, flight_to):
        self.execute(
            "SELECT * FROM Flight_Populated WHERE DepartureAirport_Abbreviation=%s AND ArrivalAirport_Abbreviation=%s", [flight_from, flight_to])
        return self.results()

    def get_available_tickets_by_flight_id(self, flight_id):
        self.execute(
            "SELECT * FROM Ticket_Populated WHERE Flight_Id=%s AND Confirmation_Status IS NULL OR lower(Confirmation_Status) !=  'active'", [flight_id])
        return self.results()

    def get_ticket_by_id(self, ticket_id):
        self.execute(
            "SELECT * FROM Ticket_Populated WHERE Id=%s", [ticket_id])
        return self.result()

    def get_flight_by_id(self, flight_id):
        self.execute(
            "SELECT * FROM Flight_Populated WHERE Id=%s", [flight_id])
        return self.result()

    def buy_single_ticket(self, ticket_id=None, passenger_id=None, card_lastfour=None, card_token=None, amount=None, processor_status=None):
        #TODO: insert billing detail, then payment with correct amount, for given ticket

        # result = self.cursor.callproc('buy_single_ticket', args=(ticket_id, passenger_id, billing_id))
        result = None

        return result
    
    def create_user(self, Firstname, AirlineId, Lastname, Password, Email):
        result = self.cursor.callproc('create_user', args = (Firstname, AirlineId, Lastname, Password, Email))
        return result
    
    def UserLogin(self, email, password):
        result = self.cursor.callproc('user_login_in', args=(email, password))
        return result
        
    def addbillingdetail(self, userid, cardlastfour, cardtoken):
        result = self.cursor.callproc('add_billing_detail', args=(userid, cardlastfour, cardtoken))
        return result

