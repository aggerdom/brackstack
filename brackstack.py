# coding: utf-8
__author__ = 'Alex'

def get_nesting_depth(s, checked="()[]{}"):
    """
    :param s: string (presumably code) to be checked
    :param checked: A string consisting of pairs of characters to check for
    :return: the number of levels deep each character is nested
    """
    # Dictionary that matches left and right delimiters
    LeftRight = {l:r for (l,r) in zip(checked[::2], checked[1::2])}
    # How deeply nested each character is
    depths = []
    # Stack that holds the last encountered left delimiter
    leftStack = []
    curDepth = 0
    nextRight = None # Don't count right characters until a left character is encountered
    is_left = lambda c: c in LeftRight.keys()
    get_next_right = lambda c: LeftRight[c]
    for c in s:
        if is_left(c):
            depths.append(curDepth) # add the left delimiter at the current level
            leftStack.append(c) # push it onto the stack of characters whos' scope we're in
            curDepth += 1
            nextRight = get_next_right(c) # update which character we're searching for
        elif c == nextRight:
            curDepth -= 1 # decrease the level to match it with the last left delimiter
            depths.append(curDepth)
            leftStack.pop(-1) # remove the left delimiter that has been matched
            if len(leftStack) == 0:
                nextRight = None # reset the sentinal for the right sentinal to match nothing
            else:
                nextRight = get_next_right( leftStack[-1] )  # get the match for the last active left bracket
        else:
            depths.append(curDepth)
    return depths

def nestprint(s, depths, nest_downwards=False):
    """
    :param s: String to be (un)nested
    :param depths: Level to each character will be printed at. Presumably calculated by using get_nesting_depth(s).
    :param nest_downwards: If true, higher levels of nesting will print below the baseline (level 0)."""
    levels = [[] for _ in range(max(depths)+1)]
    for lvl,c in zip(depths,s):
        for i in range(len(levels)):
            if lvl == i:
                levels[i].append(c)
            else:
                levels[i].append(' ')
    levels = [''.join(lvl) for lvl in levels]
    if nest_downwards:
        return '\n'.join([lvl for lvl in levels])
    else:
        return '\n'.join([lvl for lvl in levels[::-1]])

def stackbrack(s):
    """
    :param s: String to be nested
    :return: A multiline string with one line per level
    """
    return nestprint(s, get_nesting_depth(s))

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

def demo():
    s = ")a(a)(b[c]],{sum(range(max(array([1,2,3],[4,5,5]))))})"
    tk_display_text(stackbrack(s))
    print(stackbrack(s))

if __name__ == '__main__':
    demo()

# lvls = get_nesting_depth(s)
# print nestprint(s, lvls)
# print nestprint(s, lvls,nest_downwards=True)