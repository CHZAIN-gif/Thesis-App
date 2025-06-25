import bcrypt

def hash_password(password):
    """
    Hashes a given password using bcrypt.
    """
    # First, we need to convert the password string into bytes
    password_bytes = password.encode('utf-8')

    # Then, we generate a "salt", which is a random value to make each hash unique
    salt = bcrypt.gensalt()

    # Now, we create the secure hash
    hashed_password = bcrypt.hashpw(password_bytes, salt)

    # We return the hash as a string so we can store it in our database
    return hashed_password.decode('utf-8')

def verify_password(plain_password, hashed_password):
    """
    Checks if a plain password matches a stored hashed password.
    """
    plain_password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    
    # bcrypt's checkpw function does all the hard work for us
    return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)