from flask import Flask, flash
import argparse
from signup_checker import signup_checker
from mailconfirm.tokenconfirm import generate_confirmation_token, confirm_token

app = Flask(__name__, instance_relative_config=True)
# app.config.from_object('config')
app.config.from_pyfile('config.py')

#debug
from flask_mail import Mail
from flask_mail import Message
mail = Mail(app)

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
    email = "hellow@gmail.com"
    playerid = "hellowordlz"

    # Validate the email and playerid
    checker = signup_checker(email, playerid)
    if checker.check().success:
        # TODO: Write the username and playerid to the database
        # TODO: Hash the password again and store it in the database

        token = generate_confirmation_token(email, app.config['SECRET_KEY'], app.config['SECRET_SALT'])
        msg = Message("Hello, I am The chefmoji. Test token " + token,
                  sender=app.config['MAIL_DEFAULT_SENDER'],
                #   recipients=["esiswadi@g.ucla.edu", "wfehrnstrom@gmail.com", "mbshark@g.ucla.edu", "ychua@ucla.edu", "insiyab8@gmail.com", "ssmore12@g.ucla.edu"])
                recipients=["esiswadi@g.ucla.edu"])
        mail.send(msg)
        return token

@app.route("/emailconfirm/<token>")
def email_confirm(token):
    try:
        email = confirm_token(token, app.config['SECRET_KEY'], app.config['SECRET_SALT'])
    except:
        return 'OHNO'
        # flash('Your account is already confirmed', 'success')
    # TODO: check if email exists in the database
    # TODO: check if email is already confirmed

    # if email/user is confirmed
        # flash('Your account is already confirmed', 'success')
    # else
        # write to the database that the user is confirmed
        # flash('You have confirmed your account', 'success')

    # TODO: redirect to page to generate QRCODE for TOTP
    # return redirect(..TOTP page..)
    return email or ''
    # NOTE: working with flash on the front end - get_flashed_messages() https://pythonprogramming.net/flash-flask-tutorial/