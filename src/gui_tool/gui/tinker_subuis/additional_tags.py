from tkinter import Tk, Frame, Entry, Button
from typing import List


class TagField:
    def __init__(self, master):
        self.key_field = Entry(master)
        self.value_field = Entry(master)

class AdditionalTagWindow:

    def __init__(self):
        self.tags = []
        self.entries = []
        self.root = Tk()
        self.root.title("Additional Tags")
        self.root.minsize(width=400, height=400)

        self.frame = Frame(self.root)
        self.add_entry_button = Button(self.frame, text="New Entry", command=self.add_entry)
        self.confirm_button = Button(self.frame, text="Confirm", command=self.submit)
        self.cancel_button = Button(self.frame, text="Cancel", command=self.root.destroy)

    def add_entry(self):
        tag = TagField(self.frame)
        self.entries.append(tag)

        self.update_frame()

    def submit(self):
        for tag in self.entries:
            if tag.key_field.get() != "" and tag.value_field.get() != "":
                self.tags.append((tag.key_field.get(), tag.value_field.get()))
        self.root.destroy()

    def update_frame(self):
        for i, tag in enumerate(self.entries):
            tag.key_field.grid(row=i, column=0)
            tag.value_field.grid(row=i, column=1)

        n = len(self.entries)

        self.add_entry_button.grid(row=n, column=0)
        self.confirm_button.grid(row=n, column=1)
        self.cancel_button.grid(row=n, column=2)

        self.frame.grid(row=0, column=0)
        self.frame.tkraise()


    def get_user_tags(self) -> List:
        self.add_entry()
        self.root.mainloop()

        return self.tags
