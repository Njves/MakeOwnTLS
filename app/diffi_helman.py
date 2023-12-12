import os
from base64 import b64encode, b64decode

import sympy
import random
from math import gcd

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, modes
from cryptography.hazmat.primitives.ciphers.algorithms import AES


def generate_coprime_with_p(p):
    while True:
        s = random.randint(2, p - 1)
        print(s)
        if gcd(s, p) == 1:
            return s


def get_g_p():
    p = sympy.randprime(10 ** 15, 10 ** 16)
    g = generate_coprime_with_p(p)
    return g, p


def secret_key_client():
    return random.randint(10 ** 15, 10 ** 16 - 1)


def get_shared_server_key(A, b, p):
    return pow(A, b, p)

def get_shared_client_key(g, b, p):
    return pow(g, b, p)


def secret_key_server():
    return random.randint(10 ** 15, 10 ** 16 - 1)


def hash_key(secret_key):
    secret_key = str(secret_key)
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(secret_key.encode())
    return digest.finalize()


def encrypt(text, key):
    # Convert the text to bytes
    data = text.encode()

    # Generate a random initialization vector (IV)
    iv = os.urandom(12)

    # Create a new AES-GCM cipher using the key
    cipher = Cipher(AES(key), modes.GCM(iv),
                    backend=default_backend())
    encryptor = cipher.encryptor()

    # Encrypt the data
    encrypted_data = encryptor.update(data) + encryptor.finalize()

    # Append the tag to the encrypted data
    encrypted_data_with_tag = encrypted_data + encryptor.tag

    # Convert the encrypted data with tag and IV to Base64 strings
    encrypted_data_with_tag_str = b64encode(encrypted_data_with_tag).decode()
    iv_str = b64encode(iv).decode()

    return encrypted_data_with_tag_str, iv_str


def decrypt(encrypted_text, key, iv):
    iv = b64decode(iv)
    # Decode the Base64 string back into bytes
    encrypted_data_with_tag = b64decode(encrypted_text)

    # Separate the encrypted data and the tag
    encrypted_data = encrypted_data_with_tag[:-16]
    tag = encrypted_data_with_tag[-16:]
    decoded = ""
    # Create a new AES-GCM cipher for decryption
    try:
        cipher = Cipher(AES(key), modes.GCM(iv, tag),
                        backend=default_backend())
        decryptor = cipher.decryptor()
        # Decrypt the data
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        decoded = decrypted_data.decode()
    except InvalidTag:
        print("Impossible to decrypt")
    return decoded
