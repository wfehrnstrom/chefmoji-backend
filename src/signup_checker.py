import re
from password_strength import PasswordPolicy

import sys
import os
sys.path.append(os.getcwd() + '/' + 'src/protocol_buffers')
import signupconfirm_pb2

#debug
from pprint import pprint

class signup_checker:
    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password = password
        self.message = signupconfirm_pb2.SignUpConfirmation()

    def username_checker(self):
        #does it exist in the database
        #TODO: call the DB manager to check if username exists
        username_unique = False

        if(len(self.username) <= 2 or len(self.username) >= 20):
            self.message.username = self.message.UsernameCode.length
        if(not username_unique):
            self.message.username = self.message.UsernameCode.unique

    def email_checker(self):
        email_regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
        self.message.email = False
        if(re.search(email_regex, self.email)):
            self.message.email = True

    def password_checker(self):
        policy = PasswordPolicy.from_names(
            length=8,  # min length: 8
            uppercase=2,  # need min. 2 uppercase letters
            numbers=2,  # need min. 2 digits
            special=2,  # need min. 2 special characters
        )
        self.message.password = ",".join(map(str, policy.test(self.password)))

    def check(self):
        self.password_checker()
        self.email_checker()
        self.username_checker()

        #debug
        message2 = signupconfirm_pb2.SignUpConfirmation()
        message2.ParseFromString(self.message.SerializeToString())
        pprint(message2.email)

        return self.message.SerializeToString()



