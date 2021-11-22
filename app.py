from flask import Flask, Blueprint, current_app, g, render_template, redirect, request, flash, url_for, session
#from flask.cli import with_appcontext

import sqlite3

import random
import string

# creating the app
app = Flask(__name__)

def get_message_db():
    """
    Function handles creating the database of messages
    """
    # Checks whether there exists a "message_db" database in g
    if 'message_db' not in g:
        g.message_db = sqlite3.connect('messages_db.sqlite')

    # Check whether the messages table exists
    # Use command CREATE TABLE IF NOT EXISTS in 
    # the init.sql file
    with current_app.open_resource('init.sql') as f:
        g.message_db.executescript(f.read().decode('utf8'))

    # Return the connection
    return g.message_db
    
def insert_message(request):
    """
    Function handles inserting user mesasges to the 
    database of messages
    """
    db = get_message_db()
    # Extract message and handle from the request
    message = request.form['message']
    handle = request.form['handle']

    db.execute(
                'INSERT INTO messages (handle, message) VALUES (?, ?)',
                (handle, message)
            )
    db.commit()
    # Closing the connection!
    db = g.pop('message_db', None)
    if db is not None:
        db.close()

def random_messages(n):
    """
    Function returns a collection of n random messages
    from the 'message_db' database
    """
    # First we need to connect to the message_db
    # database
    db = get_message_db()
    # extracting random messages and handles from messages table
    rand_messages = db.execute(f'SELECT handle, message FROM messages ORDER BY RANDOM() LIMIT {n}').fetchall()
    # Close the connection!
    db = g.pop('message_db', None)
    if db is not None:
        db.close()
    return rand_messages


@app.route("/")
def main():
    return render_template("base.html")

@app.route("/submit/", methods=['POST', 'GET'])
def submit():
    if request.method == "GET":
        return render_template("submit.html")
    else:
        insert_message(request)
        return render_template("submit.html", thanks=True)


@app.route("/view/")
def view():
    return render_template("view.html", rand_messages = random_messages(3))
