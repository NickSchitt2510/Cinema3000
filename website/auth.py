"""
The purpose of auth.py is to store the authentication routes for the website.
Blueprint allows the program view this file as a blueprint, which means this file will store routes of our application.
This way the app.py can be nicely organized and separate the views from application itself.
"""
# Import functions and classes from the Flask framework. 
# These are used for creating routes, rendering templates, handling requests, flashing messages, and redirecting.
from flask import Blueprint, render_template, request, flash, redirect, url_for
# Imports the user model from the current package, which define the database tables and their relationships
from .models import User
# Import the necessary function to hash passwords which is used to securely store and verify passwords.
from werkzeug.security import generate_password_hash, check_password_hash
# Import the 'db' object located in __init__.py from the current package (website) for database operations
from . import db
# Import necessary functions for user authentication.
from flask_login import login_user, login_required, logout_user, current_user
# Import necessary modules for file I/O
import csv
from pathlib import Path
import os

# Define a blueprint named 'auth' for this module.
# Blueprints are used to organize routes and views in Flask applications.
auth = Blueprint('auth', __name__)


# Define a route for the login page
@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Route for the login page.

    If a POST request is received:
        - Retrieves the email and password from the form submission.
        - Looks for a user with the given email in the database.
        - If a user is found:
            - Checks if the given password matches the hashed password stored in the database.
            - If the password matches, logs the user in and redirects to the home page.
            - If the password does not match, displays an error message.
        - If no user is found with the given email, displays an error message.

    If a GET request is received:
        - Renders the login page template.

    Returns:
        Response: The rendered template or a redirect response.
    """
    if request.method == "POST":
        # Get email and password from form submission
        email = request.form.get('email')
        password = request.form.get('password')

        # Look for user with the given email in the database
        user = User.query.filter_by(email=email).first()
        if user:
            # Check if the given password matches the hashed password stored in the database
            if check_password_hash(user.password, password):
                # If the password matches, log the user in
                flash("Logged in successfully!", category='success')
                # Keep user logged in after browsing session ends,until clearing its browsing history or session
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                # If the password does not match, display an error message
                flash("Incorrect password, try again.", category='error')
        else:
            # If no user is found with the given email, display an error message
            flash("Email does not exist.", category='error')
    # Render the login page template
    return render_template("login.html", user=current_user)


# Define a route for the logout functionality
@auth.route('/logout')
@login_required
def logout():
    """
    Route for the logout functionality.

    Logs the user out and redirects them to the login page.

    Returns:
        Response: A redirect response to the login page.
    """
    # Log the user out
    logout_user()
    flash("You've successfully log out!", category='success')
    # Redirect the user to the login page
    return redirect(url_for('auth.login'))


# Define a route for the registration page
@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Route for the registration page.

    If a POST request is received:
        - Retrieves the form input data.
        - Performs validation checks on the input data.
        - If the input data is valid:
            - Creates a new User object with the data and adds it to the database.
            - Logs the new user in and remembers the user.
            - Writes the new user's data to the user.csv file.
            - Flashes a success message to the user.
            - Redirects the user to the home page.
        - If the input data is invalid, flashes an error message to the user.

    If a GET request is received:
        - Renders the registration page template.

    Returns:
        Response: The rendered template or a redirect response.
    """
    if request.method == 'POST':
        # Get form input data from form submission
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # Perform validation checks on form input data
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 4 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 characters.', category='error')
        elif len(last_name) < 2:
            flash('Last name must be greater than 1 characters.', category='error')
        elif password1 != password2:
            flash('Password don\'t match', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            # If form input data is valid, create a new User object with the data and add it to the database
            new_user = User(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'))
            # add new_user to the database
            db.session.add(new_user)
            db.session.commit()
            # Log the new user in and remember the user
            login_user(new_user, remember=True)
            # Flash a message to the user with success category
            flash('Account created.', category='success')

            # Write new user database to user.csv
            # Get the absolute path of the directory where this script file resides
            working_directory = Path(__file__).absolute().parent
            # Get the path of the user.csv file
            path_user = os.path.join(working_directory, "static", "user.csv")
            
            # Get data from user
            # Get all the user objects from the database
            user_list = User.query.all()
            # Get the number of users in the database
            user_list_count = User.query.count()

            fieldnames = [
                'email', 'password', 'first_name', 'last_name'
                ]
            
            # if creating user for the first time
            if user_list_count == 1:
                # If the user.csv file is being created for the first time, open it in write mode
                with open(path_user, 'w') as file_user:
                    writer = csv.DictWriter(file_user, fieldnames=fieldnames)
                    # Write the header row to the csv file
                    writer.writeheader()
                    # Write each user's data as a row in the csv file
                    for user in user_list:
                        row = {
                            'email': user.email,
                            'password': user.password, 
                            'first_name': user.first_name, 
                            'last_name': user.last_name
                        }
                        writer.writerow(row)
            # add new user to the csv file
            else:
                with open(path_user, 'a', newline='') as file_user:
                    writer = csv.DictWriter(file_user, fieldnames=fieldnames)
                    row = {
                        'email': new_user.email, 
                        'password': new_user.password, 
                        'first_name': new_user.first_name, 
                        'last_name': new_user.last_name
                    }
                    writer.writerow(row)
                    
            # location for the home function in views. blueprint name.function name
            return redirect(url_for('views.home'))

    return render_template("register.html", user=current_user)
