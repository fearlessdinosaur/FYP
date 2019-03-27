import re 
def stripping(data):
    l = re.findall("^{.+?}|{.+?{.+?}}",data)
    for x in l:
        print(x)
