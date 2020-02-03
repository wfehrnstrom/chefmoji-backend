from flask import Flask, flash, url_for, redirect
import argparse
import sys
import os
from signup_checker import signup_checker
from mailconfirm.tokenconfirm import generate_confirmation_token, confirm_token
from flask_mail import Mail
from flask_mail import Message
import sha3
import pyotp
sys.path.append(os.getcwd() + '/' + 'src/protocol_buffers')
import emailconfirm_pb2, loginconfirm_pb2
sys.path.append(os.getcwd() + '/' + 'src/db')
from db import DBman

#debug
# to dump object properties
from inspect import getmembers
from pprint import pprint

db = DBman()

app = Flask(__name__, instance_relative_config=True)
# app.config.from_object('config')
app.config.from_pyfile('config.py')

mail = Mail(app)

#debug
EMAIL = "auww@gmail.com"
PLAYERID = "auww"
PASSWORD = "IloveYoU3thoUsandxOXo"
EMAILSUBJHEADER = "Hello, I am The chefmoji👨‍🍳👩‍🍳"
totpOBJ = pyotp.TOTP('FWAKZJVKJMD6DHT7')
TOTP = totpOBJ.now()

@app.route("/register")
def register():
    # TODO: Get protobuf data from form
    # formdata.ParseFromString(request.form.get('protobuf'))
    # email = formdata.message.email
    # playerid = formdata.message.playerid
    # password = formdata.message.password
    # debug
    email = EMAIL
    playerid = PLAYERID
    password = PASSWORD

    # Hash the password again using sha3
    password = sha3.sha3_224(password.encode('utf-8')).hexdigest()

    # Validate the email and playerid
    checker = signup_checker(email, playerid)
    toreturn = checker.check()

    if toreturn.success:
        # Write the email and playerid and hashed password to the database
        # TODO: Try catch block, what if write fails.., set toreturn.success = False
        db.set_signupinfo(playerid, email, password)

        # TODO: Look at above to do, make sure write success before sending mail
        token = generate_confirmation_token(email, app.config['SECRET_KEY'], app.config['SECRET_SALT'])
        msg = Message(EMAILSUBJHEADER, sender = app.config['MAIL_USERNAME'],\
                recipients = [email])
                # recipients=["esiswadi@g.ucla.edu", "wfehrnstrom@gmail.com", "mbshark@g.ucla.edu", "ychua@ucla.edu", "insiyab8@gmail.com", "ssmore12@g.ucla.edu"])
        msg.body = url_for('email_confirm', token = token, _external=True)
        mail.send(msg)
    
    # debug
    pprint(getmembers(toreturn))

    return toreturn.SerializeToString()

@app.route("/emailconfirm/<token>")
def email_confirm(token):
    # return a protobuf message
    toreturn = emailconfirm_pb2.EmailConfirmation()
    try:
        email = confirm_token(token, app.config['SECRET_KEY'], app.config['SECRET_SALT'])
    except:
        toreturn.success = False
        toreturn.status = toreturn.ErrorCode.doesnotexist
        # debug
        pprint(getmembers(toreturn))

        return toreturn.SerializeToString()

    if not db.is_email_unique(email): # if email exists in the database
        if db.is_account_verified('', email):
            toreturn.success = True
            toreturn.status = toreturn.ErrorCode.prevconfirmed
        else: 
            # set verified flag in db and write mfa key to datbase
            if db.verify_account(email):
                # TODO: handle if this fails
                totpkey = db.set_totp_key(email)
                
                toreturn.success = True
                toreturn.status = toreturn.ErrorCode.justconfirmed
                toreturn.totpkey = totpkey
            else: # failed to write to db
                toreturn.success = False
                toreturn.status = toreturn.ErrorCode.otherfailures
    else: #if email DOES NOT EXIST in the database
        toreturn.success = False
        toreturn.status = toreturn.ErrorCode.doesnotexist
    
    # debug
    pprint(getmembers(toreturn))
    return toreturn.SerializeToString()
    # NOTE: working with flash on the front end - get_flashed_messages() https://pythonprogramming.net/flash-flask-tutorial/

@app.route("/login")
def login():
    # TODO: Get protobuf data from form
    # formdata.ParseFromString(request.form.get('protobuf'))
    # playerid = formdata.message.playerid
    # password = formdata.message.password
    # totp = formdata.message.password
    # debug
    playerid = PLAYERID
    password = PASSWORD
    totp = TOTP

    # hash password
    password = sha3.sha3_224(password.encode('utf-8')).hexdigest()

    # return a protobuf message
    toreturn = loginconfirm_pb2.LoginConfirmation()

    # call DBman to check
    toreturn = db.check_login_info(playerid, password, totp, toreturn)

    # if toreturn.success:
        # TODO: start the socket connection

    #debug
    pprint(getmembers(toreturn))
    return toreturn.SerializeToString()

# TODO: Change this to server our home page
@app.route("/")
def hello_world():
    checker =  signup_checker(EMAIL, PLAYERID)
    return str(checker.check().playerid) #returns an object of the protobuf
#debug route
@app.route("/testdb")
def test_db():
    # totp = pyotp.TOTP('RM2K7MBFXURNP3YA')
    # print(str(sha3.sha3_224('IloveYoU3thoUsandxOXo'.encode('utf-8')).hexdigest()))
    # return str(db.check_login_info("alice", str(sha3.sha3_224('IloveYoU3thoUsandxOXo'.encode('utf-8')).hexdigest()), totp.now()))
    # # return "HAPPY"
    # return str(db.update_counter('alice'))
    # return str(db.is_cooldown('alice'))
    
    toreturn = loginconfirm_pb2.LoginConfirmation()
    pprint(getmembers(db.check_login_info(PLAYERID, PASSWORD, TOTP, toreturn)))
    return 'check terminal'