from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import AES
import time
import os
def speed_comp():
    aes_start = time.time()
    
    aes_key = os.urandom(16)
    aes_encryptor = AES.new(aes_key,AES.MODE_EAX)
    aes_mid = time.time() - aes_start
    nonce = aes_encryptor.nonce
    aes_output,tag = aes_encryptor.encrypt_and_digest(b'they come at dawn')
    aes_done = round(time.time() - aes_start,3) * 1000
    print("AES complete in "+ str(aes_done)+" milliseconds")

    
    rsa_start = time.time()
    rand = Random.new().read
    rsa_key = RSA.generate(2048,rand)
    rsa_mid = time.time()
    rsa_gen = rsa_mid - rsa_start
    rsa_pub = rsa_key.publickey()
    rsa_encryptor = PKCS1_OAEP.new(rsa_pub)
    rsa_cipher = rsa_encryptor.encrypt(b'they come at dawn')
    rsa_done = round(time.time() - rsa_start,3)* 1000
    print("RSA encryption complete in "+str(rsa_done)+" milliseconds")


def run():
    for i in range(0,10):
        speed_comp()
