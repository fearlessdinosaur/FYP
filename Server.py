from curio import run,spawn,tcp_server
import json
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
class Server:
    # based off accept connection code found at https://gist.github.com/Cartroo/063f0c03808e9622d33b41f140a63f6a
    async def make_uplink(self,client,addr):
        print("new connection from "+str(addr))
        js = json.dumps({"code":7,"Message":"please Enter username"})
        await client.send(js.encode())
        while True:
            Uname = await Server.assign_user(client,addr,self)
            if Uname is not None:
                js = json.dumps({"code":7,"Message":"welcome "+Uname+",you may now start chatting"})
                await client.send(js.encode())
                js = json.dumps({"code":10,"Message":self.key.decode("utf-8")})
                await client.send(js.encode())
                await Server.chat(client,addr,Uname,self)
            else:
               js = json.dumps({"code":7,"Message":"sorry username is taken"})
               await client.send(js.encode()) 
        
    # based off accept handle connection code found at https://gist.github.com/Cartroo/063f0c03808e9622d33b41f140a63f6a           
    async def chat(client,addr,Uname,self):
        while True:
            data = await client.recv(1024)
            print(data.decode())
            js = json.loads(data.decode())
            if( js["code"] == 1):
                for c in self.clients:
                    if(self.groupAssignment[self.clients[c]] == self.groupAssignment[client]):
                        await Server.broadcast(self.clients[c],addr,Uname,js["Message"])
            if(js["code"] == 5):
                await Server.MkGroup(client,addr,Uname,js["Message"],self)
            if(js["code"] == 2):
                self.clients.pop(Uname)
                print(self.clients)
            if(js["code"] == 7):
                await self.listGroup(client,addr,Uname)
            if(js["code"] == 9):
                await self.SetGroup(client,addr,Uname,js["Message"])
                
            
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
    
    async def broadcast(client,addr,Uname,message):
        js = json.dumps({"code":1,"Message":Uname + ":" + message})
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
        self.key = get_random_bytes(16)
        print(self.key)
        self.clients = {}
        self.groups = ["general"]
        self.groupAssignment = {}
        port = 1661
        run(tcp_server,'',port,self.make_uplink)
        
Server()
