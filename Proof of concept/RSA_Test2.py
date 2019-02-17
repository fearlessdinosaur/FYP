import rsa
import time

def enc():
    
    start = time.time()

    (pub,priv) = rsa.newkeys(2048,poolsize=2)

    end = time.time()
    print("runtime:"+str(end - start))
    return(end-start)

def run():
    total = 0
    for i in range(0,10):
        f = enc()
        total = total + f

    print("avg:" + str(total/10))
