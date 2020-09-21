from tkinter import Tk, Frame, Entry, Button

class TextPopup:
    def __init__(self, title):
        self.tags = []
        self.entries = []
        self.root = Tk()
        self.root.title(title)
        self.root.minsize(width=400, height=1)

        self.frame = Frame(self.root)
        self.field = Entry(self.frame)
        self.field.config(width=100)
        self.confirm_button = Button(self.frame, text="Confirm", command=self.submit)

        self.field.grid(row=1, column=1)
        self.confirm_button.grid(row=3, column=1)
        self.frame.pack()

        self.field.focus_set()
        self.field.bind('<Return>', lambda event: self.confirm_button.invoke())

        self.inp = None
        self.root.after(1, lambda: self.root.focus_force())
        self.root.bind('<Escape>', lambda event: self.root.destroy())

    def submit(self):
        self.inp = self.field.get()
        self.root.destroy()

    def run(self) -> str:
        self.root.mainloop()
        return self.inp
