import sympy
import random
from math import gcd

def generate_coprime_with_p(p):
    while True:
        s = random.randint(2, p - 1)
        print(s)
        if gcd(s, p) == 1:
            return s

def get_g_p():
    p = sympy.randprime(10 ** 15, 10 ** 16)
    g = generate_coprime_with_p(p)
    return p, g

def secret_key_client():
    return random.randint(10 ** 15, 10 ** 16 - 1)


def secret_key_server():
    return random.randint(10 ** 15, 10 ** 16 - 1)



