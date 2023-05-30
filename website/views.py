"""
The purpose of auth.py is to store the standard routes for the website.
Blueprint allows the program view this file as a blueprint, which means this file will store routes of our application.
This way the app.py can be nicely organized and separate the views from application itself.
"""

# Import the 'db' object located in __init__.py from the current package (website) for database operations
from . import db
# Import functions and classes from the Flask framework. 
# These are used for creating routes, rendering templates, handling requests, flashing messages, and redirecting.
from flask import Blueprint, render_template, request, flash, redirect, url_for
# Import for user authentication and user information access. 
from flask_login import login_required, current_user
# Imports the models from the current package, which define the database tables and their relationships
from .models import Theater, Movie, Screening, Booking
# Import necessary modules to work with dates and times.
from datetime import datetime
# Import necessary modules to write data into csv
import csv
# Import necessary modules to create a temporary file to edit a row based on condition in csv 
from tempfile import NamedTemporaryFile
# Import necessary modules to move file
import shutil
# Import necessary modules to retrieve dynamic file location
from pathlib import Path
import os

# Define a blueprint named 'views' for this module
# Blueprints are used to organize routes and views in Flask applications.
views = Blueprint('views', __name__)

# Defining route and view for the homepage ('/' route) with the home function.
@views.route('/', methods=['GET', 'POST'])               
# '@login_required' ensures only authenticated (logged in) users can access the page.
@login_required
def home():
    """
    Route for the homepage.

    Renders the home.html template to display the authenticated user's home page.

    Returns:
        Response: The rendered template.
    """
    # Returns the rendered template home.html and passes the current_user to the template.
    return render_template("home.html", user=current_user)

# Defining route and view for the theater page ('/theater' route) with the theater function. 
@views.route('/theater', methods=['GET', 'POST'])
# '@login_required' ensures only authenticated (logged in) users can access the page.
@login_required
def theater():
    """
    Route for the theater page.

    Renders the theater.html template to display available theaters.

    Returns:
        Response: The rendered template.
    """
    # Retrieves all theater objects from the database
    theater_list = Theater.query.all()
    # Returns the rendered template theater.html and passes theater_list and current_user to the template.
    return render_template("theater.html", user=current_user, theater_list=theater_list)


# Defining route and view for the currentMovies page ('/currentMovies' route) with the movies function. 
@views.route('/currentMovies', methods=['GET', 'POST'])
# '@login_required' ensures only authenticated (logged in) users can access the page.
@login_required
def movies():
    """
    Route for the currentMovies page.

    Renders the movies.html template to display movie screenings.

    Returns:
        Response: The rendered template.
    """
    # Retrieve all theater objects from the database
    theater_list = Theater.query.all()
    # Retrieve available screening dates (only showing 7 days from today)
    screening_date = db.session.query(Screening).filter(Screening.date >= datetime.today().date()).group_by(Screening.date).all()
    
    if request.method == "POST":
        # Get the selected date from the form submission
        date = request.form.get("date")
        # Get screening times and associated theater and movie information for the selected date
        screening_list = (db.session.query(Screening, Theater, Movie)
                          .join(Theater)
                          .join(Movie)
                          .filter(Screening.date == date)
                          ).all()
        # Get distinct movie information for the selected date and group by theater name and movie title
        movie_list = (db.session.query(Screening, Theater, Movie)
                          .join(Theater)
                          .join(Movie)
                          .filter(Screening.date == date)
                          .group_by(Theater.name, Movie.title)
                          ).all()
        # Render the movies.html template and pass the retrieved data to the template, showing users the page with list of movies on the desired date
        return render_template("movies.html", user=current_user, screening_date=screening_date, theater_list=theater_list,
                                screening_list=screening_list, movie_list=movie_list, date=date)
    else:
        # Render the movies.html template with the available data, showing users the page to choose dates
        return render_template("movies.html", user=current_user, theater_list=theater_list, screening_date=screening_date)
            

