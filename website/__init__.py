"""
This is the special file to define this directory as a package and a Python program that defines a Flask web application.
"""
# Import Flask library used to create web application
from flask import Flask
# Import SQLAlchemy library for database operations
from flask_sqlalchemy import SQLAlchemy
# Import LoginManager library for managing user authentication
from flask_login import LoginManager
# Import necessary modules for file I/O
import csv
from pathlib import Path
import os
# Import necessary modules to work with dates and times.
from datetime import datetime, timedelta
 
# Initialize a SQLAlchemy object named "db", which will be the database object to use when we want to manipulate the database
db = SQLAlchemy()
# Set the name of the database file to "database.db".
DB_NAME = "database.db"



def create_app():
    """
    Create the Flask application.

    Returns:
        app (Flask): Flask application object
    """

    # Initialize the Flask object named "app".
    # __name__ represents the name of the file that the program is going to run on
    app = Flask(__name__)

    # app.config is a dictionary containing key value pair.
    # Set up the SECRET_KEY configuration parameters for the Flask application,
    # It's used to secure the cookie and session data related to the website
    app.config['SECRET_KEY'] = 'cinema3000'

    # Set up the SQLALCHEMY_DATABASE_URI configuration parameter for the Flask application.
    # It specifies the location of the SQLite database file that the applicaiton will use. (URI = Unified Resource Identifier)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    # Set up the SQLALCHEMY_TRACK_MODIFICATIONS configuration parameter for the Flask application.
    # It disables the modification tracking feature of SQLAlchemy to improve performance.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    # Initialise database
    # Initializes the SQLAlchemy object "db" to be used by the Flask application. 
    # It tells the application to use the database we define earlier
    with app.app_context():
        db.init_app(app)


    # Blueprints are a way to organize a Flask application into reusable modules. 
    # Import two "blueprints" (views.py and auth.py) that define different parts of the web application.
    from .views import views
    from .auth import auth

    # Register blueprints with the Flask application so the application knows where blueprints are in the file
    # The url_prefix parameter specifies the URL prefix that should be used for each blueprint.
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Create database
    # 'app.app_context()' ensures that the Flask application context is set up properly before executing the code inside it.
    with app.app_context():
        # Drop any existing tables in the database
        db.drop_all()
        # Create the database tables
        db.create_all()
        print("Database Created!")
        # Initialize the database tables with initial data from csv files.
        insert_data()

    from .models import User

    # Creates a LoginManager object and assigns it to the login_manager variable. 
    # This object is responsible for managing user authentication and session management.
    login_manager = LoginManager()

    # Set the login_view attribute of the LoginManager object to 'auth.login'. 
    # This specifies the name of the view function that Flask-Login should redirect users to when they need to log in. 
    login_manager.login_view = 'auth.login'

    # 'init_app()' method is used to initialize the LoginManager object with the Flask application 
    # and allows Flask-Login to access the Flask application's configuration and other resources that it needs to function correctly.
    # By calling login_manager.init_app(app), the LoginManager object is associated with the Flask application instance 'app'. 
    login_manager.init_app(app)

    # The '@login_manager.user_loader' decorator is used to register 'load_user' function with Flask-Login. 
    # and specifies that 'load_user' should be called to load a user whenever Flask-Login needs to access information about the current user.
    @login_manager.user_loader
    def load_user(id):
        """
        Load a user from the database given their ID.

        Args:
            id (int): The ID of the user to load.

        Returns:
            User: The User object representing the loaded user.
        """
        # The User.query.get() method is used to look up the user in the database by their primary key (ID). 
        # This method returns the User object with the given primary key (ID), or None if the user is not found.
        # It defines a user_loader function that loads a user from the database given their ID.
        # User.query.get() the parameter will just look for primary key in the User model
        return User.query.get(int(id))

    # Return the Flask application object
    return app


# Import classes that are used in the function.
from .models import Movie, Theater, Screening, User, Booking

