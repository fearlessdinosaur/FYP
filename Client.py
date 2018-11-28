import asyncio
import readchar
from tkinter import *
class client:
    
    def __init__(self):
        self.Message_Buffer = []
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(asyncio.gather(client.send_message(self.loop,self,),client.get_message(self.loop,self,)))
        
    async def send_message(loop,self):
        reader, writer = await asyncio.open_connection('127.0.0.1', 1661,
                                                   loop=loop)
        while 1:
            message = input(">>")
            print('Send: %r' % message)
            writer.write(message.encode())

    async def get_message(loop,self):
        reader, writer = await asyncio.open_connection('127.0.0.1', 1661,
                                                   loop=loop)

        while True:
            data = await reader.read(100)
            print('Received: %r' % data.decode())
            if(data.decode() == "{end}"):
                break;
        writer.close()
client()

            
