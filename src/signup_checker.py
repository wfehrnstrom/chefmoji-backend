import re
from protocol_buffers import signupconfirm_pb2
from db.db import DBman

db = DBman()

class signup_checker:
    def __init__(self, email, playerid):
        self.email = email
        self.playerid = playerid
        self.message = signupconfirm_pb2.SignUpConfirmation()
        self.check()

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
        try:
            if(not db.is_email_unique(self.email)):
                self.message.email = self.message.ErrorCode.notunique
                return 0
            return 1
        except:
            raise

    def check(self):
        try:
            # cannot be in one line because we want to run both checkers
            is_email_unique = self.email_checker()
            is_player_id_unique = self.playerid_checker()
            self.message.success = is_email_unique and is_player_id_unique
        except:
            self.message.success = False
            self.message.email = self.message.ErrorCode.otherfailures
            self.message.playerid = self.message.ErrorCode.otherfailures
        finally:
            return self.message



