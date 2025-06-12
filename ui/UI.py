from tkinter import Tk, Frame, Button, Label, Entry, messagebox
from ui.headerModUI import Headerframe
from ui.clientframe import ClientFrame
from ui.switchprofile import Switch
class BaseRoot(Tk):
    def __init__(self, screenName = None, baseName = None, className = "Tk", useTk = True, sync = False, use = None):
        super().__init__(screenName, baseName, className, useTk, sync, use)
    def back(self):
        pass
class UI:
    def __init__(self, root):
        self.root = root
        self.root.back = self.back
        self.root.title("Simple UI")
        self.root.geometry("400x500")
        self.frame = Frame(self.root)
        self.frame.pack(padx=10, pady=10)
        self.button_h = Button(self.frame, text="HeaderMod",command=self.onClick_h)
        self.button_c = Button(self.frame, text="clientSync",command=self.onClick_c)
        self.button_s = Button(self.frame, text="Switch Profile",command=self.onClick_s)
        self.button_h.pack()
        self.button_c.pack()
        self.button_s.pack()
    def onClick_s(self):
        self.frame.pack_forget()
        self.switch = Switch(self.root)
    def onClick_c(self):
        self.frame.pack_forget()
        self.client_frame = ClientFrame(self.root)
    def onClick_h(self):
        self.frame.pack_forget()
        self.header_frame = Headerframe(self.root)
    def back(self):
        try:
            self.frame.pack()
        except Exception as e:
            print(e)
        try:
            self.header_frame.destroy()
        except Exception as e:
            print(e)
        
        try:
            self.client_frame.destroy()
        except Exception as e:
            print(e)
        try:
            self.switch.destroy()
        except Exception as e:
            print(e)
