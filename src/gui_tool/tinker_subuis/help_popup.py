from tkinter import Tk, Frame, Label, BOTH, LEFT
class HelpPopup:
    def __init__(self, title: str, list_of_instructions: list):
        self.tags = []
        self.entries = []
        self.root = Tk()
        self.root.title(title)
        self.root.minsize(width=400, height=400)


        self.frame = Frame(self.root)
        self.frame.pack(fill=BOTH, expand=1, padx=20, pady=20)

        i = 0
        for instructions in list_of_instructions:
            Label(self.frame, text=instructions[0], anchor="nw", justify=LEFT).grid(sticky="nw", row=i, column=0, ipady=5, ipadx=10)
            Label(self.frame, text="\n".join(instructions[1:]), anchor="nw", justify=LEFT).grid(sticky="nw", row=i, column=1, ipady=3, ipadx=10)
            i += 1

        self.root.bind('<Escape>', lambda event: self.root.destroy())
        self.root.bind('<Return>', lambda event: self.root.destroy())
        self.root.after(1, lambda: self.root.focus_force())

    def run(self):
        self.root.mainloop()