def insert_data():
    """
    Inserts data from csv files into the respective tables in the database.

    Returns:
        None
    """
    # Return a dictionary containing file paths for each csv files and assign it to paths
    paths = get_csv_paths()

    # Read the data from the user.csv file and insert it into the User table in the database.
    read_user_data(paths)

    # Read the data from the movie.csv file and insert it into the Movie table in the database. 
    # Return a dictionary containing the show times for each movie and assign it to show_times.
    show_times = read_movie_data(paths)

    # Read the data from the theater.csv file and insert it into the Theater table in the database. 
    # Return two dictionaries: available_movies and theater_seats and assign them to available_movies and theater_seats.
    available_movies, theater_seats = read_theater_data(paths)

    # Read the data from the screening.csv file.
    # Returns a set of dates on which screenings have already been scheduled.
    existing_dates = read_screening_data(paths)

    # Generate new screening data based on the movies available, the number of available seats, the show times, and the existing screening dates. 
    # The new screening data then is inserted into the Screening table in the database.
    create_new_screening_data(existing_dates, available_movies, theater_seats, show_times, paths)
    
    # Read the data from the booking.csv file and insert it into the Booking table in the database. 
    # Also create a relationship between the Screening and Booking tables by adding booking to screening's booking list.
    read_booking_data(paths)


def get_csv_paths():
    """
    Creates a dictionary that maps file names to their corresponding absolute paths on the local file system.

    Returns:
        dict: A dictionary with file names as keys and their corresponding absolute paths as values.
    """

    # Get absolute path of directory containing the current script file
    working_directory = Path(__file__).absolute().parent
    # Create a dictionary named paths that maps file names to their corresponding absolute paths on the local file system. 
    paths = {
        "movie": os.path.join(working_directory, "static", "movie.csv"),
        "theater": os.path.join(working_directory, "static", "theater.csv"),
        "user": os.path.join(working_directory, "static", "user.csv"),
        "booking": os.path.join(working_directory, "static", "booking.csv"),
        "screening": os.path.join(working_directory, "static", "screening.csv")
    }
    # Return a dictionary of paths
    return paths


def read_user_data(paths):
    """
    Reads data from user.csv into the user table in the database.

    Args:
        paths (dict): A dictionary containing the absolute paths of the csv files.

    Returns:
        None
    """
    # Open user.csv file for reading data
    with open(paths["user"], "r") as file:
        # Read its data into reader object
        reader = csv.DictReader(file)
        # Create a list of User objects using list comprehension to iterate over each row in the csv file.
        users = [User(email=row['email'], password=row['password'], first_name=row['first_name'], last_name=row['last_name']) for row in reader]
        # Add all users to the database
        db.session.add_all(users)
        # Commit changes to the database
        db.session.commit()


def read_movie_data(paths):
    """
    Reads data from movie.csv into the movie table in the database.

    Parameters:
        paths (dict): A dictionary containing the absolute paths of the csv files.

    Returns:
        show_times (dict): A dictionary that has movie title as key and a list of show times as value.

    """
    # Open movie.csv file for reading data
    with open(paths["movie"], "r") as file:
        # Read its data into reader object
        reader = csv.DictReader(file)
        # Initialize an empty list for movie objects
        movies = []
        # Initialize an empty dictionary for show times
        show_times = {}
        # Iterate over each row in the csv file
        for row in reader:
            # Convert release date string to datetime object.
            release_date = datetime.strptime(row['release_date'], '%Y-%m-%d').date()
            # Create Movie object with data from the row
            movie = Movie(title=row['title'], price=row['price'], release_date=release_date)
            # Append the Movie object to the list of movies
            movies.append(movie)
            # Store the show times for this movie in the show_times dictionary
            show_times[movie.title] = row['show_times'].split(", ")
        # Add all movies to the database
        db.session.add_all(movies)
        # Commit changes to the database
        db.session.commit()
        # Return the dictionary of show times
        return show_times


def read_theater_data(paths):
    """
    Read data from theater.csv into the theater table in the database.

    Args:
        paths (dict): A dictionary containing the absolute paths of the csv files.
        
    Returns:
        Tuple: A tuple containing two dictionaries. 
            The first dictionary has theater name as key and a list of available movies as value. 
            The second dictionary has theater name as key and the number of seats in the theater as value.
    """
    # Open theater.csv file for reading data
    with open(paths['theater'], "r") as file:
        # Read its data into reader object
        reader = csv.DictReader(file)
        # Initialize an empty list for theater objects
        theaters = []
        # Initialize an empty dictionary for storing available movies
        available_movies = {}
        # Initialize an empty dictionary for storing theater seats
        theater_seats = {}
        # Iterate over each row in the csv file
        for row in reader:
            # Create Theater object with data from the row
            theater = Theater(name=row['theater_name'], number_of_seats=row['number_of_seats'], available_movies=row['available_movies'])
            # Append the Theater object to the list of theaters
            theaters.append(theater)
            # Split the available_movies string into a list and add it to the available_movies dictionary
            available_movies[theater.name] = row['available_movies'].split(", ")
            # Add the number of seats for this theater to the theater_seats dictionary
            theater_seats[theater.name] = row['number_of_seats']
        # Add all movies to the database
        db.session.add_all(theaters)
        # Commit changes to the database
        db.session.commit()
        # Return the tuple of containing available_movies and theater_seats
        return available_movies, theater_seats


