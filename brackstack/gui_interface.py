from sys import version_info
if version_info[0] < 3:
    from Tkinter import Tk, Message, TOP, Toplevel
elif version_info[0] >= 3:
    from tkinter import Tk, Message, TOP, Toplevel

class App:
    """docstring for App"""
    def __init__(self, arg):
        self.root = Tk()
        self.root.withdraw()
        self.toplevel = None
        self.message = None
    def get_clipboard_text(self):
        clipboard_text = self.root.clipboard_get()
        return clipboard_text
    def display_text(self,text):
        self.create_toplevel()
        self.message = Message(self.toplevel, text=text, width=2000)
        self.message.config(font='TkFixedFont')
        self.toplevel.bind('q',self.destroy_toplevel)
    def create_toplevel(self):
        self.toplevel = Toplevel(self.root)
    def destroy_toplevel(self):
        self.toplevel.destroy()
        self.toplevel = None




        

def tk_display_text(text,master=None):
    """
    Displays string using a tkinter message with fixed-width font. Pressing 'q' will close the window.
    :param text: string to be shown, presumably nest(s)
    :return: None
    """
    if master is None:
        master = Tk()
    else:
        master = master
    w = Message(master, text=text, width=2000)
    w.config(font='TkFixedFont')
    w.pack()
    def destroymaster(self):
        master.destroy()
    master.bind('q',destroymaster)
    master.mainloop()
