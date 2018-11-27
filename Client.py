import asyncio
class client:
    
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(client.setup(self.loop,))

    async def setup(loop):
        print("connection established")
        reader,writer = await asyncio.open_connection('127.0.0.1',8888,loop=loop)
        await client.read(reader)


    async def read(reader):
        print("reading")
        data = await reader.read(100)
        print(data)
        await client.write(writer)

    async def write(writer):
        print("writing")
        data=input("enter message")
        writer.write(data.encode())
        await client.read(reader)


client()

            
