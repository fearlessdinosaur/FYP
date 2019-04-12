import time
import sys
import os
import random
def scrub_file(file,times):
    alf = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    start = time.time()
    st = os.stat(file)
    size = st.st_size
    for a in range(0,times):
        p = open(file,"w")
        for b in range(0,size):
            p.write(alf[random.randint(0,25)])
        p.close()
    end = time.time() - start
    print(str(times)+" rounds took "+ str(round(end,1))+" seconds to complete")
    os.remove(file)
def run():
    scrub_file("testfile.txt",10)

