import asyncio
class Server:
    
    async def make_uplink(self,reader,writer):
        print("connected")
        writer.write(b"please enter username")
        Uname = await Server.get_user(reader,writer,self)
        #if Uname is not None:
            #writer.write("welcome "+Uname)
            #yield self.chat(reader,writer,Uname)
            
    #async def chat(reader,writer,Uname):
        #while True:
            #data = (yield reader.read()).decode()
            #print(data)
            
    async def get_user(reader,writer,self):
        print("in this function now")
        user = reader.read(1024).decode()
        print(user)
        return(user)
    
    def __init__(self):
        clients = {}
        port = 1661
        self.loop = asyncio.get_event_loop()
        self.serv = asyncio.start_server(self.make_uplink,'127.0.0.1',port,loop=self.loop)
        self.server = self.loop.run_until_complete(self.serv)
        self.loop.run_forever()
        
Server()
