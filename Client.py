# begin imports
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
# end imports

class messenger:
    
    # function to create buttons and labels for all files offered by the system
    def check_files(self):
        
        # instantiating lists for buttons
        accepts = []
        denys = []
        labels = []
        
        for j in range(0,len(self.files)) :
            
            #creates the label for the file and it in the window
            string = str(self.files[j][0])+"  from "+ str(self.files[j][1])
            label = Label(self.side_panel,text = string,width=20)
            label.grid(row=j+1,column=0)# j+1 tells the button where to go within the length of the screen
            
            #creates the accept and refuse buttons and places them in the window
            self.accept = Button(self.side_panel,text = "Accept")
            self.refuse= Button(self.side_panel,text = "Refuse")
            self.accept.grid(row = j+1,column = 1)# j+1 tells the button where to go within the length of the screen
            self. refuse.grid(row = j+1,column = 2)# j+1 tells the button where to go within the length of the screen   
            
            #adds newly created labels and buttons to their respective lists 
            accepts.append(self.accept)
            denys.append(self.refuse)
            labels.append(label)
            
            # sets commands for button to call once it has been pressed
            self.accept["command"] = lambda:[self.fileInform(self.files[j][0]),self.download_file(self.files[j][0]),self.files.pop(j),self.destructor(accepts[j]),self.destructor(denys[j]),self.destructor(labels[j])]
            self.refuse["command"] = lambda:[self.fileInform(self.files[j][0]),self.files.pop(j),self.destructor(denys[j]),self.destructor(accepts[j]),self.destructor(labels[j])]
            
        # repeats command after 10000 seconds
        self.top.after(10000,self.check_files)
    
    #function to tell the server that a file has been downloaded
    def fileInform(self,file):
        js = json.dumps({"code":15,"Message":file})# contructs the js message block sent to the server
        self.s.send(js.encode())# sends encoded message
        
    # function to externally call the tkinter destroy method.    
    def destructor(self,thing):
        thing.destroy()
    # init function to run initial setup    
    def __init__(self):
        # start basic variable initialisation
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
        # end basic variable initialisation
        
        # create socket connection
        self.s = sock.socket(sock.AF_INET,sock.SOCK_STREAM)
        self.s.connect((host,port))
        
        #generate RSA key
        rand = Random.new().read
        self.key = RSA.generate(2048,rand)
        self.pub = self.key.publickey()        
        
        # construct login window
        self.root = Tk()
        self.root.geometry("200x100")#set window size
        self.root.wm_iconbitmap('project_logo.ico')# set logo
        
        #create neccessary frames for layout management
        self.inp_box = Frame(self.root)
        self.button_box = Frame(self.root)
        
        #create neccessary buttons and labels
        name = Entry(self.inp_box)
        logLabel = Label(self.inp_box,text="Login:")
        accept = Button(self.button_box,text="Accept",command=lambda:[self.userCheck(name.get())])# sends username to usercheck function
        close = Button(self.button_box,text="Close",command=lambda: self.root.destroy())# closes down window
        
        # lay out the widgets within the window
        self.inp_box.pack(padx = 2,pady=10)
        logLabel.pack(side="left")
        name.pack(side="left")
        self.button_box.pack(pady=20)
        accept.pack(side="left",padx=10)
        close.pack(side="left",padx=5)
        
        # lauch main loop
        self.root.mainloop()
    
    # function to check and set username  
    def userCheck(self,username):
        
        message = json.dumps({"code":0,"Message":username,"username":self.username}) # builds message block
        self.s.send(message.encode())# sends message
        # recieves message from server and stores it in "x"
        x = self.s.recv(1024)
        # converts self from json to a dictionary
        x = json.loads(x)
        
        # if message = "username taken" tells the user that they they cannot login and to pick another
        if( x["Message"] == "uname Taken"):
            print("username is incorrect")
            lab = Label(self.root,text="username taken, try another")
            lab.pack()
            
        else: # else allows them to log in 
            
            self.username = username # sets username variable to chosen Uname
            # exports users key
            key = self.pub.exportKey(format = "PEM",passphrase=None,pkcs=1)
            # sends key to server
            self.s.send(key)
            # destroys login window
            self.root.destroy()
            # runs chat app
            self.chat_app()
     
    # function to run the chat application GUI      
    def chat_app(self):
        self.top = Tk()
        self.top.wm_iconbitmap('project_logo.ico')
        self.height = 400
        self.width = 850
        
        self.top.geometry('{}x{}'.format(self.width,self.height))
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
        
        # creates task bar
        menu = Menu(self.top)
        self.Group_Menu = Menu(menu,tearoff=0)
        self.Group_Menu.add_command(label="current group:"+self.groupName)
        self.Group_Menu.add_command(label="Find Group" ,command = lambda:messenger.FindGroup(self))
        self.Group_Menu.add_command(label="create Group",command = lambda:messenger.CreateGroup(self))
        self.Group_Menu.add_command(label="Leave Group",command = lambda:messenger.setGroup("general",self))
        menu.add_cascade(label="group",menu=self.Group_Menu)

        UserMenu = Menu(menu,tearoff=0)
        UserMenu.add_command(label="Logoff")
        menu.add_cascade(label="User",menu=UserMenu)
        
        File_Menu = Menu(menu,tearoff=0)
        File_Menu.add_command(label="Upload File",command = lambda:messenger.FileUpload(self,))
        menu.add_cascade(label="Files",menu=File_Menu)
        # finish creating task bar
        
        self.send = Button(inputFrame,text="SEND",command=lambda:messenger.sendmsg(self.s,self))
        self.send.grid(row=2,column = 6)
        
        self.top.config(menu=menu)
        self.top.protocol("WM_DELETE_WINDOW",lambda:[messenger.shutdown(self.s,self),self.top.destroy()])
        
        # starts check file loop
        self.check_files()
        
        # starts all neccessary threads
        Thread(target=messenger.getmsg, args=(self.s,self)).start()
        Thread(target=messenger.timer, args =(self,)).start()
        Thread(target=messenger.FTP_setup, args =(self,)).start()        
        self.top.mainloop()       
    
    # function to display file upload window    
    def FileUpload(self):
        top = Tk()
        top.geometry("200x70")
        fileBox = Frame(top)
        path = Entry(fileBox)
        browse = Button(fileBox,text="Browse",command = lambda: path.insert(1,filedialog.askopenfilename(initialdir="C:/",filetypes =(("text Files",".txt"),("All Files","*.*")),title = "Please select a file to upload")) )
        subButton  = Button(top,text="OK",command = lambda:[self.upload_File(path.get()),top.destroy()])
        canButton = Button(top,text="Cancel",command =lambda:top.destroy())
        fileBox.pack(pady=5)
        path.pack(side="left")
        browse.pack(side="left",padx=3)
        subButton.pack(side="left",padx=20)
        canButton.pack(side="left",padx=20)
        top.lift()
        mainloop()  
    
    #function to append to the system file list    
    def FileDownload(self,file,sender):
        self.files.append([file,sender])
    
    #function to run initial ftp setup
    def FTP_setup(self):
        self.ftp = FTP('')
        self.ftp.connect('localhost',1026)
        self.ftp.login()
        self.ftp.cwd('General')
        self.ftp.retrlines('LIST')  
    
    #function to send a message when send button is pressed    
    def sendmsg(s,self):
        message =self.message.get()
        # function to send message to each user in user group
        self.broadcast(message)
        # clears input window
        self.message.delete(0,END)

    # function to listen for incoming messages
    def getmsg(s,self):
        counter = 0
        
        #runs until flag tells it to stop
        while self.shutdown_flag == False:
            
            # ensures that no messages sent if error occurs in sending
            try:
                js = s.recv(2048)
            except:
                self.ftp.close()
                exit(0)
            # regular expression to split incoming messages into a buffer    
            l = re.findall("^{.+?}|{.+?{.+?}}",js.decode())
            
            # for each message recieved
            for x in l:
                #fixes message if a "}" has been dropped
                try:
                    msg = json.loads(x)
                except:
                    msg = x+ "}"
                    msg = json.loads(msg)
                    
                # begin code comparison    
                if(msg["code"] == 5):
                    self.group = msg["Message"]
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
                    
                if(msg["code"] == 11):
                    self.groupMems = msg["Message"]
                    for x in self.groupMems:
                        self.groupMems[x] = RSA.importKey(self.groupMems[x],passphrase=None)
                    
                if(msg["code"] == 12):
                    self.groupMems[msg["user"]] = RSA.importKey(msg["Message"],passphrase=None)
                    time.sleep(5)
                    
                if(msg["code"] == 13):
                    self.FileDownload(msg["Message"],msg["sender"])
                    
                if(msg["code"] == 16):
                    print("dropping user "+msg["Message"])
                    self.dropKey(msg["Message"])
                # end code comparison
    
    # function to remove member from key list
    def dropKey(self,user):
        self.groupMems.pop(user)
        
    # opens group creation window
    def CreateGroup(self):
        pop = Tk()
        dataBox = Frame(pop)
        dataBox.pack(pady=5)
        name = Label(dataBox,text="Name")
        name.pack(side="left")
        pop.geometry("200x100")
        name_enter = Entry(dataBox,text="Enter group name")
        name_enter.pack(side="left")
        commit = Button(pop,text="Accept",command = lambda:[messenger.SendGroup(name_enter.get(),self),pop.destroy()])
        commit.pack(padx=10,pady=10)
        mainloop()
        
    # opens group selection window
    def FindGroup(self):
        message = json.dumps({"code":7,"Message":"group request","username":self.username})
        self.s.send(message.encode())
        pop = Tk()
        pop.geometry("200x100")
        selArea = Frame(pop)
        selArea.pack()
        group = Label(selArea,text= "group")
        group.pack(side="left")
        var = StringVar(pop)
        var.set(self.groups[0])
        drop = OptionMenu(selArea,var,*self.groups)
        drop.pack(side="left")

        pick = Button(pop,text="choose",command = lambda:[messenger.setGroup(var.get(),self),pop.destroy()])
        cancel = Button(pop,text="cancel",command = lambda:[pop.destroy()])
        pick.pack(side="left",padx=20,pady=10)
        cancel.pack(side="left",padx=30,pady=10)
        
    #group join function
    def setGroup(group,self):
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
        
    # function to send message to each member of a group 
    def broadcast(self,msg):
        #for each member
        for x in self.groupMems:
            # creates new encryptor, using members public key
            encryptor = PKCS1_OAEP.new(self.groupMems[x])
            # encrypts message
            cipher = encryptor.encrypt(msg.encode())
            # encodes message in base 64 and constructs a json message block
            message = json.dumps({"code":1,"Message":base64.b64encode(cipher),"sender":self.username,"reciever":x})
            # sends message
            self.s.send(message.encode())
            
    # uploads file to ftp server
    def upload_File(self,file):
        # creates connection to server
        self.ftp = FTP('')
        self.ftp.connect('localhost',1026)
        self.ftp.login()
        # ensures working directory is correct
        self.ftp.cwd("..")
        self.ftp.cwd("../"+self.groupName+"/")
        
        self.ftp.retrlines('LIST')   
        # splits file path given
        x = file.split("/")
        # tells server that a file is being uploaded by this user
        js = json.dumps({"code":14,"Message":x[len(x)-1],"sender":self.username})
        self.s.send(js.encode())
        # sends file to ftp server
        self.ftp.storlines('STOR '+x[len(x)-1], open(file, 'rb'))
        self.ftp.close()
        
    # function to download files from ftp server    
    def download_file(self,file):
        self.ftp = FTP('')
        self.ftp.connect('localhost',1026)
        self.ftp.login()
        # ensures working directory is correct
        self.ftp.cwd(self.groupName)
        #writes file
        x = open(file,"wb")
        self.ftp.retrbinary("RETR "+file,x.write)
        self.ftp.close()
        x.close()
        
    # timing thread 
    def timer(self):
        # gets original time
        past = time.time()
        popped = []
        # runs while not attempting a shutdown
        while self.shutdown_flag == False:
            
            # sleep for 10 seconds
            time.sleep(10)
            # get current time
            current = time.time()
            temp = self.messages
            
            #system checks group list for updates
            message = json.dumps({"code":7,"Message":"group request","username":self.username})
            
            # tries to send the message 
            try:
                self.s.send(message.encode())
            except:
                exit(0)
                break
            
            # for each message in temp
            for x in temp:
                #checks arrival time
                if abs(round(temp[x]["time"] - current))>=30:
                    # if message is already burned, add it to an array to be deleted
                    if(self.messages[x]["message"] == "-- burned --"):
                        if(x not in popped):
                            popped.append(x)
                    # else burn the message
                    else:
                        self.messages[x]["message"] = "-- burned --"
                        self.messages[x]["time"] = round(time.time())#reset stored time
            # checks flag before proceeding            
            if(self.window_flag == True):
                self.display.delete(1.0,END) # clears window 
            else:
                exit(0)
                break
            # pops burned messages
            for burned_message in popped:
                self.messages.pop(burned_message)
                popped.remove(burned_message)
            # repopulates display window
            for x in self.messages:
                if(self.messages[x]["sender"] == "system"):
                    self.display.insert(END,self.messages[x]["message"]+"\n","System")
                else:
                    self.display.insert(END,self.messages[x]["sender"]+":"+self.messages[x]["message"]+"\n")
    
    # shuts down system                
    def shutdown(s,self):
        self.shutdown_flag = True
        self.window_flag = False
        message = json.dumps({"code":2,"Message":"shutdown request"})
        s.send(message.encode())
        self.top.destroy()
        self.s.shutdown(sock.SHUT_RDWR)
        self.s.close()
        self.ftp.close()
        exit(0)

if __name__ == "__main__":
    messenger()
