import time
import sys
import os
import random
def scrub_file(file):
    alf = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    start = time.time()
    st = os.stat(file)
    print(st.st_size)
    size = st.st_size
    for a in range(0,10):
        p = open(file,"w")
        for b in range(0,size):
            p.write(alf[random.randint(0,25)])
        p.close()
    end = time.time() - start
    print("took "+ str(round(end,1))+" seconds to complete")
