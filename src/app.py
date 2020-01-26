from flask import Flask
import argparse
from signup_checker import signup_checker
from tokenABC import generate_confirmation_token

app = Flask(__name__, instance_relative_config=True)
# app.config.from_object('config')
app.config.from_pyfile('config.py')

@app.route("/")
def hello_world():
    checker =  signup_checker("hello@@gmail.com", "LAlala.,")
    return checker.check() #returns an object of the protobuf

@app.route("/register")
def register():
    # TODO: Get protobuf data from form
    # formdata.ParseFromString(request.form.get('protobuf'))
    # email = formdata.message.email
    # playerid = formdata.message.playerid
    # password = formdata.message.password
    # debug
    email = "hello@gmail.com"
    playerid = "hellowordlz"

    # Validate the email and playerid
    checker = signup_checker(email, playerid)
    if checker.check().success:
        # TODO: write the username and playerid to the database
        # TODO: Hash the password again and store it in the database

        tokenz = generate_confirmation_token(email, app.config['SECRET_KEY'], app.config['SECRET_SALT'])
        return tokenz