# Defining route and view for the getTIcket page ('/getTicket' route) with the ticket function. 
@views.route('/getTicket', methods=['GET', 'POST'])
# '@login_required' ensures only authenticated (logged in) users can access the page.
@login_required
def ticket():
    """
    Route for the getTicket page, rendering the ticket page and handling ticket booking.

    If a POST request is received:
        - If the form contains the selected screening ID:
            - Retrieve the selected screening details.
            - Render the ticket.html template with the screening details.
        - If the form contains the number of tickets:
            - Retrieve the number of tickets and the selected screening ID.
            - Retrieve the details of the selected screening.
            - If there are not enough tickets available:
                - Display an error message and redirect to the movies page.
            - If there are enough tickets available:
                - Book the tickets and update the screening and booking data.
                - Write the booking data to the booking.csv file.
                - Update the available seats of the booked screening in the screening.csv file.
                - Display a success message and redirect to the booking page.

    If a GET request is received:
        - Renders the ticket.html template.

    Returns:
        Response: The rendered template or a redirect response.
    """
    if request.method == "POST":
        if request.form.get("screening_id"):
            # Retrieve the selected screening details
            screening = request.form.get("screening_id")
            # Get screening times and associated theater and movie information for the selected date
            screening_desired = (db.session.query(Screening, Theater, Movie)
                            .join(Theater)
                            .join(Movie)
                            .filter(Screening.id == screening)
                            ).first()

            return render_template("ticket.html", user=current_user, screening=screening_desired)
        
        # When get the number of ticket user want
        elif request.form.get('number_of_ticket'):
            # Retrieve the number of tickets and the selected screening ID
            number = request.form.get('number_of_ticket')
            screening_id = request.form.get('booked_screening')
            # Get the details of the selected screening
            screening_desired = (db.session.query(Screening, Theater, Movie)
                            .join(Theater)
                            .join(Movie)
                            .filter(Screening.id == screening_id)
                            ).first()
            
            # If not enough ticket available
            if int(number) > screening_desired[0].available_seats:
                # Validate ticket availability
                left = screening_desired[0].available_seats
                flash(f"There are only {left} tickets left for this screening. Please try to book again.", category='error')
                return redirect(url_for('views.movies'))
            # if there are enough tickets
            else:
                # Book the tickets and update the screening and booking data
                new_number_of_seats = screening_desired[0].available_seats - int(number)
                print(new_number_of_seats)
                # write new booking to booking database default already has timestamp
                booking = Booking(number_of_tickets=number, user_id=current_user.id)
                # add new booking data to booking database
                db.session.add(booking)
                db.session.commit()
                # update screening's available seats
                screening_desired[0].available_seats = new_number_of_seats

                # link new booking to screening query the screening we want to append booking to in screening_booking
                screening_booking = Screening.query.filter(Screening.id == screening_id).first()
                screening_booking.bookings.append(booking)
                db.session.commit()

                working_directory = Path(__file__).absolute().parent
                path_booking = os.path.join(working_directory, "static", "booking.csv")
                path_screening = os.path.join(working_directory, "static", "screening.csv")

                # Write data into booking.csv
                booking_list = Booking.query.all()
                booking_list_count = Booking.query.count()
                
                fieldnames_booking = [
                    'transaction_id', 
                    'user_id', 
                    'customer_name', 
                    'number_of_tickets', 
                    'date', 
                    'time', 
                    'movie_id', 
                    'screening_id',
                    'timestamp'
                ]

                # if creating booking for the first time
                if booking_list_count == 1:
                    # Write booking data to the booking.csv file
                    with open(path_booking, 'w') as file_booking:
                        writer = csv.DictWriter(file_booking, fieldnames=fieldnames_booking)
                        writer.writeheader()
                        for booking in booking_list:
                            row = {
                                'transaction_id': booking.id, 
                                'user_id': booking.user_id,
                                'customer_name': (current_user.first_name + " " + current_user.last_name),
                                'number_of_tickets': booking.number_of_tickets,
                                'date': booking.screenings[0].date, 
                                'time': booking.screenings[0].time, 
                                'movie_id': booking.screenings[0].movie_id,
                                'screening_id': booking.screenings[0].id,
                                'timestamp': booking.timestamp
                            }
                            writer.writerow(row)

                # if there are old booking already exists
                else:
                    # Append new booking entry to the booking.csv file
                    with open(path_booking, 'a', newline='') as file_booking:
                        writer = csv.DictWriter(file_booking, fieldnames=fieldnames_booking)
                        row = {
                            'transaction_id': booking.id, 
                            'user_id': booking.user_id,
                            'customer_name': (current_user.first_name + " " + current_user.last_name),
                            'number_of_tickets': booking.number_of_tickets,
                            'date': booking.screenings[0].date, 
                            'time': booking.screenings[0].time, 
                            'movie_id': booking.screenings[0].movie_id,
                            'screening_id': booking.screenings[0].id,
                            'timestamp': booking.timestamp
                        }
                        writer.writerow(row)

                # update available seats of the booked screening in screening csv file
                screening_list = Screening.query.all()

                # Create a temporary file in write mode ("w") to hold new values
                tempfile = NamedTemporaryFile(mode="w", delete=False)
                # Fieldnames are the columns for the csv file we wish to update
                fieldnames = [
                    'id',
                    'date',
                    'time',
                    'available_seats',
                    'theater_id',
                    'movie_id'
                ]

                
                # Open the csv file in read more ("r")
                # Then write into the temporary file first
                with open(path_screening, 'r') as file_screening, tempfile:
                    # Create reader and writer objects using csv library.
                    reader = csv.DictReader(file_screening, fieldnames=fieldnames)
                    writer = csv.DictWriter(tempfile, fieldnames=fieldnames)

                    # Loop every row in the screening file
                    for row_s in reader:
                        #  Change the value of available seats if id is the booked screening id.
                        if row_s["id"] == screening_id:
                            row_s["available_seats"] = new_number_of_seats

                        # write row into the temporary file
                        row = {
                            'id': row_s["id"],
                            'date': row_s["date"],
                            'time': row_s["time"],
                            'available_seats': row_s["available_seats"],
                            'theater_id': row_s["theater_id"],
                            'movie_id': row_s["movie_id"],
                        }
                        writer.writerow(row)

                # Move the temporary file to original csv.file, replacing the original screening.csv
                # shutil.move(source, destination) 
                shutil.move(tempfile.name, path_screening)

                flash("You've successfully booked the ticket!", category='success')
                return redirect(url_for('views.booking'))



@views.route('/myBooking', methods=['GET', 'POST'])
@login_required
def booking():
    """
    Route for the myBooking page.

    Renders the booking page to display the user's booking history.

    Returns:
        Response: The rendered template with user's booking history.
    """
    # Retrieve the user's bookings
    book = Booking.query.filter(Booking.user_id == current_user.id)
    # Retrieve the booking history including related screening, theater, and movie details
    booking_history = (db.session.query(Booking, Screening, Theater, Movie)
                       # Booking is the table on the left
                        .join(Screening, Booking.screenings)
                        .join(Theater)
                        .join(Movie)
                        .filter(Booking.user_id == current_user.id)
                        ).all()
    # Render the booking.html template and pass user data to the template, showing users the page of his booking history
    return render_template("booking.html", user=current_user, booking_history=booking_history)