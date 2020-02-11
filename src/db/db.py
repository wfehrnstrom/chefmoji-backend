import mysql.connector as mysql
import pyotp
import os

class DBman:
    def __init__(self):
        self.db = mysql.connect(
            host = "localhost",
            user = os.getenv("DB_USERNAME"),
            passwd = os.getenv("DB_PASSWORD"),
            database = os.getenv("DB_NAME")
        )
        self.cursor = self.db.cursor()
        self.tbl_user = 'tbl_user'

    def db_read_query(self, query, params):
        try:
            self.cursor.execute(query, params)
        except Exception as err:
            print('DB exception: %s' % err)
            raise

    # insert, update, delete
    def db_write_query(self, query, params):
        try:
            self.cursor.execute(query, params)
            self.cursor.commit()
        except Exception as err:
            self.cursor.rollback()
            print('DB exception: %s' % err)
            raise

    def is_email_unique(self, email):
        query = f"\
            SELECT COUNT(1)\
              FROM {self.tbl_user} t\
             WHERE t.email=%(email)s"
        params = {'email': email}

        try:
            self.db_read_query(query, params)
            if self.cursor.fetchone()[0] > 0:
                return False
            else:
                return True
        except:
            raise

    def is_account_verified(self, player_id='', email=''):
        query = f"\
            SELECT t.verified\
              FROM {self.tbl_user} t\
             WHERE t.email=%(email)s or t.player_id=%(player_id)s"
        self.cursor.execute(query, {'player_id': player_id, 'email': email})
        result = self.cursor.fetchone()
        if result and result[0] == 1:
            return True
        else:
            return False

    def is_player_id_unique(self, player_id):
        query = f"\
            SELECT COUNT(1)\
              FROM {self.tbl_user} t\
             WHERE t.player_id=%(player_id)s"
        self.cursor.execute(query, {'player_id': player_id})
        if self.cursor.fetchone()[0] > 0:
            return False
        else:
            return True

    def set_signupinfo(self, player_id, email, password):
        values = (player_id, email, password)
        self.cursor.execute("INSERT INTO tbl_user (player_id, email, password) VALUES (%s, %s, %s)", values)
        self.db.commit()

    def verify_account(self, email):
        query = f"\
            UPDATE {self.tbl_user}\
               SET verified=TRUE\
             WHERE email=%(email)s"
        try:
            self.cursor.execute(query, {'email': email})
            self.db.commit()
        except:
            self.db.rollback()
            return False
        return True

    def set_totp_key(self, email):
        totpkey = pyotp.random_base32()

        query = f"\
            UPDATE {self.tbl_user}\
               SET mfa_key=%(totpkey)s\
             WHERE email=%(email)s"
        try:
            # TODO: Hash the totpkey before storing in db with a 2-way hash
            self.cursor.execute(query, {'totpkey': totpkey, 'email': email})
            self.db.commit()
        except:
            self.db.rollback()
            return False
        return totpkey

    def check_login_info(self, player_id, password, totp, message):
        message.success = False
        if self.is_account_verified(player_id):
            # check if cooldown, execute below, else say that it is in cooldown
            if not self.in_cooldown(player_id):
                # reset counter if time and then and update timestamp to now
                self.update_counter(player_id, 'ifcooldownended')

                query = f"\
                    SELECT mfa_key\
                    FROM {self.tbl_user}\
                    WHERE player_id=%(player_id)s AND password=%(password)s"
                try:
                    self.cursor.execute(query, {'player_id': player_id, 'password': password})
                except: #db error
                    message.status = message.ErrorCode.otherfailures
                    return message

                result = self.cursor.fetchone()
                if result:
                    totp_checker = pyotp.TOTP(str(result[0]))
                    if totp_checker.verify(totp):
                        # reset counter = 0
                        self.update_counter(player_id, 'loginsuccessful')
                        message.success = True
                        message.status = message.ErrorCode.good
                    else:
                        # counter++
                        self.counterpp(player_id)
                        message.status = message.ErrorCode.badinput
                else:
                    # counter++
                    self.counterpp(player_id)
                    message.status = message.ErrorCode.badinput
            else:
                message.status = message.ErrorCode.incooldown
        else:
            message.status = message.ErrorCode.notverified
        self.update_timestamp(player_id)
        return message

    # reset counter to 0 if timestampdiff >= 5
    # reset counter to 0 after successful login
    def update_counter(self, player_id, case):
        query = ''
        if case == 'ifcooldownended':
            query = f"\
                UPDATE {self.tbl_user}\
                SET counter=0\
                WHERE player_id=%(player_id)s AND (TIMESTAMPDIFF(MINUTE, timestamp, LOCALTIME())>=5)"
        elif case == 'loginsuccessful':
            query = f"\
                UPDATE {self.tbl_user}\
                SET counter=0\
                WHERE player_id=%(player_id)s"
        try:
            self.cursor.execute(query, {'player_id': player_id})
            self.db.commit()
        except:
            self.db.rollback()

    # reset timestamp to now
    def update_timestamp(self, player_id):
        query_update_timestamp = f"\
            UPDATE {self.tbl_user}\
               SET timestamp=LOCALTIME()\
             WHERE player_id=%(player_id)s"
        try:
            self.cursor.execute(query_update_timestamp, {'player_id': player_id})
            self.db.commit()
        except:
            self.db.rollback()

    # increment failed login attempts counter and update timestamp
    def counterpp(self, player_id):
        query = f"\
            UPDATE {self.tbl_user}\
               SET counter=counter+1\
             WHERE player_id=%(player_id)s"
        try:
            self.cursor.execute(query, {'player_id': player_id})
            self.db.commit()
        except:
            self.db.rollback()

    # check if player is still in a cooldown
    def in_cooldown(self, player_id):
        query = f"\
            SELECT COUNT(1)\
              FROM {self.tbl_user}\
             WHERE player_id=%(player_id)s AND (counter<5 OR TIMESTAMPDIFF(MINUTE, timestamp, LOCALTIME())>5)"
        self.cursor.execute(query, {'player_id': player_id,})
        result = self.cursor.fetchone()

        if result and result[0]==1:
            return False
        else:
            return True
