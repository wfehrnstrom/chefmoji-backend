from itsdangerous import URLSafeTimedSerializer

def generate_confirmation_token(email, key, saltkey):
    serializer = URLSafeTimedSerializer(key)
    return serializer.dumps(email, salt=saltkey)