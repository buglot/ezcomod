from tkinter import Button,Frame,Label,Listbox,StringVar,messagebox,OptionMenu
from utils import MangagerProfile
class Switch(Frame):
    def __init__(self, master = None):
        super().__init__(master)
        self.master = master
        self.pack(fill="x",padx=10)
        self.box1 = Frame(self)
        self.box1.pack()
        self.modfile = MangagerProfile()
        Label(self.box1,text="Switch Profile").pack(side="left")
        self.profile_op = StringVar()
        self.Option_Profile = OptionMenu(self.box1,self.profile_op,*self.modfile.get_profiles())
        self.modfile.checkProfileAll()
        self.profile_op.set(self.modfile.getNowProfile())
        