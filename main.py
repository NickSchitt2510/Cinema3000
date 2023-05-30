"""
Cinema3000 Movie Theater Booking Website

Runs a Flask application and starts a web server.

This script imports a function called create_app from a module called website, which creates an instance of a Flask app.
The app is then run on a web server, using the app.run method. This method accepts various parameters, one of which is
debug, set to True in this script, which causes the web server to restart every time a change is detected in the code.

Attributes:
app: An instance of a Flask app.
"""
# Imports a function called create_app from a module called website, which creates an instance of a Flask app.
# Website is a custom created python package
from website import create_app

app = create_app()

# Only if we run this file directly, (not if we import this file) will the program execute the next line
if __name__ == '__main__':

    # Run the Flask application with debug mode enabled and start up a web server.
    app.run(debug=True)