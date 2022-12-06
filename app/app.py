from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap

import mysql.connector

from app.db import DatabaseHelper
import datetime


app = Flask(__name__)

db_helper = DatabaseHelper(user='root', password='mysqladmin', db='airline_db')

Bootstrap(app)


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

    flights = db_helper.get_flights_from_to(flight_from, flight_to) or []

    return render_template('flights.html.jinja', result=flights)


@app.get("/flights/<int:flight_id>/tickets")
def flight_tickets(flight_id):

    tickets = db_helper.get_available_tickets_by_flight_id(flight_id)

    flight = db_helper.get_flight_by_id(flight_id)

    return render_template('tickets.html.jinja', result={'tickets': tickets, 'flight': flight})


@app.get("/checkout/<int:ticket_id>")
def checkout(ticket_id):

    ticket = db_helper.get_ticket_by_id(ticket_id)
    flight = db_helper.get_flight_by_id(ticket['flight_id'])

    return render_template('checkout.html.jinja', result={'ticket': ticket, 'flight': flight})


@app.post("/purchase/ticket/<int:ticket_id>")
def purchase_ticket(ticket_id):

    # Attempt purchase, if success, go to confirmation else go to failure page
    # TODO: save passenger info, save billing detail, use stored procedure for ticket purchase

    ticket = {}

    return redirect(url_for('purchase_confirmation', ticket_id=ticket_id))


@app.get("/confirmation/<int:ticket_id>")
def purchase_confirmation(ticket_id):
    # TODO: Confirmation page
    #  Fetch ticket and display its status
    return render_template('confirmation.html.jinja')


@app.get("/error/<int:ticket_id>")
def purchase_error(ticket_id):
    return render_template('error.html.jinja')
