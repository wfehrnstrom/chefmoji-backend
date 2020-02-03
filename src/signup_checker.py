import re
import sys
import os
sys.path.append(os.getcwd() + '/' + 'src/protocol_buffers')
import signupconfirm_pb2
sys.path.append(os.getcwd() + '/' + 'src/db')
from db import DBman
db = DBman()
class signup_checker:
    def __init__(self, email, playerid):
        self.email = email
        self.playerid = playerid
        self.message = signupconfirm_pb2.SignUpConfirmation()

    #checks if playerid is unique
    #checks if playerid has swear words
    def playerid_checker(self):
        #does it exist in the database
        playerid_not_unique = False
        #TODO: check if playerid has swear words
        playerid_not_clean = False

        if(playerid_not_clean):
            self.message.playerid = self.message.ErrorCode.notclean
        if(not db.is_player_id_unique(self.playerid)):
            self.message.playerid = self.message.ErrorCode.notunique
            playerid_not_unique = 1
        if(playerid_not_clean or playerid_not_unique):
            return 0
        return 1

    # checks if email is unique
    # checks if email is valid
    def email_checker(self):
        if(not db.is_email_unique(self.email)):
            self.message.email = self.message.ErrorCode.notunique
            return 0
        return 1

    def check(self):
        is_email_ok = self.email_checker()
        is_player_id_ok = self.playerid_checker()
        if(is_email_ok and is_player_id_ok):
            self.message.success = True

        #debug
        # return str(self.message.email) + ''
        return self.message



