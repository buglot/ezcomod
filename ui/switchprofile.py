import threading
from tkinter import Button,Frame,Label,Listbox,StringVar,messagebox,OptionMenu,_setit,Scrollbar

from utils import MangagerProfile
from ui.component.createbox import CreateBox
class Switch(Frame):
    __index:int = 0
    def __init__(self, master = None):
        super().__init__(master)
        self.master = master
        self.pack(fill="x",padx=10)
        self.box1 = Frame(self)
        self.box1.pack()
        self.modfile = MangagerProfile()
        self.modfile.log = self.log
        Label(self.box1,text="Switch Profile").pack(side="left")
        self.profile_op = StringVar()
        self.Option_Profile = OptionMenu(self.box1,self.profile_op,*self.modfile.get_profiles(),command=self.optionmenu_callback)
        self.Option_Profile.pack(fill="x",expand=True)
        
        self.profile_op.set(self.modfile.getNowProfile())
        self.box2 = Frame(self)
        self.box2.pack(fill="x")
        Button(self.box2,text="UpdateMod",command=self.modUpdate).pack(fill="x",pady=4)
        self.c = Button(self.box2,text="create Profile",command=self.showCreate)
        self.c.pack(fill="x",pady=4)
        Button(self,text="Delete Profile",command=self.deleteProfile).pack(fill="x",pady=4)

        self.box3 = Frame(self)
        self.box3.pack(fill="both",anchor="s")
        self.sco = Scrollbar(self.box3)
        self.sco.pack(side="right",fill="y")
        self.Viewlog = Listbox(self.box3,yscrollcommand=self.sco.set)
        self.sco.config(command=self.Viewlog.yview)
        self.Viewlog.pack(side="left",fill="both",expand=1)
        self.modfile.checkProfileAll()
        Button(self,text="Open Mod Folder ",command=self.modfile.OpenLocalMod).pack(fill="x",pady=4)
        Button(self,text="Open Profile Mod Folder",command=self.OpenFolderProfile).pack(fill="x",pady=4)
        Button(self,text="back to main menu",command=self.master.back).pack(fill="x",pady=4)
    def OpenFolderProfile(self):
        self.modfile.OpenLocalModeProfile(self.nowProfile())
    def nowProfile(self):
        return self.profile_op.get()
    def showCreate(self):
        self.c.pack_forget()
        self.creat = CreateBox(self.box2)
        self.creat.pack()
        self.creat.close1.bind("<Button-1>", self.closeCrate)
        self.creat.create.bind("<Button-1>",self.createProfile)
    def closeCrate(self,event):
        self.creat.pack_forget()
        self.c.pack(fill="x")
    def createProfile(self,event):
        if self.creat.name.get()=="":
            messagebox.showerror("Error","plz enter the name")
            self.__doCancelBox3(None)
        else:
            self.modfile.doUpdate = self.Reload_options_create
            self.modfile.createProfile(self.creat.name.get())
    def Reload_options(self,default=0):
        self.options = self.modfile.get_profiles()
        self.Option_Profile['menu'].delete(0, 'end')  
        for option in self.options:
            self.Option_Profile['menu'].add_command(label=option,command=_setit(self.profile_op, option, self.optionmenu_callback))
            self.profile_op.set(self.options[default])
        self.optionmenu_callback(self.profile_op.get(),default)
    def Reload_options_create(self):
        self.Reload_options(-1)
    def optionmenu_callback(self,choice:str,create=0):
        self.log("Change Profile:",choice)
        th =threading.Thread(target=self.doT,args=[choice,create])
        th.start()
    def doT(self,choice:str,create=0):
        if create == 0:
            self.modfile.changeModFolder(choice)
        self.modfile.setNowProfile(choice)
        self.modfile.updateNowProfile()
    def log(self,*x):
        self.Viewlog.insert(self.__index," ".join(map(str,x)))
        self.__index+=1
        self.Viewlog.yview_moveto(self.__index)
    def modUpdate(self):
        self.modfile.updateProfile(self.profile_op.get())
    def deleteProfile(self):
        try:
            self.modfile.doUpdate = self.Reload_options
            self.modfile.remove_profile(self.profile_op.get())
        except Exception as e:
            messagebox.showerror(title="erorr",message=str(e))
        
        
        