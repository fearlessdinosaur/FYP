import asyncio

class Server:
    
    async def uplink(reader,writer):
        print("uplink established")
        data = await reader.read(100)
        msg = data.decode()
        print(msg)

        writer.write(data)
        
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.serv = asyncio.start_server(Server.uplink,'127.0.0.1',8888,loop=self.loop)
        self.server = self.loop.run_until_complete(self.serv)
        self.loop.run_forever()
        
Server()
