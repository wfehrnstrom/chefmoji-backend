from itsdangerous import URLSafeTimedSerializer

def generate_confirmation_token(email, key, saltkey):
    serializer = URLSafeTimedSerializer(key)
    return serializer.dumps(email, salt=saltkey)

# token by default is valid for only 1 hour.
def confirm_token(token, key, saltkey, expiration=3600):
    serializer = URLSafeTimedSerializer(key)
    try:
        email = serializer.loads(
            token,
            salt=saltkey,
            max_age=expiration
        )
    except:
        raise Exception('Token provided is invalid or has expired')
    return email