from tkinter import Tk, Frame, Button, Label

class ButtonPopup:
    def __init__(self, title, msg, options):
        self.options = options
        self.tags = []
        self.entries = []
        self.root = Tk()
        self.root.title(title)
        self.root.minsize(width=400, height=1)

        self.frame = Frame(self.root)
        self.msg = Label(self.frame, text=msg)

        self.msg.grid(row=1, column=1)
        for i, text in enumerate(options):
            btn = Button(self.frame, text=text, command=lambda i=i: self.submit(i))
            btn.grid(row=2, column=i+1)
        self.frame.pack()

        self.inp = None
        self.root.after(1, lambda: self.root.focus_force())
        self.root.bind('<Escape>', lambda event: self.root.destroy())

    def submit(self, i):
        self.inp = self.options[i]
        self.root.destroy()

    def run(self) -> str:
        self.root.mainloop()
        return self.inp
