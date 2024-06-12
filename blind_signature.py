from Crypto.PublicKey import RSA
from Crypto.Util.number import getPrime, inverse
from hashlib import sha512
import random
import math
import sympy

# Generate RSA key pair(public key, private key, n)
def gen_key():
    keyPair = RSA.generate(bits=1024)
    return hex(keyPair.e), hex(keyPair.d), hex(keyPair.n)

# Hash function
def hash_func(text):
    hash = int.from_bytes(sha512(text).digest(), byteorder='big')
    return hash

# Blind message with bank public key
def blind_msg(message, public_key, n):
    e = int(public_key, 16)
    mod = int(n, 16)
    hash_msg = hash_func(message)
    while True:
        r = random.randint(2, mod-1)
        if math.gcd(r, mod) == 1:
            break
        
    r_e = pow(r, e, mod)
    r_inv = int(sympy.mod_inverse(r, mod))
    blinded_message = (hash_msg * r_e) % mod
    return blinded_message, r, r_inv

# Bank use private key to sign the blinded message
def sign_blinded_msg(blinded_message, private_key, mod):
    signature = pow(blinded_message, private_key, mod)
    return signature   
 
# payer unblind signature use blind factor
def unblind_signature(blinded_signature, blind_factor, mod):
    blind_factor = int(blind_factor)
    unblinded_signature = (blind_factor * blinded_signature) % mod
    return unblinded_signature

# Verify signature
def verify_signature(message, signature, public_key, n):
    public_key = int(public_key, 16)
    n = int(n, 16)
    ver_sign = pow(signature, public_key, n)
    print(ver_sign)
    if hash_func(message) == ver_sign:
        return True
    else:
        return False
