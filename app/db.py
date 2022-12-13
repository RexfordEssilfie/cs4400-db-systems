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

        proc_results = self.free_procedure_cursor()

        return result


    def call_proc(self):
        pass

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


    def free_procedure_cursor(self):
        proc_results = []
        for result in self.cursor.stored_results():
            proc_results.extend(result.fetchall())

        return proc_results

    def get_flights_from_to(self, flight_from, flight_to):
        self.execute_query(f"""
        SELECT
        `flight`.`Id` AS `Id`,
        `flight`.`Aircraft_Id` AS `Aircraft_Id`,
        `flight`.`Name` AS `Name`,
        `flight`.`DepartureGate_Id` AS `DepartureGate_Id`,
        `flight`.`ArrivalGate_Id` AS `ArrivalGate_Id`,
        `flight`.`DepartureDate` AS `DepartureDate`,
        `flight`.`ArrivalDate` AS `ArrivalDate`,
        `G1`.`Name` AS `DepartureGate_Name`,
        `G2`.`Name` AS `ArrivalGate_Name`,
        `C1`.`Name` AS `Aircraft_Name`,
        `L1`.`Name` AS `Airline_Name`,
        `T1`.`Name` AS `DepartureTerminal_Name`,
        `T2`.`Name` AS `ArrivalTerminal_Name`,
        `A1`.`Name` AS `DepartureAirport_Name`,
        `A2`.`Name` AS `ArrivalAirport_Name`,
        `A1`.`Abbreviation` AS `DepartureAirport_Abbreviation`,
        `A2`.`Abbreviation` AS `ArrivalAirport_Abbreviation`
    FROM
        ((((((((`flight`
        LEFT JOIN `gate` `G1` ON ((`flight`.`DepartureGate_Id` = `G1`.`Id`)))
        LEFT JOIN `gate` `G2` ON ((`flight`.`ArrivalGate_Id` = `G2`.`Id`)))
        LEFT JOIN `aircraft` `C1` ON ((`flight`.`Aircraft_Id` = `C1`.`Id`)))
        LEFT JOIN `terminal` `T1` ON ((`G1`.`Terminal_Id` = `T1`.`Id`)))
        LEFT JOIN `terminal` `T2` ON ((`G2`.`Terminal_Id` = `T2`.`Id`)))
        LEFT JOIN `airport` `A1` ON ((`T1`.`Airport_Id` = `A1`.`Id`)))
        LEFT JOIN `airport` `A2` ON ((`T2`.`Airport_Id` = `A2`.`Id`)))
        LEFT JOIN `airline` `L1` ON ((`C1`.`Airline_Id` = `L1`.`Id`)))

	WHERE DepartureGate_Id IN (select Id from airline_db.Gate WHERE Terminal_Id IN (select Id from airline_db.Terminal WHERE Airport_Id  IN (select Id from airline_db.Airport WHERE Abbreviation="{flight_from}"))) and
    ArrivalGate_Id IN (
         select Id from airline_db.Gate WHERE Terminal_Id IN
         (
           select Id from airline_db.Terminal WHERE Airport_Id  IN
           (
             select Id from airline_db.Airport WHERE Abbreviation="{flight_to}")));
        """)
        return self.results()

    def get_available_tickets_by_flight_id(self, flight_id):
       self.execute_query(f"""
       SELECT 
        `ticket`.`Id` AS `Id`,
        `ticket`.`Flight_Id` AS `Flight_Id`,
        `ticket`.`Seat_Id` AS `Seat_Id`,
        `ticket`.`Price` AS `Price`,
        `seat`.`Name` AS `Seat_Name`,
        `class`.`Name` AS `Class_Name`,
        `confirmation`.`Status` AS `Confirmation_Status`
    FROM
        (((`ticket`
        LEFT JOIN `seat` ON ((`seat`.`Id` = `ticket`.`Seat_Id`)))
        LEFT JOIN `class` ON ((`seat`.`Class_Id` = `class`.`Id`)))
        LEFT JOIN `confirmation` ON ((`confirmation`.`Ticket_Id` = `ticket`.`Id`)))
        
       WHERE Ticket.Flight_Id="{flight_id}" AND (Confirmation.Status IS NULL OR Confirmation.Status NOT IN ("Active"));
       """)

       return self.results()

    def get_ticket_by_id(self, ticket_id):
        self.execute_query(
            f"""
            SELECT 
        `ticket`.`Id` AS `Id`,
        `ticket`.`Flight_Id` AS `Flight_Id`,
        `ticket`.`Seat_Id` AS `Seat_Id`,
        `ticket`.`Price` AS `Price`,
        `seat`.`Name` AS `Seat_Name`,
        `class`.`Name` AS `Class_Name`,
        `confirmation`.`Status` AS `Confirmation_Status`
        FROM
        (((`ticket`
        LEFT JOIN `seat` ON ((`seat`.`Id` = `ticket`.`Seat_Id`)))
        LEFT JOIN `class` ON ((`seat`.`Class_Id` = `class`.`Id`)))
        LEFT JOIN `confirmation` ON ((`confirmation`.`Ticket_Id` = `ticket`.`Id`)))
        
       WHERE Ticket.Id="{ticket_id}";
            """, [])
        return self.result()

    def get_flight_by_id(self, flight_id):
        self.execute_query("""
        SELECT
        `flight`.`Id` AS `Id`,
        `flight`.`Aircraft_Id` AS `Aircraft_Id`,
        `flight`.`Name` AS `Name`,
        `flight`.`DepartureGate_Id` AS `DepartureGate_Id`,
        `flight`.`ArrivalGate_Id` AS `ArrivalGate_Id`,
        `flight`.`DepartureDate` AS `DepartureDate`,
        `flight`.`ArrivalDate` AS `ArrivalDate`,
        `G1`.`Name` AS `DepartureGate_Name`,
        `G2`.`Name` AS `ArrivalGate_Name`,
        `C1`.`Name` AS `Aircraft_Name`,
        `L1`.`Name` AS `Airline_Name`,
        `T1`.`Name` AS `DepartureTerminal_Name`,
        `T2`.`Name` AS `ArrivalTerminal_Name`,
        `A1`.`Name` AS `DepartureAirport_Name`,
        `A2`.`Name` AS `ArrivalAirport_Name`,
        `A1`.`Abbreviation` AS `DepartureAirport_Abbreviation`,
        `A2`.`Abbreviation` AS `ArrivalAirport_Abbreviation`
    FROM
        ((((((((`flight`
        LEFT JOIN `gate` `G1` ON ((`flight`.`DepartureGate_Id` = `G1`.`Id`)))
        LEFT JOIN `gate` `G2` ON ((`flight`.`ArrivalGate_Id` = `G2`.`Id`)))
        LEFT JOIN `aircraft` `C1` ON ((`flight`.`Aircraft_Id` = `C1`.`Id`)))
        LEFT JOIN `terminal` `T1` ON ((`G1`.`Terminal_Id` = `T1`.`Id`)))
        LEFT JOIN `terminal` `T2` ON ((`G2`.`Terminal_Id` = `T2`.`Id`)))
        LEFT JOIN `airport` `A1` ON ((`T1`.`Airport_Id` = `A1`.`Id`)))
        LEFT JOIN `airport` `A2` ON ((`T2`.`Airport_Id` = `A2`.`Id`)))
        LEFT JOIN `airline` `L1` ON ((`C1`.`Airline_Id` = `L1`.`Id`)))

	WHERE Flight.Id=%s; 
        """, [flight_id])
        return self.result()

    def buy_single_ticket(self, ticket_id=None, passenger_id=None, billing_detail_id=None, amount=None,
                          processor_status=None):
        result = self.execute_proc('buy_single_ticket',
                                   ('ticket_id', 'passenger_id', 'billing_detail_id', 'amount', 'payment_status'),
                                   (),
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
        result = self.cursor.callproc('create_user', args=(first_name, airline_id, last_name, password, email, 0))
        return result

    def create_passenger(self, first_name=None, last_name=None, passport_number=None, country_code='US', email=None):

        result = self.execute_proc('create_passenger',
                                   ('passport_number', 'first_name', 'last_name',  'country_code', 'email'),
                                   ('id',),
                                   dict(first_name=first_name, last_name=last_name,
                                        passport_number=passport_number,
                                        country_code=country_code, email=email)
                                   )

        return result

    def create_passenger_from_user(self, user_id, passport_number):
        result = self.cursor.callproc('create_passenger_from_user', args=(user_id, passport_number, 0))
        return result

    def user_login(self, email, password):
        result = self.cursor.callproc('user_login_in', args=(email, password))
        return result

    def add_billing_detail(self, userid, cardlastfour, cardtoken):
        result = self.execute_proc('add_billing_detail',
                                   ('userid', 'cardlastfour', 'cardtoken'),
                                   ('id',),
                                   dict(userid=userid, cardlastfour=cardlastfour,
                                        cardtoken=cardtoken)
                                   )
        return result

    def get_available_airlines(self):
        self.execute_query("SELECT * FROM Airline", [])
        return self.results()

    def fetch_flights_between_airports_on_departure_date(self, departure_airport_code, arrival_airport_code, departure_date):
        result = self.cursor.callproc('fetch_flights_betweenAirports_on_departureDate', args=(departure_airport_code, arrival_airport_code, departure_date, 0))
        return result


if __name__=='__main__':
    db = DatabaseHelper(user='root', password='mysqladmin', db='airline_db')
