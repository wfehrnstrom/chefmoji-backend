import re
from protocol_buffers import signupconfirm_pb2
from db.db import DBman

db = DBman()

class signup_checker:
    def __init__(self, email, playerid):
        self.email = email
        self.playerid = playerid
        self.message = {
            "success": False,
            "email": "OTHERFAILURES", # GOOD, NOTUNIQUE, NOTCLEAN, NOTVALID, OTHERFAILURES
            "playerid": "OTHERFAILURES", # GOOD, NOTUNIQUE, NOTCLEAN, NOTVALID, OTHERFAILURES
        }
        self.check()

    #checks if playerid is unique
    #checks if playerid has swear words
    def playerid_checker(self):
        #does it exist in the database
        playerid_not_unique = False
        #TODO: check if playerid has swear words
        playerid_not_clean = False

        if(playerid_not_clean):
            self.message["playerid"] = "NOTCLEAN"
        if(not db.is_player_id_unique(self.playerid)):
            self.message["playerid"] = "NOTUNIQUE"
            playerid_not_unique = 1
        if(playerid_not_clean or playerid_not_unique):
            return 0
        self.message["playerid"] = "GOOD"
        return 1

    # checks if email is unique
    # checks if email is valid
    def email_checker(self):
        if(db.email_exists_in_db(self.email)):
            self.message["email"] = "NOTUNIQUE"
            return 0
        self.message["email"] = "GOOD"
        return 1

    def check(self):
        try:
            # cannot be in one line because we want to run both checkers
            is_email_unique = self.email_checker()
            is_player_id_unique = self.playerid_checker()
            self.message["success"] = is_email_unique and is_player_id_unique
        except:
            self.message["success"] = False
            self.message["email"] = "OTHERFAILURES"
            self.message["playerid"] = "OTHERFAILURES"
        finally:
            return self.message