from curio import run,spawn,tcp_server
import json
class Server:
    
    async def make_uplink(self,client,addr):
        print("new connection from "+str(addr))
        js = json.dumps({"code":0,"Message":"please Enter username"})
        await client.send(js.encode())
        while True:
            Uname = await Server.assign_user(client,addr,self)
            if Uname is not None:
                js = json.dumps({"code":0,"Message":"welcome "+Uname+",you may now start chatting"})
                await client.send(js.encode())
                await Server.chat(client,addr,Uname,self)
            else:
               js = json.dumps({"code":0,"Message":"sorry username is taken"})
               await client.send(js.encode()) 
        
            
    async def chat(client,addr,Uname,self):
        while True:
            data = await client.recv(1024)
            print(data.decode())
            js = json.loads(data.decode())
            if( js["code"] == 1):
                for c in self.clients:
                    await Server.broadcast(self.clients[c],addr,Uname,js["Message"])
            
            
    async def assign_user(client,addr,self):
        message = await client.recv(1024)
        js = json.loads(message.decode())
        username = js["Message"]
        if(username not in self.clients):    
            print(username)
            self.clients[username] = client
            return(username)

    async def broadcast(client,addr,Uname,message):
        js = json.dumps({"code":1,"Message":Uname + ":" + message})
        await client.send(js.encode())
        
    
    def __init__(self):
        self.clients = {}
        port = 1661
        run(tcp_server,'',port,self.make_uplink)
        
Server()
