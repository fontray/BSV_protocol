from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
import os

# Generate blind factor 'b' 
def gne_blindfactior(public_k):
    n = public_k.n
    blind_factor = int.from_bytes(os.urandom(128), byteorder='big') % n
    if blind_factor > 1 and blind_factor < n and pow(blind_factor, public_k.e, n) != 0:
        return blind_factor

# Generate random number 'r'
def gen_random(bit, mod):
    r = int.from_bytes(os.urandom(bit), byteorder='big') % mod
    return r

# Hash message using SHA256 and convert to integer
def hash_message(message):
    digest = SHA256.new()
    digest.update(message.encode('utf-8'))
    return int.from_bytes(digest.digest(), byteorder='big')


# Blind message
def blinding(message, random, blind_factor, public_k):
    message_int = hash_message(message)
    n = public_k.n
    e = public_k.e
    blinded = (message_int * pow(blind_factor, e, n)) % n
    blinded_r = (random * pow(blind_factor, e, n)) % n
    return blinded, blinded_r

# Sign blinded message with private key
def sign(blinded, private_k, mod):
    signature = pow(blinded, private_k.d, mod)
    return signature

# Unblind signature s' 
def unblind(blind_sign, blind_factor, public_k):
    n = public_k.n
    inv_b = pow(blind_factor, -1, n)
    unblind_sign = (blind_sign * inv_b) % n
    return unblind_sign

# Verify the signature
def verify(signature, message, public_k):
    message_int = hash_message(message)
    
    if(message_int == pow(signature, public_k.e, public_k.n)):
        return True
    else:
        return False

# Generate private key sK and public key pK
random_gen = Random.new().read
rsa = RSA.generate(2048, random_gen)  # Use 2048 bits for better security
private_key = rsa.exportKey()
public_key = rsa.publickey().exportKey()

with open("private_rsa",'wb') as f:
    f.write(private_key)

with open("public_rsa",'wb') as f:
    f.write(public_key)    


# print("Private key:", private_key.decode('utf-8'))
# print("Public key:", public_key.decode('utf-8'))

# # Load keys from memory
# sK = RSA.importKey(private_key)
# pK = RSA.importKey(public_key)
# n = pK.n

# b = gne_blindfactior(pK) # blind factor
# r = gen_random(32, n) # voter random number

# print(f"Blind factor 'b' is :{b}")
# print(f"Rnadom number 'r' is :{r}")

# m = "yes"

# blind_msg, blind_r  = blinding(m, r, b, pK)

# print(f"The blind ballot (m,r)':({blind_msg}, {blind_r})")

# # Government sign the blind ballot
# blind_msg_sign = sign(blind_msg, sK, n)
# blind_r_sign = sign(blind_r, sK, n)

# print(f"The government sign ballot s': ({blind_msg_sign}, {blind_r_sign})")

# # Voter unblind the signature
# unblind_msg = unblind(blind_msg_sign, b, pK)
# unblind_r = unblind(blind_r_sign, b, pK)

# print(f"The ballot with government sign s :({unblind_msg}, {unblind_r})")

# # Verify the signature
# is_valid = verify(unblind_msg, m, pK)

# print(f"Is the signature valid? {is_valid}")
