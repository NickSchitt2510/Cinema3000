"""
This module defines several SQLAlchemy models representing different tables in a database. 
These tables are used in a Flask web application to store data related to user accounts, theaters, movies, screenings, and bookings. 

Methods:
    db.Column(type_, nullable=False, unique=False, primary_key=False, **kwargs):
        This method creates a column in the database table.
        A method provided by SQLAlchemy, a popular Object Relational Mapping (ORM) library for Python.

        Args:
            type_ (type): The data type of the column.
            nullable (bool, optional): Whether or not the column can be null. Defaults to False.
            unique (bool, optional): Whether or not the column values must be unique. Defaults to False.
            primary_key (bool, optional): Whether or not the column is a primary key. Defaults to False.
            **kwargs: Additional keyword arguments that are passed to the underlying SQLAlchemy column constructor.

        Returns:
            sqlalchemy.Column: A SQLAlchemy column object representing the database column.

    db.relationship(other, backref=None, lazy=True, uselist=True,  **kwargs):
        This method creates a relationship between two models.
        A method provided by SQLAlchemy, a popular Object Relational Mapping (ORM) library for Python.

        Args:
            other (str): The name of the other model in the relationship.
            backref (str or None, optional): The name of the attribute that will be added to the related model to reference the current model. Defaults to None.
            lazy (bool or str, optional): Controls how the related items are loaded. Defaults to True.
            uselist (bool, optional): Whether or not the relationship should return a list of items. Defaults to True.
            **kwargs: Additional keyword arguments that are passed to the underlying SQLAlchemy relationship constructor.

        Returns:
            sqlalchemy.orm.relationship: A SQLAlchemy relationship object representing the relationship between two models.

    db.ForeignKey(other_table, nullable=False, unique=False, primary_key=False, **kwargs):
        This method is used to specify which column in the current table references a column in another table when defining a relationship between two tables.
        A method provided by the Flask SQLAlchemy ORM which is used to define a foreign key in a relationship between two database tables.
        
        Args:
            other_table (str): The name of the other table and the column being referenced.
            nullable (bool): Whether or not the column can be null (default False).
            unique (bool): Whether or not the column values must be unique (default False).
            primary_key (bool): Whether or not the column is a primary key (default False).
            **kwargs: Additional keyword arguments that are passed to the underlying SQLAlchemy foreign key constructor.

        Returns:
            sqlalchemy.ForeignKey: A SQLAlchemy foreign key object representing the constraint.

    db.Table(name, *columns, **kwargs):
        Create a table that has no defined primary key, often used to create many-to-many relationships between models. 

        Args:
            name (str): The name of the table.
            *columns (Column): The list of columns to include in the table.
            **kwargs: Additional keyword arguments that are passed to the underlying SQLAlchemy Table constructor.

        Returns:
            sqlalchemy.Table: A SQLAlchemy Table object representing the database table.

    db.Model method is a class in Flask SQLAlchemy that serves as a base class for all the models defined in an application. 
    It provides the base structure and functions for the database models in a Flask SQLAlchemy application. 
    This class defines the columns and attributes of the database tables, and it also provides useful helper methods and relationships to other tables. 
    Using this method enables developers to work with a database more easily and efficiently. 
    With db.Model, developers can define columns, primary keys, foreign keys, and relationships between tables in their Flask applications.

"""

# Import the 'db' object located in __init__.py from the current package (website) for database operations
from . import db

# Import the UserMixin class from the flask_login module. 
# UserMixin provides some default implementations for the User model used by Flask-Login.
from flask_login import UserMixin

# Import the func object from the sqlalchemy module. 
# func is used to call SQL functions in SQLAlchemy and it is used in Booking model to create timestamp.
from sqlalchemy import func
    

