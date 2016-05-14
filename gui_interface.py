def tk_display_text(text):
    """
    Displays string using a tkinter message with fixed-width font. Pressing 'q' will close the window.
    :param text: string to be shown, presumably nest(s)
    :return: None
    """
    from Tkinter import Tk, Message, TOP
    master = Tk()
    w = Message(master, text=text, width=2000)
    w.config(font='TkFixedFont')
    w.pack()
    def destroymaster(self):
        master.destroy()
    master.bind('q',destroymaster)
    master.mainloop()
