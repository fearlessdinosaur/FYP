from curio import run,spawn,tcp_server
import simplejson as json
import Crypto
import os
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto import Random
from threading import Thread
import shutil
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import random

class Server:
    
    # based off accept connection code found at https://gist.github.com/Cartroo/063f0c03808e9622d33b41f140a63f6a
    async def make_uplink(self,client,addr):
        while True:
            try:
                Uname = await Server.assign_user(client,addr,self)
            except:
                print("this is what was going wrong")
            if Uname is not None:
                js = json.dumps({"code":7,"Message":"username available"})
                await client.send(js.encode())
                await Server.get_Key(client,Uname,addr,self)
                js = json.dumps({"code":7,"Message":"welcome "+Uname+",you may now start chatting"})
                await client.send(js.encode())
                itemlist = {}
                #generates member list for user and sends username to each member
                itemlist = await self.keyShare(Uname,"general")
                #sends list on to new user 
                js = json.dumps({"code":11,"Message":itemlist})
                await client.send(js.encode())
                await Server.chat(client,addr,Uname,self)
                break
            else:
                js = json.dumps({"code":7,"Message":"uname Taken"})
                await client.send(js.encode()) 
        
    # code to run the main chat loop which allows users to communicate with eachother         
    async def chat(client,addr,Uname,self):
        while True:
            try:
                # recieves data 
                data = await client.recv(2048)
                js = json.loads(data.decode())
                # runs functions based on code recieved
                if( js["code"] == 1):
                    await Server.broadcast(self.clients[js["reciever"]],addr,Uname,js["Message"],js["reciever"],self)
                if(js["code"] == 5):
                    await Server.MkGroup(client,addr,Uname,js["Message"],self)
                if(js["code"] == 2):
                    dropKey = json.dumps({"code":16,"Message":Uname})
                
                    for x in self.groupAssignment:
                        await x.send(dropKey.encode())                         
                    self.groupAssignment.pop(client)               
                    await client.close()
                if(js["code"] == 7):
                    await self.listGroup(client,addr,Uname)
                if(js["code"] == 9):
                    await self.SetGroup(client,addr,Uname,js["Message"])
                if(js["code"] == 11):
                    await self.SendMembers(client,addr,Uname,js["Message"])
                if(js["code"] == 14):
                    key = js["Message"]
                    print("download offer:"+key)
                    self.files[key] = 0
                    await self.OfferDownload(client,addr,Uname,js["Message"],js["sender"])  
                # file scrubber
                if(js["code"] == 15):
                    self.files[js["Message"]] = self.files[js["Message"]] - 1
                    # if 0 downloads left, run burn 
                    if(self.files[js["Message"]] <= 0):
                        # create alphabet array
                        alf = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
                        # check size of message using stat
                        st = os.stat(js["Message"])
                        size = st.st_size
                        #wait 5 seconds
                        time.sleep(5)
                        # runs loop 10 times
                        for a in range(0,10):
                            p = open(js["Message"],"w")
                            # replaces each byte with random character
                            for b in range(0,size):
                                p.write(alf[random.randint(0,25)])
                            p.close()
                        #deletes file
                        os.remove(js["Message"])   
                        
            # if exception occurs, shut down connection
            except Exception as e:
                print("exception:"+str(e))
                print("before:"+str(self.clients))
                
                if(Uname in self.clients):
                    self.clients.pop(Uname)
                print("After:"+str(self.clients))
                break
           
    #function to offer file to be downloaded to each user and count them         
    async def OfferDownload(self,client,addr,Uname,file,sender):
        # loops through group list
        for x in self.groupAssignment:
            # checks if groups are the same
            if(self.groupAssignment[x] == self.groupAssignment[client]):
                self.files[file] = self.files[file] + 1
                js = json.dumps({"code":13,"Message":file,"sender":sender})
                await x.send(js.encode())

    # assigns user their username if available            
    async def assign_user(client,addr,self):
        try:
            message = await client.recv(1024)
        except Exception as e:
            return 0
        js = json.loads(message.decode())
        username = js["Message"]
        # set username if free and set up basic user info
        if(username not in self.clients):    
            print("username:"+username)
            self.clients[username] = client
            self.groupAssignment[client] = "general"
            return(username)
    # ask user for key    
    async def get_Key(client,Uname,addr,self):
        key= await client.recv(1024)
        self.KeyTab[Uname] = RSA.importKey(key,passphrase=None)
        
    # passes messages between users
    async def broadcast(client,addr,Uname,message,reciever,self):
        js = json.dumps({"code":1,"Message":message,"sender":Uname,"reciever":reciever})
        print("sending message from "+Uname+" to "+reciever)
        try:
            await client.send(js.encode())
        except:
            print("something is wrong")
    
    # sends group list to users        
    async def listGroup(self,client,addr,Uname):
        js = json.dumps({"code":8,"Message":self.groups})
        await client.send(js.encode())
    
    # group creation    
    async def MkGroup(client,addr,Uname,group,self):
        #create group if group is free
        if group not in self.groups:
            # creates new group
            self.groups.append(group)
            oldGroup = self.groupAssignment[client]
            self.groupAssignment[client] = group
            js = json.dumps({"code":11,"Message":await self.keyShare(Uname,group)})
            await client.send(js.encode())
            jsConf= json.dumps({"code":7,"Message":"group creation successful"})
            jsAssign = json.dumps({"code":5,"Message":group})
            # create new group directory
            os.mkdir("Files/"+group)
            await client.send(jsConf.encode())
            await client.send(jsAssign.encode())
            j = 0
            # builds drop key message
            dropKey = json.dumps({"code":16,"Message":uname})
            for x in self.groupAssignment:
                # tells all old group members to drop users key
                if(self.groupAssignment[x] == oldGroup):
                    j = j+1
                    await x.send(dropKey.encode())   
            # if < 1 person in old group, delete old group from list
            if(j < 1 and oldGroup != "general"):
                self.groups.remove(oldGroup)
                try:
                    shutil.rmtree(oldGroup)
                except OSError as e:
                    print("ERROR: %s - %s"%(e.filename,e.strerror))
        #else join group
        else:
            self.SetGroup(client,addr,Uname,group)
            
    #group join        
    async def SetGroup(self,client,addr,uname,group):
        if group in self.groups:
            old = self.groupAssignment[client]
            self.groupAssignment[client] = group
            js = json.dumps({"code":11,"Message":await self.keyShare(uname,group)})
            jsAssign = json.dumps({"code":5,"Message":group})
            
            dropKey = json.dumps({"code":16,"Message":uname})
            await client.send(jsAssign.encode())
            await client.send(js.encode())
            for x in self.groupAssignment:
                if self.groupAssignment[x] == old:
                    await x.send(dropKey.encode())
    # runs standard ftp server setup        
    def ftp_setup():
        aut = DummyAuthorizer()
        aut.add_user("user","pass","Files",perm="elradfmw")
        aut.add_anonymous("Files",perm="elradfmw")
        
        handler = FTPHandler
        handler.authorizer = aut
        
        server = FTPServer(("127.0.0.1", 1026), handler)
        server.serve_forever()        
     
    # runs key share       
    async def keyShare(self,uname,group):
        itemlist = {}
        
        # for everyone in all groups
        for x in self.groupAssignment:
                    # if both in same group
                    if self.groupAssignment[x] == group:
                        # gets group members key
                        for key,value in self.clients.items():
                            if value == x:
                                # if key is not users key 
                                if key != uname:
                                    # send users public key to group member
                                    userData = json.dumps({"code":12,"Message":self.KeyTab[uname].exportKey(format = "PEM",passphrase=None,pkcs=1),"user":uname})
                                    await x.send(userData.encode())
                                # add member key to key list
                                itemlist[key] = self.KeyTab[key].exportKey(format = "PEM",passphrase=None,pkcs=1)                    
        return(itemlist)
    # function to complete initial set up
    def __init__(self):
        self.clients = {}
        self.files = {}
        self.groups = ["general"]
        self.groupAssignment = {}
        self.KeyTab = {}
        port = 1661
        Thread(target=Server.ftp_setup).start()
        run(tcp_server,'',port,self.make_uplink)

if __name__ == "__main__":
    Server()
