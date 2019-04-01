import socket as sock
from threading import Thread
from tkinter import *
from tkinter import filedialog
import time
import re
import simplejson as json
from sys import exit
from ftplib import FTP
import ftplib
import Crypto
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto import Random
import base64
from ftplib import FTP

class messenger:
    
    
    def check_files(self):
        c = 0
        accept = []
        refuse = []
        for j in range(0,len(self.files)) :
            
            string = "do you want to download "+ str(self.files[j][0])+"  from "+ str(self.files[j][1])
            label = Label(self.side_panel,text = string)
            label.grid(row=j+1,column=0)
            accept = Button(self.side_panel,text = "Accept",command = lambda:[self.download_file(self.files[j][0]),self.files.pop(j)])
            accept.grid(row = j+1,column = 1)
            refuse= Button(self.side_panel,text = "Refuse",command = lambda:self.file.pop(j))
            refuse.grid(row = j+1,column = 2)
        self.top.after(1000,self.check_files)

    def __init__(self):
    
        self.shutdown_flag = False
        self.window_flag = True
        self.files = []
        self.count =0
        host = '127.0.0.1'
        port = 1661
        self.groups = ["General"]
        self.username = ""
        self.groupName = "General"
        self.messages = {}
        self.s = sock.socket(sock.AF_INET,sock.SOCK_STREAM)
        self.s.connect((host,port))
        
        rand = Random.new().read
        self.key = RSA.generate(2048,rand)
        self.pub = self.key.publickey()        
        
        self.root = Tk()
        name = Entry(self.root)
        accept = Button(self.root,text="Accept",command=lambda:[self.userCheck(name.get())])
        close = Button(self.root,text="close",command=lambda: self.root.destroy())
        
        name.grid(row = 0,column=0)
        accept.grid(row = 2,column=0)
        close.grid(row = 2,column=1)
        self.root.mainloop()
        
    def userCheck(self,username):
        message = json.dumps({"code":0,"Message":username,"username":self.username})
        self.s.send(message.encode())
        x = self.s.recv(1024)
        x = json.loads(x)
        if( x["Message"] == "sorry username is taken"):
            lab = Label(self.root,text="username taken, try another")
            lab.grid(row=1,column=0)
            
        else:
            self.username = username
            print(self.username)
            key = self.pub.exportKey(format = "PEM",passphrase=None,pkcs=1)
            self.s.send(key)
            self.root.destroy()
            self.chat_app()
            
    def chat_app(self):
        self.top = Tk()
        self.height = self.top.winfo_screenheight()
        self.width = self.top.winfo_screenwidth()
        self.top.geometry("725x375")
        rand = Random.new().read
        self.side_panel = Frame(self.top,bg="black",relief=SUNKEN)
        self.side_panel.grid(row=0,column=4)
        self.tag = Label(self.side_panel,text = "Downloads")
        self.tag.grid(row=0,column=0)
        self.top.title("Private Chat")
        display_Frame = Frame(self.top)
        inputFrame = Frame(self.top)
        display_Frame.grid(row=0,column=0,columnspan= 3,rowspan=10)
        inputFrame.grid(row=11, column=1)
        self.display = Text(display_Frame, height=20,width= 80)
        self.display.grid(row = 1, column = 1, columnspan = 5,padx=(40,5))
        self.display.tag_configure("System",foreground="dark blue")
        self.scroll = Scrollbar(display_Frame)
        self.scroll.grid(row = 1,column = 6,rowspan=10)
        self.scroll.config(command=self.display.yview)
        self.display.config(yscrollcommand=self.scroll.set)
        
        self.message = Entry(inputFrame,text="Please enter Message",width=60)
        self.message.grid(row=2,column=0,columnspan=5)

        menu = Menu(self.top)
        self.Group_Menu = Menu(menu,tearoff=0)
        self.Group_Menu.add_command(label="current group:"+self.groupName)
        self.Group_Menu.add_command(label="Find Group" ,command = lambda:messenger.FindGroup(self))
        self.Group_Menu.add_command(label="create Group",command = lambda:messenger.CreateGroup(self))
        self.Group_Menu.add_command(label="Leave Group")
        menu.add_cascade(label="group",menu=self.Group_Menu)

        UserMenu = Menu(menu,tearoff=0)
        UserMenu.add_command(label="change username")
        UserMenu.add_command(label="Logoff")
        UserMenu.add_command(label="Self Destruct")
        menu.add_cascade(label="User",menu=UserMenu)

        Setting_Menu = Menu(menu,tearoff=0)
        Setting_Menu.add_command(label="placeholder1")
        Setting_Menu.add_command(label="placeholder2")
        Setting_Menu.add_command(label="placeholder3")
        menu.add_cascade(label="Settings",menu=Setting_Menu)
        
        File_Menu = Menu(menu,tearoff=0)
        File_Menu.add_command(label="Upload File",command = lambda:messenger.FileUpload(self,))
        File_Menu.add_command(label="Download File",command = lambda:messenger.FileDownload(self,))
        menu.add_cascade(label="Files",menu=File_Menu)

        self.send = Button(inputFrame,text="SEND",command=lambda:messenger.sendmsg(self.s,self))
        self.send.grid(row=2,column = 6)
        
        self.top.config(menu=menu)
        self.top.protocol("WM_DELETE_WINDOW",lambda:[messenger.shutdown(self.s,self),self.top.destroy()])
        self.check_files()
        Thread(target=messenger.getmsg, args=(self.s,self)).start()
        Thread(target=messenger.timer, args =(self,)).start()
        Thread(target=messenger.FTP_setup, args =(self,)).start()        
        self.top.mainloop()       
        
    def FileUpload(self):
        top = Tk()
        top.geometry("200x100")
        path = Entry(top)
        browse = Button(top,text="Browse",command = lambda: path.insert(1,filedialog.askopenfilename(initialdir="C:/",filetypes =(("text Files",".txt"),("All Files","*.*")),title = "Please select a file to upload")) )
        subButton  = Button(top,text="OK",command = lambda:[self.upload_File(path.get()),top.destroy()])
        #print(name)
        path.grid(row=0,column=0,columnspan=3)
        browse.grid(row=0,column=4)
        subButton.grid(row=1,column=0)
        mainloop()  
        
    def FileDownload(self,file,sender):
        self.files.append([file,sender])
        print(self.files)
    
    # Based on code from https://www.techinfected.net/2017/07/create-simple-ftp-server-client-in-python.html
    def FTP_setup(self):
        self.ftp = FTP('')
        self.ftp.connect('localhost',1026)
        self.ftp.login()
        self.ftp.cwd('General')
        self.ftp.retrlines('LIST')  
        
    def sendmsg(s,self):
        message =self.message.get()
        print(message)
        self.broadcast(message)
        self.message.delete(0,END)

    def getmsg(s,self):
        counter = 0
        while self.shutdown_flag == False:
            print(self.shutdown_flag)
            print("listening")
            print(s)
            try:
                js = s.recv(2048)
            except:
                self.ftp.close()
                exit(0)
            print(js)
            l = re.findall("^{.+?}|{.+?{.+?}}",js.decode())
            print(l)
            for x in l:
                print(x)
                msg = json.loads(x)
                if(msg["code"] == 5):
                    self.group = msg["Message"]
                    print("setting new group to"+msg["Message"])
                    self.Group_Menu.entryconfigure(0,label="Group:"+msg["Message"])
                if(msg["code"] == 1):
                    decr = PKCS1_OAEP.new(self.key)
                    message = base64.b64decode(msg["Message"])
                    message = decr.decrypt(message)
                    self.display.insert(END,msg["sender"]+":"+message.decode()+"\n")
                    self.messages[self.count] = {"sender":msg["sender"],"message":message.decode(),"time":round(time.time(),3)}
                    self.count = self.count+1
                if(msg["code"] == 7):
                    self.messages[self.count] = {"sender":"system","message":msg["Message"],"time":round(time.time(),3)}
                    self.display.insert(END,msg["Message"]+"\n","System")
                    self.count = self.count+1
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
                    sleep(5)
                if(msg["code"] == 13):
                    self.FileDownload(msg["Message"],msg["sender"])
        print("recieve has been shut down")


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
        self.groupMems = {}
        message = json.dumps({"code":9,"Message":group,"username":self.username})
        self.s.send(message.encode())
        self.ftp.cwd(group)
        
    #group creation function
    def SendGroup(name,self):
        message = json.dumps({"code":5,"Message":name,"username":self.username})
        self.s.send(message.encode())
        self.groupMems = {}
        self.ftp.cwd(group)
        
    def broadcast(self,msg):
        print(self.groupMems)
        for x in self.groupMems:
            print("sending message to "+x)
            encryptor = PKCS1_OAEP.new(self.groupMems[x])
            cipher = encryptor.encrypt(msg.encode())
            message = json.dumps({"code":1,"Message":base64.b64encode(cipher),"sender":self.username,"reciever":x})
            self.s.send(message.encode())
            
    # Based on code from https://www.techinfected.net/2017/07/create-simple-ftp-server-client-in-python.html
    def upload_File(self,file):
        self.ftp = FTP('')
        self.ftp.connect('localhost',1026)
        self.ftp.login()
        self.ftp.cwd('General')
        self.ftp.retrlines('LIST')          
        x = file.split("/")
        print("working till this point")
        js = json.dumps({"code":14,"Message":x[len(x)-1],"sender":self.username})
        print("starting this...")
        self.s.send(js.encode())
        print("finished that ok...")
        self.ftp.storlines('STOR '+x[len(x)-1], open(file, 'rb'))
        
    def download_file(self,file):
        self.ftp = FTP('')
        self.ftp.connect('localhost',1026)
        self.ftp.login()
        self.ftp.cwd('General')
        self.ftp.retrlines('LIST')          
        print(file)
        x = open(file,"w")
        self.ftp.retrlines("RETR "+file,x.write)
        x.close()
        self.ftp.close()
        
    # sends exit message to server, allowing for graceful shutdown
    def timer(self):
        past = time.time()
        popped = []
        while self.shutdown_flag == False:
            print("flag is:"+str(self.shutdown_flag))
            time.sleep(10)
            current = time.time()
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
            if(self.window_flag == True):
                self.display.delete(1.0,END)
            else:
                exit(0)
                break
            for burned_message in popped:
                self.messages.pop(burned_message)
                popped.remove(burned_message)
                print(self.messages)
            for x in self.messages:
                if(self.messages[x]["sender"] == "system"):
                    self.display.insert(END,self.messages[x]["message"]+"\n","System")
                else:
                    self.display.insert(END,self.messages[x]["sender"]+":"+self.messages[x]["message"]+"\n")
    def shutdown(s,self):
        self.shutdown_flag = True
        self.window_flag = False
        print("running shutdown")
        message = json.dumps({"code":2,"Message":"shutdown request","username":self.username})
        s.send(message.encode())
        self.top.destroy()
        self.s.shutdown(sock.SHUT_RDWR)
        self.s.close()
        self.ftp.close()
        exit(0)

if __name__ == "__main__":
    messenger()
