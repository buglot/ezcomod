from re import X
from tkinter import Tk, Frame, Button, Label, Entry, messagebox,StringVar,Listbox,OptionMenu,Scrollbar,_setit
from utils import MangagerProfile
from tkinter import filedialog
from utils import Server
from utils import HTTPServer
from ui.component.createbox import CreateBox
import threading
from utils.socketsServer.typecommu import TypeCommu
class Headerframe (Frame):
    start_int:int = 1
    index_log:int = 0
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(side="top", fill="x",padx=10)
        self.label = Label(self, text="Host Mod server")
        self.label.pack()
        self.box5 = Frame(self)
        self.box5.pack(fill="x")
        Label(self.box5,text="What you DDNS?:").pack(side="left")
        self.text_ddns = StringVar()
        self.ddns = Entry(self.box5,textvariable=self.text_ddns)
        self.ddns.pack(side="left" ,fill="x",expand=True)
        Button(self.box5,text="update",command=self.save_ddns).pack(side="right")
        Label(self, text="file path:").pack()
        self.modfile = MangagerProfile()
        self.modfile.checkProfileAll()
        self.modfile.log = self.log
        self.var = StringVar()
        self.var.set(self.modfile.get_file_path())
        self.entry = Entry(self,textvariable=self.var)
        self.entry.pack(side="top", fill="x")
        if self.modfile.lock:
            self.openfolder_button = Button(self, text="Open Folder", command=self.folder_dialog)
            self.openfolder_button.pack(pady=5)
            self.start_int = 0
        self.box = Frame(self)
        self.box.pack(fill="x")
        self.sco = Scrollbar(self.box)
        self.sco.pack(side="right",fill="y")
        self.viewlog = Listbox(self.box,yscrollcommand=self.sco.set)
        self.viewlog.pack(side="left",fill="both",expand=True)
        self.sco.config(command=self.viewlog.yview)
        if self.start_int:
            th = threading.Thread(target=self.startServer(),daemon=True)
            th.start()
            self.labelserver = Label(self,text="Server ip:"+self.server.host+str(self.server.port))
            self.labelserver.pack()
        self.var_select = StringVar()
        self.profiles = self.modfile.get_profiles()
        self.var_select.set(self.profiles[0]) 
        self.box2 = Frame(self)
        self.box2.pack(fill="x")
        center_box = Frame(self.box2)
        center_box.pack(anchor="center") 
        Label(center_box,text="Select Profile: ").pack(side="left", padx=5)
        self.option = OptionMenu(center_box,self.var_select,*self.profiles,command=self.optionmenu_callback)
        self.option.pack(side="left", padx=5)
        Button(self,text="Update Mod Profile",command=self.updatemod).pack(pady=5,fill="x")
        self.box4 = Frame(self)
        self.box4.pack(pady=5,fill="x")
        self.butCreate = Button(self.box4,text="Create Profile",command=self.showCreatebox)
        self.butCreate.pack(fill="x")
        Label(self,text="Delete Profile name:").pack()
        self.dProfilename = Entry(self)
        self.dProfilename.pack(pady=5,fill="x")
        self.dDeleteProfile = Button(self,text="Delete",command=self.deleteprofile)
        self.dDeleteProfile.pack(pady=5,fill="x")

        self.httpServer= HTTPServer()
        self.httpServer.log=self.log
        httpsMuti = threading.Thread(target=self.httpServer.start,name='httpServer',daemon=True)
        httpsMuti.start()
        self.Syncb = Button(self,text="Sync",background="blue",fg="white",command=self.SyncData) 
        self.Syncb.pack(pady=5,fill="x")
        self.server.profile_name = "default"
        self.server.sha256 = self.modfile.getSha256("default")
        self.httpServer.add_file(f"default.zip",self.modfile.get_zip_file_profile_path("default"))
        Button(self,text="back to main menu",command=self.back).pack(pady=5,fill="x")
    def save_ddns(self):
        self.server.ddns = self.ddns.get()
        self.log("Save DDNS : -> ",self.ddns.get())
    def SyncData(self):
        self.server.controller(type=TypeCommu.TYPE_SYNC)
    def optionmenu_callback(self,choice,create:int=0):
        self.server.setProfile(choice)
        self.log("Change Profile:",choice)
        self.server.sha256 = self.modfile.getSha256(choice)
        self.httpServer.add_file(f"{choice}.zip",self.modfile.get_zip_file_profile_path(choice))
        if create == 0:
            self.modfile.changeModFolder(choice)
        self.modfile.setNowProfile(choice)
        self.modfile.updateNowProfile()
    def updatemod(self):
        self.modfile.updateProfile(self.var_select.get())        
    def deleteprofile(self):
        try:
            self.modfile.doUpdate = self.Reload_options
            self.modfile.remove_profile(self.dProfilename.get())
        except Exception as e:
            messagebox.showerror(title="Error",message=str(e))
    def showCreatebox(self):
        self.box3 = CreateBox(self.box4)
        self.box3.close1.bind("<Button-1>", self.__doCancelBox3)
        self.box3.create.bind("<Button-1>",self.createProfile)
        self.box3.pack(fill="x")
        self.butCreate.pack_forget()
       
    def __doCancelBox3(self, event):
        self.butCreate.pack(pady=5,fill="x")
        self.box3.pack_forget()
    def createProfile(self,event):
        if self.box3.name.get()=="":
            messagebox.showerror("Error","plz enter the name")
            self.__doCancelBox3(None)
        else:
            self.modfile.doUpdate = self.Reload_options_create
            self.modfile.createProfile(self.box3.name.get())
    def Reload_options_create(self):
        self.Reload_options(-1)
    def add_log(self,d:str):
        self.viewlog.insert(self.index_log,d)
        self.index_log+=1
        self.viewlog.yview_moveto(self.index_log)
    def startServer(self):
        self.server =Server()
        self.server.log = self.log
        self.text_ddns.set(self.server.ddns)
        self.server.start()

    def log(self,*x):
        self.add_log(" ".join(map(str,x)))
    def folder_dialog(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.var.set(folder_path)
            self.modfile.set_file_path(folder_path)
            messagebox.showinfo("Folder Selected", f"Folder '{folder_path}' selected successfully!")
            th = threading.Thread(target=self.startServer(),daemon=True)
            th.start()
        else:
            messagebox.showwarning("No Folder Selected", "No folder was selected.")
    def Reload_options(self,default=0):
        self.options = self.modfile.get_profiles()
        self.option['menu'].delete(0, 'end')  
        for option in self.options:
            self.option['menu'].add_command(label=option,command=_setit(self.var_select, option, self.optionmenu_callback))
            self.var_select.set(self.options[default])
        self.optionmenu_callback(self.var_select.get(),default)
    def back(self):
        self.stop()
        self.master.back()
    def stop(self):
        self.server.stop()
        self.httpServer.stop()
        