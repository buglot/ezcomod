from tkinter import Frame,Button,Label,Entry,StringVar,Listbox,messagebox,Scrollbar
from tkinter.ttk import Progressbar
from utils import ClientServer,MangagerProfile,TypeCommu

class BaseFrame(Frame):
    def __init__(self, master = None):
        super().__init__(master)
    def log(self,*x):
        pass

class ClientFrame(BaseFrame):
    __index:int = 0
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(fill="x",padx=10)
        self.modfile = MangagerProfile()
        self.modfile.log = self.log
        self.modfile.perCentdownload = self.set_progress
        self.box1 = Frame(self)
        self.box1.pack(fill="x",anchor="center",pady=4)
        Label(self.box1, text="IP or URL:").pack(side="left")
        self.ip = Entry(self.box1)
        self.ip.pack(side="left", fill="x", expand=True)  
        self.button_connect = Button(self.box1,text="Connect",command=self.connect)
        self.button_connect.pack()
        self.progress = Progressbar(self, orient="horizontal", length=250, mode="determinate")
        self.progress.pack(fill="x")
        self.box3 = Frame(self)
        self.box3.pack()
        Label(self,text="Log").pack(anchor="w")
        self.box2= Frame(self)
        self.box2.pack(fill="x")
        self.scrollbar = Scrollbar(self.box2)
        self.scrollbar.pack(side="right",fill="y")
        self.Listbox = Listbox(self.box2,yscrollcommand=self.scrollbar.set)
        self.Listbox.pack(side="left",fill="both",expand=True)
        self.scrollbar.config(command=self.Listbox.yview)
        Button(self,text="back to main menu",command=self.master.back).pack(pady=5)

    def connect(self):
        if self.ip.get() !="":
            ip,port=self.ip.get().split(":")
            self.__connect_server(ip,int(port))
            self.Buttom_sync = Button(self.box3,text="sync",bg="skyblue",command=self.sync)
            self.Buttom_sync.pack()
        else:
            messagebox.showerror(title="error",message="Plz put ip or url or conenection")
    def __connect_server(self,ip,port):
        self.__server = ClientServer(ip,port)
        self.__server.log = self.log
        self.__server.doSync = self.doSync
        self.modfile.downlaoded=self.downloaded
        self.modfile.downloading=self.downloading
        self.__server.connect()
        self.__server.sendCommu(TypeCommu.TYPE_SYNC)
    def sync(self):
        if self.modfile.isProcess==False:
            self.__server.sendCommu(TypeCommu.TYPE_SYNC)
            self.set_progress(0)
        else:
            messagebox.showerror(title="error",message="Processing Plz Wait!!")
    def disconnect(self):
        self.__server.stop()
    def addList(self,x:str):
        self.Listbox.insert(self.__index,x)
        self.Listbox.yview_moveto(self.__index)
        self.__index+=1
    def log(self,*x):
        self.addList(" ".join(map(str,x)))
    downloadurl :str|None=None
    def doSync(self,json_data:dict):
        self.log(json_data.get("download_url"))
        self.downloadurl = json_data.get("download_url")
        self.modfile.doUpdate = self.doUpdate
        self.modfile.createProfileClient(json_data.get("sha256"),json_data.get("download_url"),json_data.get("profile_name"))
    def doUpdate(self):
        if self.downloadurl != None:
            self.modfile.changeModFolder(self.downloadurl)
            self.modfile.setNowProfile(self.downloadurl)
            self.modfile.updateNowProfile()
            self.downloadurl = None
    def set_progress(self,percent: int|float):
        self.progress["value"] = percent
    def downloading(self):
        self.__server.sendCommu(TypeCommu.TYPE_DOWNLOADING)
    def downloaded(self):
        self.__server.sendCommu(TypeCommu.TYPE_DOWNLOADED)