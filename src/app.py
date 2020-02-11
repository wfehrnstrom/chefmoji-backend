from flask import Flask, flash, url_for, redirect
import argparse
from signup_checker import signup_checker
from mailconfirm.tokenconfirm import generate_confirmation_token, confirm_token
from flask_mail import Mail
from flask_mail import Message
import sha3
import pyotp
import os
from protocol_buffers import emailconfirm_pb2, loginconfirm_pb2
from db.db import DBman
#debug - to dump object properties
from inspect import getmembers
from pprint import pprint

app = Flask(__name__, instance_relative_config=True)
# mail settings
app.config['MAIL_SERVER']=os.getenv('MAIL_SERVER')
app.config['MAIL_PORT']=os.getenv('MAIL_PORT')
app.config['MAIL_USE_SSL']=os.getenv('MAIL_USE_SSL')
app.config['MAIL_DEFAULT_SENDER']=os.getenv('MAIL_DEFAULT_SENDER')
app.config['MAIL_USERNAME']=os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD']=os.getenv('MAIL_PASSWORD')

db = DBman()
mail = Mail(app)

#debug
import sys
sys.dont_write_bytecode = True

#debug
EMAIL = "cad@gmail.com"
PLAYERID = "cad"
PASSWORD = "IloveYoU3thoUsandxOXo"
EMAILSUBJHEADER = "Hello, I am The chefmoji👨‍🍳👩‍🍳"
totpOBJ = pyotp.TOTP('DI27D62NOARZAUKG')
TOTP = totpOBJ.now()

@app.route("/register")
def register():
    # TODO: Get protobuf data from form
    # debug
    email = EMAIL
    playerid = PLAYERID
    password = PASSWORD

    # Hash the password again using sha3
    password = sha3.sha3_256(password.encode('utf-8')).hexdigest()

    # Validate the email and playerid
    checker = signup_checker(email, playerid)


    if checker.message.success:
        try:
            # Write the email and playerid and hashed password to the database
            db.set_signupinfo(playerid, email, password)
        except Exception as err:
            print("%s" % err)
            checker.message.success = False
            checker.message.email = checker.message.ErrorCode.otherfailures
            checker.message.playerid = checker.message.ErrorCode.otherfailures
            return checker.message.SerializeToString()
        try:
            # TODO: Look at above to do, make sure write success before sending mail
            token = generate_confirmation_token(email, os.getenv('SECRET_KEY'), os.getenv('SECRET_SALT'))
            msg = Message(EMAILSUBJHEADER, sender = os.getenv('MAIL_USERNAME'),\
                    recipients = [email])
                    # recipients=["esiswadi@g.ucla.edu", "wfehrnstrom@gmail.com", "mbshark@g.ucla.edu", "ychua@ucla.edu", "insiyab8@gmail.com", "ssmore12@g.ucla.edu"])
            msg.body = url_for('email_confirm', token = token, _external=True)
            mail.send(msg)
        except Exception as err:
            print("%s" % err)
            return checker.message.SerializeToString()
    # debug
    pprint(getmembers(checker.message))

    return checker.message.SerializeToString()

@app.route("/emailconfirm/<token>")
def email_confirm(token):
    # return a protobuf message
    toreturn = emailconfirm_pb2.EmailConfirmation()
    try:
        email = confirm_token(token, os.getenv('SECRET_KEY'), os.getenv('SECRET_SALT'))
    except:
        toreturn.success = False
        toreturn.status = toreturn.ErrorCode.doesnotexist
        # debug
        pprint(getmembers(toreturn))

        return toreturn.SerializeToString()

    try:
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
    except:
        toreturn.success = False
        toreturn.status = toreturn.ErrorCode.otherfailures
        # debug
        print('here1')
        # pprint(getmembers(toreturn))
        return toreturn.SerializeToString()

    # debug
    # pprint(getmembers(toreturn))
    print('here1')
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
    password = sha3.sha3_256(password.encode('utf-8')).hexdigest()

    # return a protobuf message
    toreturn = loginconfirm_pb2.LoginConfirmation()

    # call DBman to check
    toreturn = db.check_login_info(playerid, password, totp, toreturn)

    # if toreturn.success:
        # TODO: redirect to home page
    #debug
    pprint(getmembers(toreturn))
    return toreturn.SerializeToString()

# TODO: Change this to server our home page
@app.route("/")
def hello_world():
    return 'Hello Helloo WORLD'