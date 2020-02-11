import sys
import random
import os

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

def static_files_path():
    if os.environ['FLASK_ENV'] == 'development':
        if 'BUILD_INTO' in os.environ:
            return os.environ['BUILD_INTO']
        else:
            (head, _) = os.path.split(os.getcwd())
            return os.path.join(head, 'frontend', 'public')
    else:
        return 'static'

def player_in_game(player_id, game_sessions, game_id):
    return game_sessions and game_id in game_sessions and game_sessions[game_id].has_player(player_id)