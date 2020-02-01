from flask import Flask, flash, url_for, redirect
import argparse
from signup_checker import signup_checker
from mailconfirm.tokenconfirm import generate_confirmation_token, confirm_token
from flask_mail import Mail
from flask_mail import Message
import sha3
import pyotp

app = Flask(__name__, instance_relative_config=True)
# app.config.from_object('config')
app.config.from_pyfile('config.py')

mail = Mail(app)

# TODO: Change this to server our home page
@app.route("/")
def hello_world():
    checker =  signup_checker("hello@@gmail.com", "LAlala.,")
    return checker.check() #returns an object of the protobuf

@app.route("/login")
def login():
    # TODO: Get protobuf data from form
    # formdata.ParseFromString(request.form.get('protobuf'))
    # playerid = formdata.message.playerid
    # password = formdata.message.password
    # totp = formdata.message.password
    # debug
    playerid = "hellowordlz"
    password = "iloveyou"
    totp = ""

    # hash password
    password = sha3.sha3_224(password.encode('utf-8')).hexdigest()

    # TODO: call DBman to check

    # TODO: call DBman to return a totp object from
        # totp_obj = pyotp.TOTP('secrettotpkey')
    
    # TODO: totp_obj.verify('totp') 



@app.route("/register")
def register():
    # TODO: Get protobuf data from form
    # formdata.ParseFromString(request.form.get('protobuf'))
    # email = formdata.message.email
    # playerid = formdata.message.playerid
    # password = formdata.message.password
    # debug
    email = "chefmojimoji@gmail.com"
    playerid = "hellowordlz"
    password = "iloveyou"

    # Hash the password again using sha3
    password = sha3.sha3_224(password.encode('utf-8')).hexdigest()

    # Validate the email and playerid
    checker = signup_checker(email, playerid)

    if checker.check().success:
        # TODO: Write the username and playerid and hashed password to the database

        token = generate_confirmation_token(email, app.config['SECRET_KEY'], app.config['SECRET_SALT'])
        msg = Message('Hello, I am The chefmoji👨‍🍳👩‍🍳', sender = 'chefmojimoji@gmail.com',\
                recipients = [email])
                # recipients=["esiswadi@g.ucla.edu", "wfehrnstrom@gmail.com", "mbshark@g.ucla.edu", "ychua@ucla.edu", "insiyab8@gmail.com", "ssmore12@g.ucla.edu"])
        msg.body = url_for('email_confirm', token = token, _external=True)

        mail.send(msg)
        return token

@app.route("/emailconfirm/<token>")
def email_confirm(token):
    try:
        email = confirm_token(token, app.config['SECRET_KEY'], app.config['SECRET_SALT'])
    except:
        # debug
        return 'OHNO'
        # flash('Your account is already confirmed', 'success')
    # TODO: check if email exists in the database
    # TODO: check if email is already confirmed

    #debug
    totpkey = ''
    if(True):
    # if email/user is confirmed
        # flash('Your account is already confirmed', 'success')
        # implement PYOTP here
        totpkey = pyotp.random_base32()
        # TODO: Store totpkey in database        
    # else
        # write to the database that the user is confirmed
        # flash('You have confirmed your account', 'success')

    # TODO: redirect to page to generate QRCODE for TOTP 
    # (IMPORTANT! NO LET'S NOT REDIRECT FOR NOW, JUST SEND TOTP ALONG WITH SUCCESS CONFIRM PAGE)
    # return redirect(..TOTP page..)

    # debug
    return (email + '\nkey: ' + str(totpkey)) or ''
    # NOTE: working with flash on the front end - get_flashed_messages() https://pythonprogramming.net/flash-flask-tutorial/