from tkinter import Tk, Frame, Entry, Button
from tkinter import END
from .cashe_manager import ListCacheManager
class SelectPopup:
    def __init__(self, title, cache_name, cache_amount, defaults):
        self.tags = []
        self.entries = []
        self.root = Tk()
        self.root.title(title)
        self.root.minsize(width=400, height=1)

        self.frame = Frame(self.root)

        self.cm = ListCacheManager(cache_name, max(cache_amount - len(defaults), 0))
        self.defaults = defaults
        options = defaults + [v for v in self.cm.retrieve() if v not in defaults]
        i = 0
        for i, val in enumerate(options):
            button = Button(self.frame,  text=val, command=self.__get_update_inp_field_func(val))
            button.grid(row=i//2, column=i%2)

        self.inp_field = Entry(self.frame)
        self.inp_field.config(width=100)
        self.inp_field.grid(row=i//2+1, column=1)

        self.confirm_button = Button(self.frame, text="Confirm", command=self.submit)
        self.confirm_button.grid(row=i//2+2, column=1)
        self.cancel_button = Button(self.frame, text="Cancel", command=lambda event: self.root.destroy())
        self.cancel_button.grid(row=i//2+2, column=2)

        self.frame.pack()
        self.inp_field.focus_set()

        self.inp = None
        self.inp_field.bind('<Return>', lambda event: self.confirm_button.invoke())
        self.root.bind('<Escape>', lambda event: self.root.destroy())
        self.root.after(1, lambda: self.root.focus_force())

    def __get_update_inp_field_func(self, value):
        this = self
        def ret():
            this.__update_inp_field(value)
            this.submit()
        return ret

    def __update_inp_field(self, value):
        self.inp_field.delete(0, END)
        self.inp_field.insert(0, str(value))

    def submit(self):
        self.inp = self.inp_field.get()
        if self.inp not in self.defaults:
            self.cm.insert(self.inp)
        self.root.destroy()

    def run(self) -> str:
        self.root.mainloop()
        return self.inp
