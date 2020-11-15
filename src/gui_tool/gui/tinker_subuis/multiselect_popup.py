from tkinter import Tk, Frame, Entry, Button, Checkbutton, StringVar
from tkinter import END
from .cashe_manager import ListCacheManager

class MultiSelectPopup:
    def __init__(self, title, cache_name, starting_selected=None, cache_amount=100):
        self.tags = []
        self.entries = []
        self.root = Tk()
        self.root.title(title)
        self.root.minsize(width=400, height=1)

        self.options_frame = Frame(self.root)
        self.button_frame = Frame(self.root)

        self.cm = ListCacheManager(cache_name, cache_amount)
        options = self.cm.retrieve()

        if starting_selected is None:
            starting_selected = []
        for val in starting_selected:
            if val not in options:
                options.append(val)

        self.vars = []
        for val in options:
            self.__add_option(val, val in starting_selected)

        self.inp_field = Entry(self.button_frame)
        self.inp_field.config(width=100)
        self.inp_field.pack()

        self.confirm_button = Button(self.button_frame, text="Confirm", command=self.submit)
        self.confirm_button.pack()
        self.cancel_button = Button(self.button_frame, text="Cancel", command=lambda: self.root.destroy())
        self.cancel_button.pack()

        self.options_frame.pack()
        self.button_frame.pack()
        self.inp_field.focus_set()

        self.inp = None
        self.inp_field.bind('<Return>', lambda event: self.__add_input())
        self.root.bind('<Escape>', lambda event: self.root.destroy())
        self.root.after(1, lambda: self.root.focus_force())

    def __add_input(self):
        text = self.inp_field.get().strip()
        self.inp_field.delete(0, END)
        self.inp_field.insert(END, "")

        if text == "":
            return
        if text in self.cm.retrieve():
            return

        self.__add_option(text)
        self.vars[-1].set(text)
        self.cm.insert(text)
        print("{0} inserted into cache".format(text))

    def __add_option(self, text, selected=False):
        if selected:
            var = StringVar(value=text)
        else:
            var = StringVar(value="")
        button = Checkbutton(self.options_frame, text=text, var=var, onvalue=text, offvalue="")
        button.pack()
        self.vars.append(var)

    def submit(self):
        self.inp = []
        for var in self.vars:
            value = var.get()
            if value:
                self.inp.append(value)
        self.root.destroy()

    def run(self) -> str:
        self.root.mainloop()
        return self.inp