class User(db.Model, UserMixin):
    """
    A class that represents a User model that inherits from two parent classes: db.Model and UserMixin.

        Inherits from:
            db.Model: The base class for all models in Flask SQLAlchemy.
            flask_login.UserMixin: A class that provides default implementations for the methods that Flask-Login expects user objects to have.

        Attributes:
            id (int): An integer column 'id' as the primary key of the User table.
            email (str): A string column 'email' that cannot be null and must be unique.
            password (str): A string column 'password' that cannot be null and will store hashed passwords.
            first_name (str): A string column 'first_name' that cannot be null.
            last_name (str): A string column 'last_name' that cannot be null.
            bookings (relationship): A one-to-many relationship between the User and Booking models, where each user can have multiple bookings.
            booked_by (pseudo column): A backref to the Booking table that allows easy access to the user who made the booking.

        Methods:
            __repr__(): Returns a string representation of the User object.
    """

    id = db.Column(db.Integer, primary_key=True)
    # Define an integer column 'id' as the primary key of the User table.
    email = db.Column(db.String(length=80), nullable=False, unique=True)
    # Define a string column 'email' that cannot be null and must be unique.
    password = db.Column(db.String(length=50), nullable=False)
    # Define a string column 'password' that cannot be null and will store hashed passwords.
    first_name = db.Column(db.String(length=20), nullable=False)
    # Define a string column 'first_name' that cannot be null.
    last_name = db.Column(db.String(length=20), nullable=False)
    # Define a string column 'last_name' that cannot be null.
    bookings = db.relationship('Booking', backref='booked_by', lazy=True)
    # Define a one-to-many relationship between the User and Booking models, where each user can have multiple bookings.
    # Add a pseudo column 'booked_by' using backref to the Booking table that allows easy access to the user who made the booking.


    def __repr__(self):
        """
        Return a string representation of the User object.

        This magic method returns a string representation of the User object that can be used for debugging purposes.
        The returned string contains the first and last name of the User object.
        
        Returns:
            str: A string representation of the User object.
        """
        return f'<User {self.first_name} {self.last_name}>'


class Theater(db.Model):
    """
    A class that represents a Theater model.

        Inherits from:
                db.Model: The base class for all models in Flask SQLAlchemy.

        Attributes:
            id (int): An integer column 'id' as the primary key of the User table.
            name (str): A string column 'name' of the theater.
            number_of_seats (int): An integer column 'number_of_seats' that cannot be null.
            available_movies (str): A string column 'available_movies' that stores movie ids separated by comma.
            screenings (relationship): A one-to-many relationship between the Theater and Screening models, where each theater can have multiple screenings.
            screening_location (pseudo column): A backref to the Screening table that allows easy access to the theater where the screening is happening.

        Methods:
            __repr__(): Returns a string representation of the Theater object.
    """
    id = db.Column(db.Integer, primary_key=True)
    # Define an integer column 'id' as the primary key of the Theater table.
    name = db.Column(db.String(30))
    # Define a string column 'name' that can be up to 30 characters long.
    number_of_seats = db.Column(db.Integer, nullable=False)
    # Define an integer column 'number_of_seats' that cannot be null.
    available_movies = db.Column(db.Text)
    # Define a text column 'available_movies' that can contain multiple movies separated by commas.
    screenings = db.relationship('Screening', backref='screening_location', lazy=True)
    # Define a one-to-many relationship between the Theater and Screening models, where each theater can have multiple screenings.
    # Add a pseudo column 'screening_location' using backref to the Screening table that allows easy access to the theater where the screening takes place.


    def __repr__(self):
        """Return a string representation of the Theater object.

        This magic method returns a string representation of the Theater object that can be used for debugging purposes.
        The returned string contains the name of the Theater object.
        
        Returns:
            str: A string representation of the Theater object.
        """
        return f'<Theater {self.name}>'


class Movie(db.Model):
    """
    A class that represents a Movie model.

        Inherits from:
            db.Model: The base class for all models in Flask SQLAlchemy.

        Attributes:
            id (int): An integer column 'id' as the primary key of the Movie table.
            title (str): A string column 'title' that cannot be null and can be up to 50 characters long.
            price (int): An integer column 'price' that can be null.
            release_date (date): A date column 'release_date' that cannot be null.
            screenings (relationship): A one-to-many relationship between the Movie and Screening models, where each movie can have multiple screenings.
            available_movies (pseudo column): A backref to the Screening table that allows easy access to the movie being screened.

        Methods:
            __repr__(): Returns a string representation of the Movie object.
    """ 
    id = db.Column(db.Integer, primary_key=True)
    # Define an integer column 'id' as the primary key of the Movie table.
    title = db.Column(db.String(50), nullable=False)
    # Define a string column 'title' that cannot be null and can be up to 50 characters long.
    price = db.Column(db.Integer)
    # Define an integer column 'price' that can be null.
    release_date = db.Column(db.Date, nullable=False)
    # Define a date column 'release_date' that cannot be null.
    screenings = db.relationship('Screening', backref='available_movies', lazy=True)
    # Define a one-to-many relationship between the Movie and Screening models, where each movie can have multiple screenings.
    # Add a pseudo column 'available_movies' using backref to the Screening table that allows easy access to the movie being screened.

    def __repr__(self):
        """Return a string representation of the Movie object.

        This magic method returns a string representation of the Movie object that can be used for debugging purposes.
        The returned string contains the title of the Movie object.
        
        Returns:
            str: A string representation of the Movie object.
        """
        return f'<Movie {self.title}>'


