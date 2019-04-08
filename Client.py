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
        accepts = []
        denys = []
        labels = []
        for j in range(0,len(self.files)) :
            print("creating button for "+self.files[j][0])
            string = str(self.files[j][0])+"  from "+ str(self.files[j][1])
            label = Label(self.side_panel,text = string,width=20)
            label.grid(row=j+1,column=0)
            self.accept = Button(self.side_panel,text = "Accept")
            self.refuse= Button(self.side_panel,text = "Refuse")
            self.accept.grid(row = j+1,column = 1)
            self. refuse.grid(row = j+1,column = 2)            
            accepts.append(self.accept)
            denys.append(self.refuse)
            labels.append(label)
            self.accept["command"] = lambda:[self.download_file(self.files[j][0]),self.files.pop(j),self.destructor(accepts[j]),self.destructor(denys[j]),self.destructor(labels[j])]
            self.refuse["command"] = lambda:[self.files.pop(j),self.destructor(denys[j]),self.destructor(accepts[j]),self.destructor(labels[j])]
        self.top.after(10000,self.check_files)
             
    def destructor(self,thing):
        print("destroying "+str(thing))
        thing.destroy()
        
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
        self.root.geometry("200x100")
        self.root.wm_iconbitmap('project_logo.ico')
        self.inp_box = Frame(self.root)
        name = Entry(self.inp_box)
        self.button_box = Frame(self.root)
        logLabel = Label(self.inp_box,text="Login:")
        accept = Button(self.button_box,text="Accept",command=lambda:[self.userCheck(name.get())])
        close = Button(self.button_box,text="Close",command=lambda: self.root.destroy())
        self.inp_box.pack(padx = 2,pady=10)
        logLabel.pack(side="left")
        name.pack(side="left")
        self.button_box.pack(pady=20)
        accept.pack(side="left",padx=10)
        close.pack(side="left",padx=5)
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
        self.top.wm_iconbitmap('project_logo.ico')
        self.height = 400
        self.width = 850
        print(self.height,self.width)
        
        self.top.geometry('{}x{}'.format(self.width,self.height))
        rand = Random.new().read
        self.side_panel = Frame(self.top,relief=SUNKEN)
        self.side_panel.grid(row=0,column=5)
        
        self.downLabel = Label(self.side_panel,text= "downloads")
        self.downLabel.grid(row=0,column=0)
        self.tag = Label(self.side_panel,text = "Downloads")
        self.tag.grid(row=0,column=0)
        self.top.title("Crypto Chat")
        display_Frame = Frame(self.top,width=self.width-200,height=self.height-50)
        display_Frame.grid_columnconfigure(0, weight=1)
        inputFrame = Frame(self.top)
        display_Frame.grid(row=0,column=0,columnspan= 3,rowspan=10)
        display_Frame.grid_propagate(False)
        
        inputFrame.grid(row=11, column=1)
        self.display = Text(display_Frame)
        self.display.grid(row = 1, column = 1, columnspan = 5,sticky="ew")
        self.display.tag_configure("System",foreground="dark blue")
        
        scroll_Frame = Frame(self.top,height = self.height - 60)
        scroll_Frame.grid(row=4,column=4)
        self.scroll = Scrollbar(scroll_Frame)
        self.scroll.grid(row = 1,column = 6,rowspan=10,sticky="ns")
        self.scroll.config(command=self.display.yview)
        self.display.config(yscrollcommand=self.scroll.set)
        
        self.message = Entry(inputFrame,text="Please enter Message",width=70)
        self.message.grid(row=2,column=0,columnspan=5)

        menu = Menu(self.top)
        self.Group_Menu = Menu(menu,tearoff=0)
        self.Group_Menu.add_command(label="current group:"+self.groupName)
        self.Group_Menu.add_command(label="Find Group" ,command = lambda:messenger.FindGroup(self))
        self.Group_Menu.add_command(label="create Group",command = lambda:messenger.CreateGroup(self))
        self.Group_Menu.add_command(label="Leave Group",command = lambda:messenger.setGroup("general",self))
        menu.add_cascade(label="group",menu=self.Group_Menu)

        UserMenu = Menu(menu,tearoff=0)
        #UserMenu.add_command(label="change username")
        UserMenu.add_command(label="Logoff")
        menu.add_cascade(label="User",menu=UserMenu)
        
        File_Menu = Menu(menu,tearoff=0)
        File_Menu.add_command(label="Upload File",command = lambda:messenger.FileUpload(self,))
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
        top.lift()
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
                try:
                    msg = json.loads(x)
                except:
                    msg = x+ "}"
                    msg = json.loads(msg)
                    
                if(msg["code"] == 5):
                    print("new group ="+msg["Message"])
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
                if(msg["code"] == 16):
                    self.dropKey(msg["Message"])
                    
        print("recieve has been shut down")

    def dropKey(self,user):
        self.groupMems.pop(user)
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
        drop = OptionMenu(pop,var,*self.groups)
        drop.grid(row=0,column=1)

        pick = Button(pop,text="choose",command = lambda:[messenger.setGroup(var.get(),self),pop.destroy()])
        pick.grid(row=1,column=0)
        
    #group join function
    def setGroup(group,self):
        print("joining new group")
        self.groupMems = {}
        self.groupName = group
        message = json.dumps({"code":9,"Message":group,"username":self.username})
        self.s.send(message.encode())
        
    #group creation function
    def SendGroup(name,self):
        self.groupName = name
        message = json.dumps({"code":5,"Message":name,"username":self.username})
        self.s.send(message.encode())
        self.groupMems = {}
        
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
        print(self.groupName)
        self.ftp.connect('localhost',1026)
        self.ftp.login()
        self.ftp.cwd("..")
        self.ftp.cwd("../"+self.groupName+"/")
        self.ftp.retrlines('LIST')          
        x = file.split("/")
        print("working till this point")
        js = json.dumps({"code":14,"Message":x[len(x)-1],"sender":self.username})
        print("starting this...")
        self.s.send(js.encode())
        print("finished that ok...")
        self.ftp.storlines('STOR '+x[len(x)-1], open(file, 'rb'))
        
    def download_file(self,file):
        print(file)
        self.ftp = FTP('')
        self.ftp.connect('localhost',1026)
        self.ftp.login()
        self.ftp.cwd(self.groupName)
        print(file)
        x = open(file,"wb")
        self.ftp.retrbinary("RETR "+file,x.write)
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
            
            #system checks group list for updates
            message = json.dumps({"code":7,"Message":"group request","username":self.username})
            try:
                self.s.send(message.encode())
            except:
                exit(0)
                break
            
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
