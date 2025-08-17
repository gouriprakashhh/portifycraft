# yourapp/utils.py
import random
import string

def generate_unique_username(user):
    base = user.email.split('@')[0]  # Take the part before '@' from email
    suffix = ''.join(random.choices(string.digits, k=4))  # Add random digits
    return f"{base}_{suffix}"  # E.g., john_1234
