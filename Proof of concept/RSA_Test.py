import Crypto
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto import Random
import time
import base64

def encryption(x):
    tot = 0
    for i in range(0,10):
        start = time.time()
        rand = Random.new().read
        key = RSA.generate(2048,rand)
        mid = time.time()
        print("key gen time:"+str(mid - start)+" seconds")
        pub = key.publickey()
        encryptor = PKCS1_OAEP.new(pub)
        decryptor = PKCS1_OAEP.new(key)
        cipher = encryptor.encrypt(x.encode())
        base = base64.b64encode(cipher)
        text = decryptor.decrypt(base64.b64decode(base))
        print(text)
        end = time.time()
        print("encryption time:"+str(end - mid)+ " seconds")
        tot = tot+(mid - start)

    print("avg = "+str(tot/10))
