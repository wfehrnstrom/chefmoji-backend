import re
from protocol_buffers import signupconfirm_pb2
from db.db import DBman
from email_validator import validate_email, EmailNotValidError

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
        #is the playerid valid
        if len(playerid) < 6 or len(playerid) > 20:
            self.message["playerid"] = "NOTVALID"
            return 0

        #check if playerid has swear words
        with open("profanitytext.txt", "r") as f:
            if(any(line in playerid for line in f)):
                self.message["playerid"] = "NOTCLEAN"
                return 0

        #does it exist in the database
        if(not db.is_player_id_unique(self.playerid)):
            self.message["playerid"] = "NOTUNIQUE"
            return 0

        self.message["playerid"] = "GOOD"
        return 1

    # checks if email is unique
    # checks if email is valid
    def email_checker(self):
        try:
            v = validate_email(email) # validate and get info
            # email = v["email"] # replace with normalized form
        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            # print(str(e))
            self.message["email"] = "NOTVALID"
            return 0

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
