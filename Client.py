import socket as sock
from threading import Thread
from tkinter import *
import time
import json
class messenger:

    def __init__(self):
        top = Tk()
        host = '127.0.0.1'
        port = 1661
        
        start = time.time()
        print(start)

        top.title("Private Chat")


        self.username = ""
        self.groupName = "General"
        self.s = sock.socket(sock.AF_INET,sock.SOCK_STREAM)
        self.s.connect((host,port))
        Thread(target=messenger.getmsg, args=(self.s,self)).start()
        self.message = Entry(top,text="Please enter Message")
        self.message.grid(row=2,column=0,columnspan=5)
        
        menu = Menu(top)
        self.GroupMenu = Menu(menu,tearoff=0)
        self.GroupMenu.add_command(label="current group:"+self.groupName)
        self.GroupMenu.add_command(label="Find Group")
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
        
        self.send = Button(top,text="SEND",command=lambda:messenger.sendmsg(self.s,self))
        self.send.grid(row=2,column = 6)

        self.display = Text(top,height=20,width=30)
        self.display.grid(row = 1, column = 0, columnspan = 5)
        self.scroll = Scrollbar(top)
        self.scroll.grid(row = 1,column = 6,rowspan=5)
        self.scroll.config(command=self.display.yview)
        self.display.config(yscrollcommand=self.scroll.set)

        top.config(menu=menu)
        self.send.mainloop()
        self.display.mainloop()
        self.scroll.mainloop()
        self.message.mainloop()
        
    def sendmsg(s,self):
        if(self.username == ""):
            message = json.dumps({"code":0,"Message":self.message.get()})
            s.send(message.encode())
            self.username = self.message.get()
            self.message.delete(0,END)
        else:
            message = json.dumps({"code":1,"Message":self.message.get()})
            s.send(message.encode())

    def getmsg(s,self):
        while True:
            print("listening")
            js = s.recv(1024)
            msg = json.loads(js.decode())
            print(msg["Message"])
            if(msg["code"] == 5):
                self.group = msg["Message"]
                print("setting new group to"+msg["Message"])
                self.GroupMenu.entryconfigure(1,label="Group:"+msg["Message"])
            else:
                self.display.insert(END,msg["Message"]+"\n")
            
    def CreateGroup(self):
        pop = Tk()
        name = Label(pop,text="Name")
        name.grid(row = 0,column = 0)

        name_enter = Entry(pop,text="Enter group name")
        name_enter.grid(row=0,column=1,columnspan=3)
        commit = Button(pop,text="Accept",command = lambda:messenger.SendGroup(name_enter.get(),self))
        commit.grid(row=1,column=0)
        
        mainloop()

    def SendGroup(name,self):
        message = json.dumps({"code":5,"Message":name})
        self.s.send(message.encode())
        

messenger()
