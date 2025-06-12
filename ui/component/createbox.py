from tkinter import Frame,Label,Entry,Button

class CreateBox(Frame):
    close1:Button
    def __init__(self, master = None):
        super().__init__(master)
        self.Cancel = lambda: None
        self.master = master
        center = Frame(self)
        center.pack(anchor="center")
        Label(center,text="Profile name: ").pack(side="left",padx=4)
        self.name = Entry(center)
        self.name.pack(side="left",padx=4)
        self.create = Button(center,text="Create")
        self.create.pack(side="left")
        self.close1 = Button(center,text="Cancel",command=self.Cancel)
        self.close1.pack(side="left")

