import random
from django.core.cache import cache

OTP_EXPIRY = 300  # 5 minutes

def generate_otp():
    return str(random.randint(100000, 999999))


def store_otp(email, otp):
    cache.set(f"otp:{email}", otp, timeout=OTP_EXPIRY)


def get_otp(email):
    return cache.get(f"otp:{email}")


def delete_otp(email):
    cache.delete(f"otp:{email}")


def set_resend_lock(email):
    cache.set(f"resend_lock:{email}", True, timeout=30)


def can_resend(email):
    return cache.get(f"resend_lock:{email}") is None