import mysql.connector as mysql
import pyotp
import os
import sha3
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from password_generator import PasswordGenerator

# TODO: AWS MySQL Version is 8.0.16. Check that mysql-python-connector is configured to cater to this version

# TODO: Potential security vulnerability here if attacker hot swaps .env for their own.
load_dotenv(find_dotenv())

class DBValueError(ValueError):
    pass

class DBman:
    def __init__(self, logging=None):
        if self.db_credentials_found():
            try:
                self.db = mysql.connect(
                    host = os.getenv("DB_HOSTNAME"),
                    user = os.getenv("DB_USERNAME"),
                    passwd = os.getenv("DB_PASSWORD"),
                    database = os.getenv("DB_NAME")
                )
                self.cursor = self.db.cursor(buffered=True)
                self.tbl_user = 'tbl_user'
            except mysql.errors.InterfaceError:
                if logging:
                    logging.error("Unable to connect to database")
        else:
            raise DBValueError("Database credentials not set or table name invalid.")

    def db_credentials_found(self):
        return (os.getenv("DB_HOSTNAME") is not None and os.getenv("DB_USERNAME") is not None and os.getenv("DB_PASSWORD") is not None
            and os.getenv("DB_NAME") is not None)

    def db_read_query(self, query, params):
        try:
            self.cursor.execute(query, params)
        except Exception as err:
            print('DB exception: %s' % err)
            print(query)
            raise

    # insert, update, delete
    def db_write_query(self, query, params):
        try:
            self.cursor.execute(query, params)
            self.db.commit()
        except Exception as err:
            self.db.rollback()
            print('DB exception: %s' % err)
            print(query, params)
            raise

    def is_player_id_unique(self, player_id):
        query = f"\
            SELECT COUNT(1)\
              FROM {self.tbl_user} t\
             WHERE t.player_id=%(player_id)s"

        params = {'player_id': player_id}
        self.db_read_query(query, params)
        result = self.cursor.fetchone()
        if result and result[0] == 0:
            return True
        else:
            return False

    def email_exists_in_db(self, email):
        query = f"\
            SELECT COUNT(1)\
              FROM {self.tbl_user} t\
             WHERE t.email=%(email)s"
        params = {'email': email}

        self.db_read_query(query, params)
        result = self.cursor.fetchone()
        if result and result[0] == 0:
            return False
        else:
            return True

    def is_account_verified(self, player_id=''):
        query = f"\
            SELECT t.verified\
              FROM {self.tbl_user} t\
             WHERE t.player_id=%(player_id)s"

        self.db_read_query(query, {'player_id': player_id})
        result = self.cursor.fetchone()
        if result and result[0] == 1:
            return True
        else:
            return False

    def is_account_verified2(self, email=''):
        query = f"\
            SELECT t.verified\
              FROM {self.tbl_user} t\
             WHERE t.email=%(email)s"
        self.db_read_query(query, {'email': email})
        result = self.cursor.fetchone()

        if result and result[0] == 1:
            return True
        else:
            return False

    def set_signupinfo(self, player_id, email, password):
        values = (player_id, email, password)
        self.db_write_query("INSERT INTO tbl_user (player_id, email, password) VALUES (%s, %s, %s)", values)

    def verify_account(self, email):
        query = f"\
            UPDATE {self.tbl_user}\
               SET verified=TRUE\
             WHERE email=%(email)s"
        self.db_write_query(query, {'email': email})

    def set_totp_key(self, email):
        totpkey = pyotp.random_base32()

        query = f"\
            UPDATE {self.tbl_user}\
               SET mfa_key=%(totpkey)s\
             WHERE email=%(email)s"
        self.db_write_query(query, {'totpkey': totpkey, 'email': email})
        return totpkey

    def generate_new_pwd(self):
        pwo = PasswordGenerator()
        pwo.minlen = 10
        pwo.maxlen = 30
        pwo.minuchars = 1
        pwo.minlchars = 1
        pwo.minnumbers = 1
        pwo.minschars = 1
        return pwo.generate()

    def set_temp_pwd(self, email):
        password = self.generate_new_pwd()
        # need to hash it twice, because the browser hashes it once
        hashed = sha3.sha3_256(sha3.sha3_256(password.encode('utf-8')).hexdigest().encode('utf-8')).hexdigest()

        query = f"\
            UPDATE {self.tbl_user}\
               SET password=%(hashed)s\
             WHERE email=%(email)s"
        self.db_write_query(query, {'hashed': hashed, 'email': email})
        return password

    def get_totpkey_from_email(self, email):
        query = f"\
            SELECT mfa_key\
            FROM {self.tbl_user}\
            WHERE email=%(email)s"
        self.db_read_query(query, {'email': email})
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return ''

    def check_totp(self, email, totp):
        totpkey = self.get_totpkey_from_email(email)
        if totpkey:
            totp_checker = pyotp.TOTP(totpkey)
            return totp_checker.verify(totp, valid_window=1)
        else:
            return False

    def check_login_info(self, player_id, password, totp, message):
        message["success"] = False
        print(player_id)
        if self.is_account_verified(player_id):
            # check if cooldown, execute below, else say that it is in cooldown
            if not self.in_cooldown(player_id):
                # reset counter if time and then and update timestamp to now
                self.update_counter(player_id, 'ifcooldownended')

                query = f"\
                    SELECT mfa_key\
                    FROM {self.tbl_user}\
                    WHERE player_id=%(player_id)s AND password=%(password)s"
                self.db_read_query(query, {'player_id': player_id, 'password': password})

                result = self.cursor.fetchone()
                if result:
                    totp_checker = pyotp.TOTP(str(result[0]))

                    if totp_checker.verify(totp, valid_window=1):
                        # reset counter = 0
                        self.update_counter(player_id, 'loginsuccessful')
                        message["success"] = True
                        message["status"] = "GOOD"
                    else:
                        # counter++
                        self.counterpp(player_id)
                        message["status"] = "BADINPUT"
                else:
                    # counter++
                    self.counterpp(player_id)
                    message["status"] = "BADINPUT"
            else:
                message["status"] = "INCOOLDOWN"
        else:
            message["status"] = "NOTVERIFIED"
        self.update_timestamp(player_id)
        return message

    # reset login_counter to 0 if timestampdiff >= 5
    # reset login_counter to 0 after successful login
    def update_counter(self, player_id, case):
        query = ''
        if case == 'ifcooldownended':
            query = f"\
                UPDATE {self.tbl_user}\
                SET login_counter=0\
                WHERE player_id=%(player_id)s AND (TIMESTAMPDIFF(MINUTE, timestamp, LOCALTIME())>=5)"
        elif case == 'loginsuccessful':
            query = f"\
                UPDATE {self.tbl_user}\
                SET login_counter=0\
                WHERE player_id=%(player_id)s"

        self.db_write_query(query, {'player_id': player_id})

    # reset timestamp to now
    def update_timestamp(self, player_id):
        query_update_timestamp = f"\
            UPDATE {self.tbl_user}\
               SET timestamp=LOCALTIME()\
             WHERE player_id=%(player_id)s"
        self.db_write_query(query_update_timestamp, {'player_id': player_id})

    # increment failed login attempts counter and update timestamp
    def counterpp(self, player_id):
        query = f"\
            UPDATE {self.tbl_user}\
               SET login_counter=login_counter+1\
             WHERE player_id=%(player_id)s"
        self.db_write_query(query, {'player_id': player_id})

    # check if player is still in a cooldown
    def in_cooldown(self, player_id):
        query = f"\
            SELECT COUNT(1)\
              FROM {self.tbl_user}\
             WHERE player_id=%(player_id)s AND (login_counter<5 OR TIMESTAMPDIFF(MINUTE, timestamp, LOCALTIME())>5)"
        self.db_read_query(query, {'player_id': player_id,})
        result = self.cursor.fetchone()

        if result and result[0]==1:
            return False
        else:
            return True

    def get_player_id(self, email):
        query = f"\
            SELECT player_id\
              FROM {self.tbl_user}\
             WHERE email=%(email)s"

        params = {'email': email}
        self.db_read_query(query, params)
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return ''

if __name__ == '__main__':
    db = DBman()
    print(db.is_player_id_unique('xxxxxx'))