import sys
import random
import os
from flask import redirect
from dotenv import load_dotenv

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def rand_id(length = 8, allow_spec_chars=True):
    spec_chars = '# @ % $ & * ( ) ! ~ ` , ; : > < / ? | + = - _'
    allowed = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    ASCII_UPPERCASE_START = 65
    ASCII_UPPERCASE_END_EXC = 91
    ASCII_LOWERCASE_START = 97
    ASCII_LOWERCASE_END_EXC = 123
    allowed.extend([chr(i) for i in range(ASCII_UPPERCASE_START, ASCII_UPPERCASE_END_EXC)])
    allowed.extend([chr(i) for i in range(ASCII_LOWERCASE_START, ASCII_LOWERCASE_END_EXC)])
    if allow_spec_chars:
        allowed.extend(spec_chars.split(' '))
    r_id = ''
    for _ in range(0, length):
        # System random is more cryptographically secure than simply random.random()
        rand_i = random.SystemRandom().randint(0, len(allowed)-1)
        r_id = r_id + allowed[rand_i]
    assert len(r_id) == length
    return r_id

def player_in_game(player_id, game_sessions, game_id):
    return game_id in game_sessions and game_sessions[game_id][1].has_player(player_id)

def player_owns_game(player_id, game_sessions, game_id=None):
    for owner_game_tuple in game_sessions.values():
        if owner_game_tuple[0] == player_id:
            if game_id == None:
                return True
            elif game_id in game_sessions:
                return True
    return False

def player_with_key(players, key):
    if (players and key in players):
        return players[key]
    return None

def authd(supplied_player_id, supplied_session_key, authoritative_player_ids, authoritative_session_key):
    return (authoritative_session_key == supplied_session_key and player_with_key(authoritative_player_ids, supplied_session_key) == supplied_player_id)

PROTO='HTTP://'
DOMAIN=os.getenv('DOMAIN')

# Param: uri: should be in the form '/uri_path' NOT in the form 'uri_path
# Param: proto: should be a valid protocol identifier i.e. http:// or ftp://
def redirect_ext_url(uri, proto=PROTO):
    if DOMAIN is None:
        raise ValueError
    return redirect(PROTO+DOMAIN+uri)

def load_env_safe(path):
    if os.path.isfile(path):
        load_dotenv(dotenv_path=path)
    else:
        eprint('-----DIAGNOSTICS-----')
        eprint('The current scripts are being executed from: ')
        eprint(os.getcwd())
        raise FileNotFoundError('.env file was not found, and so environment variables cannot be loaded')