"""
The screening_booking table is used to create a many-to-many relationship between Booking and Screening.
since bookings can be made multiple times on a screening and a screening can be booked multiple times until seats ran out.
"""
screening_booking = db.Table('screening_booking',
    db.Column('screening_id', db.Integer, db.ForeignKey('screening.id')),
    db.Column('booking_id', db.Integer, db.ForeignKey('booking.id'))
    )


# A Table object 'screening_booking' is created using db.Table method that has two columns; 
# 'screening_id' and 'booking_id' which are foreign keys referencing 'id' columns of Screening and Booking tables, respectively.

class Screening(db.Model):
    """
    A class that represents a Screening model.

        Inherits from:
            db.Model: The base class for all models in Flask SQLAlchemy.

        Attributes:
            id (int): An integer column 'id' as the primary key of the Screening table.
            date (datetime): A date column 'date' representing the date of the screening.
            time (datetime): A time column 'time' representing the time of the screening.
            available_seats (int): An integer column 'available_seats' representing the number of available seats for the screening.
            theater_id (int): A foreign key column 'theater_id' referencing 'id' column of the Theater table.
            movie_id (int): A foreign key column 'movie_id' referencing 'id' column of the Movie table.
            bookings (relationship): A many-to-many relationship between the Screening and Booking models, where each screening can have multiple bookings and each booking can be applied to multiple screenings.

        Methods:
                __repr__(): Returns a string representation of the Screening object.
    """
    id = db.Column(db.Integer, primary_key=True)
    # Define an integer column 'id' as the primary key of the Screening table.
    date = db.Column(db.Date)
    # Define a date column 'date' representing the date of the screening.
    time = db.Column(db.Time)
    # Define a time column 'time' representing the time of the screening.
    available_seats = db.Column(db.Integer)
    # Define an integer column 'available_seats' representing the number of available seats for the screening.
    theater_id = db.Column(db.Integer, db.ForeignKey('theater.id'))
    # Define a foreign key column 'theater_id' referencing 'id' column of the Theater table.
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    # Define a foreign key column 'movie_id' referencing 'id' column of the Movie table.
    bookings = db.relationship('Booking', secondary=screening_booking, backref='screenings', lazy=True)
    # Define a many-to-many relationship between the Screening and Booking models, 
    # where each screening can have multiple bookings and each booking can be applied to multiple screenings.


    def __repr__(self):
        """Return a string representation of the Screening object.

        This magic method returns a string representation of the Screening object that can be used for debugging purposes.
        The returned string contains the id of the Screening object.

        Returns:
            str: A string representation of the Screening object.
        """
        return f'<Screening {self.id}>'


class Booking(db.Model):
    """
    A class that represents a Booking model.

        Inherits from:
                db.Model: The base class for all models in Flask SQLAlchemy.

        Attributes:
            id (int): An integer column 'id' as the primary key of the Booking table.
            number_of_tickets (int): An integer column 'number_of_tickets' that cannot be null and represents the number of tickets for a booking.
            timestamp (DateTime): A datetime column 'timestamp' that cannot be null and represents the date and time of a booking.
            user_id (int): An integer column 'user_id' that references the 'id' column in the User table using foreign key.

        Methods:
            __repr__(): Returns a string representation of the Booking object.
    """
    id = db.Column(db.Integer, primary_key=True)
    # Define an integer column 'id' as the primary key of the Booking table.
    number_of_tickets = db.Column(db.Integer, nullable=False)
    # Define an integer column 'number_of_tickets' that cannot be null and represents the number of tickets for a booking.
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())
    # Define a datetime column 'timestamp' that cannot be null and represents the date and time of a booking.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # Define an integer column 'user_id' that references the 'id' column in the User table using foreign key.

    def __repr__(self):
        """Return a string representation of the Booking object.

        This magic method returns a string representation of the Booking object that can be used for debugging purposes.
        The returned string contains the id of the Booking object.
        
        Returns:
            str: A string representation of the Booking object.
        """
        return f'<Booking {self.id}>'