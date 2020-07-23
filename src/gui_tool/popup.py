from tkinter import Tk, Frame, Entry, Button

class PopUpWindow:
    def __init__(self, title: str):
        self.tags = []
        self.entries = []
        self.root = Tk()
        self.root.title(title)
        self.root.minsize(width=400, height=1)

        self.frame = Frame(self.root)
        self.entry_field = Entry(self.frame)
        self.entry_field.config(width=100)
        self.confirm_button = Button(self.frame, text="Confirm", command=self.submit)

        self.entry_field.grid(row=1, column=1, columnspan=2)
        self.confirm_button.grid(row=2, column=1)
        self.frame.pack()

        self.inp = None

    def submit(self):
        self.inp = self.entry_field.get()
        self.root.destroy()

    def run(self) -> str:
        self.root.mainloop()
        return self.inp
