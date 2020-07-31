from tkinter import Tk, Frame, Label, BOTH, LEFT
class LabelPopup:
    def __init__(self, title: str, text: str):
        self.tags = []
        self.entries = []
        self.root = Tk()
        self.root.title(title)
        self.root.minsize(width=800, height=400)


        self.frame = Frame(self.root)
        self.frame.pack(fill=BOTH, expand=1, padx=20, pady=20)
        self.label = Label(self.frame, text=text, anchor="e", justify=LEFT)
        self.label.place(x=0, y=0)

    def run(self):
        self.root.mainloop()
