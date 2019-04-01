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

class Server:
    
    # based off accept connection code found at https://gist.github.com/Cartroo/063f0c03808e9622d33b41f140a63f6a
    async def make_uplink(self,client,addr):
        print("new connection from "+str(addr))
        js = json.dumps({"code":7,"Message":"please Enter username"})
        await client.send(js.encode())
        while True:
            Uname = await Server.assign_user(client,addr,self)
            if Uname is not None:
                await Server.get_Key(client,Uname,addr,self)
                js = json.dumps({"code":7,"Message":"welcome "+Uname+",you may now start chatting"})
                print(js)
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
                js = json.dumps({"code":7,"Message":"sorry username is taken"})
                await client.send(js.encode()) 
        
    # based off accept handle connection code found at https://gist.github.com/Cartroo/063f0c03808e9622d33b41f140a63f6a           
    async def chat(client,addr,Uname,self):
        while True:
            try:
                data = await client.recv(2048)
                js = json.loads(data.decode())
                if( js["code"] == 1):
                            await Server.broadcast(self.clients[js["reciever"]],addr,Uname,js["Message"],js["reciever"],self)
                if(js["code"] == 5):
                    await Server.MkGroup(client,addr,Uname,js["Message"],self)
                if(js["code"] == 2):
                    self.clients.pop(Uname)
                    self.groupAssignment.pop(client)
                    client.close()
                    print(self.clients)
                if(js["code"] == 7):
                    await self.listGroup(client,addr,Uname)
                if(js["code"] == 9):
                    await self.SetGroup(client,addr,Uname,js["Message"])
                if(js["code"] == 11):
                    await self.SendMembers(client,addr,Uname,js["Message"])
                if(js["code"] == 14):
                    key = js["Message"]
                    print(key)
                    self.files[key] = 0
                    await self.OfferDownload(client,addr,Uname,js["Message"],js["sender"])      
                if(js["code"] == 15):
                    self.files[js["Message"]] = self.files[js["Message"]] - 1
                    if(self.files[js["Message"]] <= 0):
                        alf = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
                        st = os.stat(js["Message"])
                        size = st.st_size
                        for a in range(0,10):
                            p = open(js["Message"],"w")
                            for b in range(0,size):
                                p.write(alf[random.randint(0,25)])
                            p.close()
                        os.remove(js["Message"])                
            except Exception as e:
                print(e)
                print("before:"+str(self.clients))
                
                if(Uname in self.clients):
                    self.clients.pop(Uname)
                print("After:"+str(self.clients))
                break
           
    # based off accept user assignment code found at https://gist.github.com/Cartroo/063f0c03808e9622d33b41f140a63f6a      
    
    async def OfferDownload(self,client,addr,Uname,file,sender):
        for x in self.groupAssignment:
            if(self.groupAssignment[x] == self.groupAssignment[client]):
                self.files[file] = self.files[file] + 1
                js = json.dumps({"code":13,"Message":file,"sender":sender})
                await x.send(js.encode())
                
    async def assign_user(client,addr,self):
        try:
            message = await client.recv(1024)
        except Exception as e:
            return 0
        js = json.loads(message.decode())
        username = js["Message"]
        if(username not in self.clients):    
            print(username)
            self.clients[username] = client
            self.groupAssignment[client] = "general"
            return(username)
        
    async def get_Key(client,Uname,addr,self):
        key= await client.recv(1024)
        self.KeyTab[Uname] = RSA.importKey(key,passphrase=None)
        
    async def broadcast(client,addr,Uname,message,reciever,self):
        js = json.dumps({"code":1,"Message":message,"sender":Uname,"reciever":reciever})
        print("sending message from "+Uname+" to "+reciever)
        await client.send(js.encode())

    async def listGroup(self,client,addr,Uname):
        js = json.dumps({"code":8,"Message":self.groups})
        await client.send(js.encode())
        
    async def MkGroup(client,addr,Uname,group,self):
        if group not in self.groups:
            self.groups.append(group)
            oldGroup = self.groupAssignment[client]
            self.groupAssignment[client] = group
            js = json.dumps({"code":11,"Message":await self.keyShare(Uname,group)})
            await client.send(js.encode())
            jsConf= json.dumps({"code":7,"Message":"group creation successful"})
            jsAssign = json.dumps({"code":5,"Message":group})
            os.mkdir("Files/"+group)
            await client.send(jsConf.encode())
            await client.send(jsAssign.encode())
            j = 0
            for x in self.groupAssignment:
                if(self.groupAssignment[x] == oldGroup):
                    j = j+1
            if(j < 1):
                self.groups.remove(oldGroup)
                try:
                    shutil.rmtree(oldGroup)
                except OSError as e:
                    print("ERROR: %s - %s"%(e.filename,e.strerror))
            
    async def SetGroup(self,client,addr,uname,group):
        if group in self.groups:
            self.groupAssignment[client] = group
            js = json.dumps({"code":11,"Message":await self.keyShare(uname,group)})
            jsAssign = json.dumps({"code":5,"Message":group})
            await client.send(jsAssign.encode())
            await client.send(js.encode())
            
    def ftp_setup():
        aut = DummyAuthorizer()
        aut.add_user("user","pass","Files",perm="elradfmw")
        aut.add_anonymous("Files",perm="elradfmw")
        
        handler = FTPHandler
        handler.authorizer = aut
        
        server = FTPServer(("127.0.0.1", 1026), handler)
        server.serve_forever()        
            
    async def keyShare(self,uname,group):
        print("running keyshare....")
        itemlist = {}
        for x in self.groupAssignment:
                    if self.groupAssignment[x] == group:
                        for key,value in self.clients.items():
                            if value == x:
                                print(key)
                                if key != uname:
                                    userData = json.dumps({"code":12,"Message":self.KeyTab[Uname].exportKey(format = "PEM",passphrase=None,pkcs=1),"user":Uname})
                                    print(userData)
                                    await x.send(userData.encode())
                                itemlist[key] = self.KeyTab[key].exportKey(format = "PEM",passphrase=None,pkcs=1)
        print("keyshare complete")                        
        return(itemlist)
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
