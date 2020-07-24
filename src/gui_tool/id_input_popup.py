from tkinter import Tk, Frame, Entry, Button

class PopUpWindow:
    def __init__(self):
        self.tags = []
        self.entries = []
        self.root = Tk()
        self.root.title("Enter ID and Class. If ID exists, can leave class empty")
        self.root.minsize(width=400, height=1)

        self.frame = Frame(self.root)
        self.id_field = Entry(self.frame)
        self.id_field.config(width=100)
        self.cls_field = Entry(self.frame)
        self.cls_field.config(width=100)
        self.confirm_button = Button(self.frame, text="Confirm", command=self.submit)

        self.id_field.grid(row=1, column=1)
        self.cls_field.grid(row=2, column=1)
        self.confirm_button.grid(row=3, column=1)
        self.frame.pack()

        self.id_inp = None
        self.cls_inp = None


    def submit(self):
        self.id_inp = self.id_field.get()
        self.cls_inp = self.cls_field.get()
        self.root.destroy()

    def run(self) -> str:
        self.root.mainloop()
        return self.id_inp, self.cls_inp
