import rsa
import time


import Crypto
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto import Random
import base64

def enc_PyRSA():
    
    start = time.time()

    (pub,priv) = rsa.newkeys(2048,poolsize=2)

    end = time.time()
    print("runtime:"+str(end - start))
    return(end-start)

def enc_Pycryptodome():
    start = time.time()
    rand = Random.new().read
    key = RSA.generate(2048,rand)
    mid = time.time()
    print("key gen time:"+str(mid - start)+" seconds")
    return(mid-start)


def run():
    total = 0
    print("---- pyRSA ----")
    for i in range(0,10):
        f = enc_PyRSA()
        total = total + f

    print("pyRSA avg:" + str(total/10))
    print("----Pycryptodome----")
    total = 0
    for i in range(0,10):
        f = enc_Pycryptodome()
        total = total + f

    print("pyCryptodome avg:" + str(total/10))

    
