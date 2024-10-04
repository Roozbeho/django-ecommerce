import random


def create_random_code():
    """
    Create random 6 digit number as Otp_code
    """
    return str(random.randint(100000, 999999))
