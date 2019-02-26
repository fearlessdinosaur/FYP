import socket as sock
from threading import Thread
from tkinter import *
import time
import simplejson as json

import Crypto
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto import Random

import base64

class messenger:

    def __init__(self):
        self.top = Tk()
        self.height = self.top.winfo_screenheight()
        self.width = self.top.winfo_screenwidth()
        self.top.geometry("725x375")
        self.count =0
        host = '127.0.0.1'
        port = 1661
        self.groups = ["General"]
        rand = Random.new().read
        self.key = RSA.generate(2048,rand)
        self.pub = self.key.publickey()
        
        self.top.title("Private Chat")
        displayFrame = Frame(self.top)
        inputFrame = Frame(self.top)
        displayFrame.grid(row=0,column=0,columnspan = 3)
        inputFrame.grid(row=1,column=1)

        self.display = Text(displayFrame,height=20,width= 80)
        self.display.grid(row = 1, column = 1, columnspan = 5,padx=(40,5))
        self.display.tag_configure("System",foreground="dark blue")
        self.scroll = Scrollbar(displayFrame)
        self.scroll.grid(row = 1,column = 6,rowspan=5)
        self.scroll.config(command=self.display.yview)
        self.display.config(yscrollcommand=self.scroll.set)

        
        self.username = ""
        self.groupName = "General"
        self.messages = {}
        self.s = sock.socket(sock.AF_INET,sock.SOCK_STREAM)
        self.s.connect((host,port))
        Thread(target=messenger.getmsg, args=(self.s,self)).start()
        Thread(target=messenger.timer, args =(self,)).start()
        self.message = Entry(inputFrame,text="Please enter Message",width=60)
        self.message.grid(row=2,column=0,columnspan=5)
        
        menu = Menu(self.top)
        self.GroupMenu = Menu(menu,tearoff=0)
        self.GroupMenu.add_command(label="current group:"+self.groupName)
        self.GroupMenu.add_command(label="Find Group" ,command = lambda:messenger.FindGroup(self))
        self.GroupMenu.add_command(label="create Group",command = lambda:messenger.CreateGroup(self))
        self.GroupMenu.add_command(label="Leave Group")
        menu.add_cascade(label="group",menu=self.GroupMenu)

        UserMenu = Menu(menu,tearoff=0)
        UserMenu.add_command(label="change username")
        UserMenu.add_command(label="Logoff")
        UserMenu.add_command(label="Self Destruct")
        menu.add_cascade(label="User",menu=UserMenu)

        SettingMenu = Menu(menu,tearoff=0)
        SettingMenu.add_command(label="placeholder1")
        SettingMenu.add_command(label="placeholder2")
        SettingMenu.add_command(label="placeholder3")
        menu.add_cascade(label="Settings",menu=SettingMenu)
        
        self.send = Button(inputFrame,text="SEND",command=lambda:messenger.sendmsg(self.s,self))
        self.send.grid(row=2,column = 6)

        self.top.config(menu=menu)
        self.top.protocol("WM_DELETE_WINDOW",lambda:messenger.shutdown(self.s,self))
        self.send.mainloop()
        self.display.mainloop()
        self.scroll.mainloop()
        self.message.mainloop()
        self.top.mainloop()
        
    def sendmsg(s,self):
        if(self.username == ""):
            message = json.dumps({"code":0,"Message":self.message.get(),"username":self.username})
            s.send(message.encode())
            self.username = self.message.get()
            print(self.username)
            key = self.pub.exportKey(format = "PEM",passphrase=None,pkcs=1)
            s.send(key)
        else:
            message =self.message.get()
            self.broadcast(message)
        self.message.delete(0,END)

    def getmsg(s,self):
        while True:
            counter = 0
            print("listening")
            js = s.recv(3000)
            msg = json.loads(js.decode())
            if(msg["code"] == 5):
                self.group = msg["Message"]
                print("setting new group to"+msg["Message"])
                self.GroupMenu.entryconfigure(0,label="Group:"+msg["Message"])
            if(msg["code"] == 1):
                decr = PKCS1_OAEP.new(self.key)
                message = base64.b64decode(msg["Message"])
                message = decr.decrypt(message)
                self.display.insert(END,msg["sender"]+":"+message.decode()+"\n")
                self.messages[self.count] = {"sender":msg["sender"],"message":message.decode(),"time":round(time.time(),3)}
                self.count = self.count+1
            if(msg["code"] == 7):
                self.display.insert(END,msg["Message"]+"\n","System")
            if(msg["code"] == 8):
                self.display.insert(END,"GROUPS" + "\n","System")
                self.groups = msg["Message"]
            if(msg["code"] == 10):
                self.key = msg["Message"]
                print(self.key)
            if(msg["code"] == 11):
                self.groupMems = msg["Message"]
                for x in self.groupMems:
                    self.groupMems[x] = RSA.importKey(self.groupMems[x],passphrase=None)
                print("setting group member list")
            if(msg["code"] == 12):
                print("new member joined")
                print(msg["user"])
                self.groupMems[msg["user"]] = RSA.importKey(msg["Message"],passphrase=None)
                print(self.groupMems)    
            
    # opens group creation window         
    def CreateGroup(self):
        pop = Tk()
        name = Label(pop,text="Name")
        name.grid(row = 0,column = 0)

        name_enter = Entry(pop,text="Enter group name")
        name_enter.grid(row=0,column=1,columnspan=3)
        commit = Button(pop,text="Accept",command = lambda:[messenger.SendGroup(name_enter.get(),self),pop.destroy()])
        commit.grid(row=1,column=0)
        mainloop()
    # opens group selection window
    def FindGroup(self):
        message = json.dumps({"code":7,"Message":"group request","username":self.username})
        self.s.send(message.encode())
        pop = Tk()
        group = Label(pop,text= "group")
        group.grid(row=0,column = 0)
        var = StringVar(pop)
        var.set(self.groups[0])
        print("populating dropdown:\n")
        print(self.groups)
        print("dropdown populated")
        drop = OptionMenu(pop,var,*self.groups)
        drop.grid(row=0,column=1)

        pick = Button(pop,text="choose",command = lambda:[messenger.setGroup(var.get(),self),pop.destroy()])
        pick.grid(row=1,column=0)
    #group join function
    def setGroup(group,self):
        print("joining new group")
        message = json.dumps({"code":9,"Message":group,"username":self.username})
        self.s.send(message.encode())
    #group creation function
    def SendGroup(name,self):
        message = json.dumps({"code":5,"Message":name,"username":self.username})
        self.s.send(message.encode())
    def broadcast(self,msg):
        for x in self.groupMems:
            print("sending message to "+x)
            encryptor = PKCS1_OAEP.new(self.groupMems[x])
            cipher = encryptor.encrypt(msg.encode())
            message = json.dumps({"code":1,"Message":base64.b64encode(cipher),"sender":self.username,"reciever":x})
            self.s.send(message.encode())
    # sends exit message to server, allowing for graceful shutdown
    def timer(self):
        past = time.time()
        popped = []
        while True:
            current = time.time()
            if(round(current - past,3) %10 == 0):
                temp = self.messages
                print(temp)
                for x in temp:
                    print(abs(round(temp[x]["time"] - current)))
                    if abs(round(temp[x]["time"] - current))>=30:
                        if(self.messages[x]["message"] == "-- burned --"):
                            if(x not in popped):
                                popped.append(x)
                            print(popped)
                        else:
                            self.messages[x]["message"] = "-- burned --"
                            self.messages[x]["time"] = round(time.time())
                self.display.delete(1.0,END)
                for x in popped:
                    self.messages.pop(x)
                    popped.remove(x)
                    print(self.messages)
                for x in self.messages:
                    self.display.insert(END,self.messages[x]["sender"]+":"+self.messages[x]["message"]+"\n")
    def shutdown(s,self):
        message = json.dumps({"code":2,"Message":"shutdown request","username":self.username})
        s.send(message.encode())
        self.top.destroy()
        
if __name__ == "__main__":
    messenger()
