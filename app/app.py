from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap

import hashlib

from app.db import DatabaseHelper

app = Flask(__name__)

db = DatabaseHelper(user='root', password='mysqladmin', db='airline_db')

Bootstrap(app)

error_message = ''


@app.template_filter()
def format_date(date):
    return date.strftime('%d %B  %Y  (%H:%M %p)')


@app.template_filter()
def first(lst):
    return lst[0] if isinstance(lst, list) and len(lst) else {}


@app.route("/")
def home():
    return render_template('home.html.jinja')


@app.get("/flights")
def flights():
    flight_from = request.args.get('from')
    flight_to = request.args.get('to')

    flight_results = db.get_flights_from_to(flight_from, flight_to) or []

    return render_template('flights.html.jinja', result=flight_results)


@app.get("/flights/<int:flight_id>/tickets")
def flight_tickets(flight_id):
    tickets = db.get_available_tickets_by_flight_id(flight_id)

    flight = db.get_flight_by_id(flight_id)

    return render_template('tickets.html.jinja', result={'tickets': tickets, 'flight': flight})


@app.get("/checkout/<int:ticket_id>")
def checkout(ticket_id):
    ticket = db.get_ticket_by_id(ticket_id)
    flight = db.get_flight_by_id(ticket['flight_id'])

    return render_template('checkout.html.jinja', result={'ticket': ticket, 'flight': flight})


@app.post("/purchase/ticket/<int:ticket_id>")
def purchase_ticket(ticket_id):
    try:
        form_data = {}
        ticket = db.get_ticket_by_id(ticket_id)

        amount = ticket['price']

        for key in request.form.keys():
            table, field = key.split('_')
            form_data.setdefault(table, {})[field] = request.form.get(key)

        print(form_data)


        billing_detail = form_data['billingdetail']


        processor_response = send_billing_to_processor(billing_detail, amount)

        billing_detail_id = db.add_billing_detail(None, processor_response['lastfour'], processor_response['token'])['id']

        passenger = form_data['passenger']
        passenger_id = db.create_passenger(first_name=passenger['firstname'],
                                           last_name=passenger['lastname'],
                                           passport_number=passenger['passportno'],
                                           email=passenger['email'])['id']

        db.buy_single_ticket(
            ticket_id=ticket_id,
            passenger_id=passenger_id,
            billing_detail_id=billing_detail_id,
            amount=amount,
            processor_status=processor_response['status']
        )

        return redirect(url_for('purchase_confirmation', ticket_id=ticket_id))
    except Exception as e:
        global error_message
        error_message = str(e)
        return redirect(url_for('purchase_error', ticket_id=ticket_id))


@app.get("/confirmation/<int:ticket_id>")
def purchase_confirmation(ticket_id):
    # TODO: Confirmation page
    #  Fetch ticket and display its status

    ticket = db.get_ticket_by_id(ticket_id)

    return render_template('status.html.jinja', result=ticket)


@app.get("/error/<int:ticket_id>")
def purchase_error(ticket_id):
    return render_template('error.html.jinja', result=error_message)


def send_billing_to_processor(details, amount):
    private_pieces = (details['cardno'] + details['cvv']).encode()
    return {'lastfour': details['cardno'][-4:],
            'token': hashlib.sha256(private_pieces).hexdigest()[0:45],
            'status': 'success',
            'amount': amount
            }