def read_screening_data(paths):
    """
    Read data from screening.csv into the Screening table in the database.

    Args:
        paths (dict): A dictionary containing the absolute paths of the csv files.
    
    Returns:
        existing_dates (set): A set containing all the existing dates in the screening.csv file. 
        If the file is empty, an empty set is returned.
    """
    # Open screening.csv file for reading data
    with open(paths['screening'], "r") as file:
        # Read its data into reader object
        reader = csv.DictReader(file)
        # If reader has any data, read it, otherwise return an empty set.
        if any(reader):
            screenings = []
            existing_dates = set()
            for row in reader:
                # Convert date and time strings to datetime objects for storing in the Screening table
                date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                time = datetime.strptime(row['time'], '%H:%M:%S').time()
                # Create a Screening object using data from the current row
                screening = Screening(date=date, time=time, available_seats=row['available_seats'], theater_id=row['theater_id'], movie_id=row['movie_id'])
                # Append the Screening object to the list of screenings
                screenings.append(screening)
                # Add the date to the set of existing dates
                existing_dates.add(date)
            # Add all screenings to the database
            db.session.add_all(screenings)
            # Commit changes to the database
            db.session.commit()
            # Return the set of existing dates in the screening.csv file
            return existing_dates
        else:
            # If there are no rows in the csv file
            existing_dates = set()
            # Return an empty set
            return existing_dates


