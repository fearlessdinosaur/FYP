import asyncio
clients = []
class Server:
    
    async def uplink(reader,writer,):
        print("uplink established")
        clients.append(writer)
        print(clients)
        while True:
            data = await reader.read(100)
            msg = data.decode()
            print(msg)
            for client in clients:
                print(client.get_extra_info('peername'))
                client.write(data)
        
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.serv = asyncio.start_server(Server.uplink,'127.0.0.1',1661,loop=self.loop)
        self.server = self.loop.run_until_complete(self.serv)
        self.loop.run_forever()
        
Server()
