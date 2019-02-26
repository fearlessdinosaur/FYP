from curio import run,spawn,tcp_server
import simplejson as json
import Crypto
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto import Random
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
                await client.send(js.encode())
                itemlist = {}
                #generates member list for user and sends username to each member
                for x in self.groupAssignment:
                    if self.groupAssignment[x] == "general":
                        for key,value in self.clients.items():
                            if value == x:
                                if key != Uname:
                                    userData = json.dumps({"code":12,"Message":self.KeyTab[Uname].exportKey(format = "PEM",passphrase=None,pkcs=1),"user":Uname})
                                    print(userData)
                                    await x.send(userData.encode())
                                itemlist[key] = self.KeyTab[key].exportKey(format = "PEM",passphrase=None,pkcs=1)
                #sends list on to new user 
                js = json.dumps({"code":11,"Message":itemlist})
                await client.send(js.encode())
                await Server.chat(client,addr,Uname,self)
            else:
               js = json.dumps({"code":7,"Message":"sorry username is taken"})
               await client.send(js.encode()) 
        
    # based off accept handle connection code found at https://gist.github.com/Cartroo/063f0c03808e9622d33b41f140a63f6a           
    async def chat(client,addr,Uname,self):
        while True:
            data = await client.recv(1024)
            js = json.loads(data.decode())
            if( js["code"] == 1):
                        await Server.broadcast(self.clients[js["reciever"]],addr,Uname,js["Message"],js["reciever"],self)
            if(js["code"] == 5):
                await Server.MkGroup(client,addr,Uname,js["Message"],self)
            if(js["code"] == 2):
                self.clients.pop(Uname)
                print(self.clients)
            if(js["code"] == 7):
                await self.listGroup(client,addr,Uname)
            if(js["code"] == 9):
                await self.SetGroup(client,addr,Uname,js["Message"])
            if(js["code"] == 11):
                await self.SendMembers(client,addr,Uname,js["Message"])
                
            
    # based off accept user assignment code found at https://gist.github.com/Cartroo/063f0c03808e9622d33b41f140a63f6a        
    async def assign_user(client,addr,self):
        message = await client.recv(1024)
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
            self.groupAssignment[client] = group
            jsConf= json.dumps({"code":1,"Message":"group creation successful"})
            jsAssign = json.dumps({"code":5,"Message":group})
            await client.send(jsConf.encode())
            await client.send(jsAssign.encode())

    async def SetGroup(self,client,addr,uname,group):
        if group in self.groups:
            self.groupAssignment[client] = group
            jsAssign = json.dumps({"code":5,"Message":group})
            await client.send(jsAssign.encode())
            
    def __init__(self):
        self.clients = {}
        self.groups = ["general"]
        self.groupAssignment = {}
        self.KeyTab = {}
        port = 1661
        run(tcp_server,'',port,self.make_uplink)

if __name__ == "__main__":
    Server()