def create_new_screening_data(existing_dates, available_movies, theater_seats, show_times, paths):
    """
    Create new screening data for a movie theater based on available movies and show times.
    Then store those data into the screening.csv file.

    Args:
        existing_dates (set): A set containing existing screening dates.
        available_movies (dict): A dictionary containing theater names as keys and available movies as values.
        theater_seats (dict): A dictionary containing theater names as keys and number of seats as values.
        show_times (dict): A dictionary containing movie titles as keys and a list of show times as values.
        paths (dict): A dictionary containing file paths.

    Returns:
        None

    """
    # Fieldnames for the screening.csv file for writing data
    fieldnames = [
        'id',
        'date',
        'time',
        'available_seats',
        'theater_id',
        'movie_id'
    ]

    # If no existing dates are provided, create new screenings for the next 7 days starting from today
    if not existing_dates:
        # Initialize an empty list for movie objects for screenings objects
        screenings = []
        # Create a dictionary using list comprehension with movie tile as key and movie id as value for indexing. 
        movie_ids = {movie.title: movie.id for movie in Movie.query.all()}
        # Create a dictionary using list comprehension with theater name as key and theater id as value for indexing.
        theater_ids = {theater.name: theater.id for theater in Theater.query.all()}
        today = datetime.now().date()
        duration = 7
        # Iterate through the next 7 days starting from today
        for i in range(duration):
            screening_date = today + timedelta(days = i)
            # Iterate over every theater
            for theater in available_movies:
                # Create data for number_of_seats using theater_seats dictionary for creating Screening object later
                number_of_seats = theater_seats[theater]
                # Iterate over each available movie for the current theater
                for movie in available_movies[theater]:
                    # If the movie matches the show times, create a screening for each time
                    if movie in show_times:
                        # Create data for movie_id and theater_id using movie_ids and theater_ids dictionary for creating Screening object later
                        movie_id = movie_ids[movie]
                        theater_id = theater_ids[theater]
                        # Iterate over every show times for the current movie
                        for time in show_times[movie]:
                            # Convert show time string to datetime object for storing in the screening table
                            time = datetime.strptime(time, '%H:%M').time()
                            # Create a Screening object using data for current screening
                            screening = Screening(date=screening_date, time=time, available_seats=number_of_seats, theater_id=theater_id, movie_id=movie_id)
                            # Append the Screening object to the list of Screenings
                            screenings.append(screening)
        # Add all screenings to the database
        db.session.add_all(screenings)
        # Commit changes to the database
        db.session.commit()

        # Query the database for all Screening objects and returns a list.
        screening_list = Screening.query.all()
        # Open screening.csv file for writing data
        with open(paths['screening'], 'w') as file:
            # Create a DictWriter object with fieldnames specified
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            # Write the header row to the CSV file
            writer.writeheader()
            # Iterate over each screening in the screening_list
            for screening in screening_list:
                # Create a dictionary with the screening data for each row in the CSV file
                row = {
                    'id': screening.id,
                    'date': screening.date,
                    'time': screening.time,
                    'available_seats': screening.available_seats,
                    'theater_id': screening.theater_id,
                    'movie_id': screening.movie_id
                }
                # Write the row to the CSV file
                writer.writerow(row)
    # If existing dates are provided, only create new screenings for dates that don't already exist
    else:
        # Initialize an empty list for movie objects for screenings objects
        screenings = []
        # Create a dictionary using list comprehension with movie tile as key and movie id as value for indexing. 
        movie_ids = {movie.title: movie.id for movie in Movie.query.all()}
        # Create a dictionary using list comprehension with theater name as key and theater id as value for indexing.
        theater_ids = {theater.name: theater.id for theater in Theater.query.all()}
        today = datetime.now().date()
        duration = 7
        # Iterate through the next 7 days starting from today
        for i in range(duration):
            screening_date = today + timedelta(days = i)
            # Only create screenings for new dates
            if screening_date not in existing_dates:
                # Iterate over every theater
                for theater in available_movies:
                    # Create data for number_of_seats using theater_seats dictionary for creating Screening object later
                    number_of_seats = theater_seats[theater]
                    # Iterate over each available movie for the current theater
                    for movie in available_movies[theater]:
                        # If the movie matches the show times, create a screening for each time
                        if movie in show_times:
                            # Create data for movie_id and theater_id using movie_ids and theater_ids dictionary for creating Screening object later
                            movie_id = movie_ids[movie]
                            theater_id = theater_ids[theater]
                            # Iterate over every show times for the current movie
                            for time in show_times[movie]:
                                # Convert show time string to datetime object for storing in the screening table
                                time = datetime.strptime(time, '%H:%M').time()
                                # Create a Screening object using data for current screening
                                screening = Screening(date=screening_date, time=time, available_seats=number_of_seats, theater_id=theater_id, movie_id=movie_id)
                                # Append the Screening object to the list of Screenings
                                screenings.append(screening)
        # Add all screenings to the database
        db.session.add_all(screenings)
        # Commit changes to the database
        db.session.commit()

        # Open screening.csv file for appending new line
        with open(paths['screening'], 'a') as file:
            # Create a DictWriter object with fieldnames specified
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            # Iterate over each screening (new data compared with the file) in the screenings
            for screening in screenings:
                # Create a dictionary with the screening data for each row in the CSV file
                row = {
                    'id': screening.id,
                    'date': screening.date,
                    'time': screening.time,
                    'available_seats': screening.available_seats,
                    'theater_id': screening.theater_id,
                    'movie_id': screening.movie_id
                }
                # Write the row to the CSV file
                writer.writerow(row)


def read_booking_data(paths):
    """
    Reads data from booking.csv into the booking table in the database and adds bookings to their respective screenings.

    Args:
        paths (dict): A dictionary containing file paths to the data files.

    Returns:
        None
    """
    # Open booking.csv file for reading data
    with open(paths['booking'], "r") as file:
        # Read its data into reader object
        reader = csv.DictReader(file)
        # Iterate over each row in the csv file
        for row in reader:
            # Get the screening id from the row
            screening_id = int(row['screening_id'])
            # Find the screening with the given id in the database
            screening = Screening.query.filter_by(id=screening_id).first()

            # If the screening is not found, skip to the next row
            if screening is None:
                continue
            
            # Convert the timestamp string from the CSV file to a datetime object
            timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
            # Create a new Booking object with the data from the row
            booking = Booking(number_of_tickets=row['number_of_tickets'], timestamp=timestamp, user_id=row['user_id'])
            # Add the booking to the screening's list of bookings (Booking and Screening has many-to-many relationship)
            screening.bookings.append(booking)
            # Commit the changes to the database
            db.session.commit()
