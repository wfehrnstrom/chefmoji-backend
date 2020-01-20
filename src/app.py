from flask import Flask
import argparse
from signup_checker import signup_checker

app = Flask(__name__)

@app.route("/")
def hello_world():
    checker =  signup_checker("hello@@gmail.com", "LAlala.,", "1234A.")
    return checker.check()