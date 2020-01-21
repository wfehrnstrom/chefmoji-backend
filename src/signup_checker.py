import re
import sys
import os
sys.path.append(os.getcwd() + '/' + 'src/protocol_buffers')
import signupconfirm_pb2

class signup_checker:
    def __init__(self, email, playerid):
        self.email = email
        self.playerid = playerid
        self.message = signupconfirm_pb2.SignUpConfirmation()

    #checks if playerid is unique
    #checks if playerid has swear words
    def playerid_checker(self):
        #does it exist in the database
        #TODO: call the DB manager to check if playerid exists
        playerid_not_unique = False
        #TODO: check if email exists (valid)
        playerid_not_clean = False

        if(playerid_not_unique):
            self.message.playerid = self.message.ErrorCode.notunique
        if(playerid_not_clean):
            self.message.playerid = self.message.ErrorCode.notclean

    # checks if email is unique
    # checks if email is valid
    def email_checker(self):
        #TODO: call the DB manager to check if email exists
        email_not_unique = False
        #TODO: check if email exists (valid)
        email_exists = False

        if(email_exists):
            self.message.email = self.message.ErrorCode.notvalid
        if(email_not_unique):
            self.message.email = self.message.ErrorCode.notunique

    def check(self):
        self.email_checker()
        self.playerid_checker()

        return self.message.SerializeToString()



