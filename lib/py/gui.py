import Tkinter as tk
import ttk
import tkMessageBox
import psycopg2
import os
import sys


def center(widget, width, height):
    screen_width = widget.winfo_screenwidth()
    screen_height = widget.winfo_screenheight()

    x = screen_width / 2 - width / 2
    y = screen_height / 2 - height / 2

    widget.geometry('{}x{}+{}+{}'.format(width, height, x, y))


class EditableTreeview(ttk.Treeview):

    def __init__(self, parent, **kw):
        ttk.Treeview.__init__(self, parent, **kw)
        self.active_popup = None
        self.bind('<Double-Button-1>', self.on_double_click)
        self.bind('<Button-3>', self.on_right_click)

    def on_double_click(self, event):
        """
        Executed, when a row is double-clicked. Opens
        read-only EntryPopup above the item's column, so it is possible
        to select text
        """
        # what row and column was clicked on
        rowid = self.identify_row(event.y)
        column = self.identify_column(event.x)
        # col is 0 or 1 for parameter and argument
        col = int(column[-1:]) - 1
        # clicked row parent id
        # parent = self.parent(rowid)
        # do nothing if item is top-level
        # if parent == '':
        #    return
        # get column position info
        x, y, width, height = self.bbox(rowid, column)
        # y-axis offset
        pady = height // 2
        # place Entry popup properly
        # if col == 0:
        #     parameter = str(self.item(rowid)['values'][col])
        # else:
        #     parameter = str(self.item(rowid)['values'][0])
        #     argument = str(self.item(rowid)['values'][col])

        if 'new' in self.item(rowid)['tags']:
            self.active_popup = EntryPopup(self, rowid, column, '')
        else:
            self.active_popup = EntryPopup(self, rowid, column, str(self.item(rowid)['values'][col]))
        self.active_popup.place(x=x, y=y+pady, anchor=tk.W, width=width)

        print('col: {}'.format(column))
        print('width: {}'.format(width))

    # def set_save_callback(self, func):
    #     self.save_callback = func
    #
    # def set_delete_callback(self, func):
    #     self.delete_callback = func

    def on_right_click(self, event):
        rowid = self.identify_row(event.y)
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label='Delete', command=lambda: self.delete_row(rowid))
        menu.post(event.x_root, event.y_root)

    # def update_entry(self, row, col, val):
    #     print('update_entry:  row: {}  col: {}  val: {}'.format(row, col, val))
    #     self.save_callback(row, col, val)
    #
    def delete_row(self, rowid):
        print('delete_row: {}'.format(rowid))

    def on_entry_changed(self, row, col, old_val, new_val):
        print('on_entry_changed:  row: {}  col: {}  old_val: {}  new_vale: {}'.format(
            row, col, old_val, new_val
        ))


class EntryPopup(tk.Entry):

    def __init__(self, parent, row, col, cur_val, **kw):
        """
        If relwidth is set, then width is ignored
        """
        tk.Entry.__init__(self, parent, **kw)

        self.parent = parent
        self.row = row
        self.col = col
        self.cur_val = cur_val

        self.insert(0, cur_val)
        # self['state'] = 'readonly'
        # self['readonlybackground'] = 'white'
        self['selectbackground'] = '#1BA1E2'
        self['exportselection'] = False

        self.focus_force()
        self.bind("<Control-a>", self.select_all)
        self.bind('<FocusOut>', self.on_complete)
        self.bind('<Return>', self.on_complete)
        self.bind("<Escape>", lambda *ignore: self.destroy())

    def select_all(self, *ignore):
        """
        Set selection on the whole text
        """
        self.selection_range(0, 'end')
        # returns 'break' to interrupt default key-bindings
        return 'break'

    def on_complete(self, event):
        if self.cur_val != self.get():
            self.parent.on_entry_changed(self.row, self.col, self.cur_val, self.get())
        self.destroy()
        # if self.is_new:
        #     self.parent.insert_entry()
        # else:
        #     print('old: {}  new: {}'.format(type(self.old_val), type(self.get())))
        #     print('old: {}  new: {}'.format(self.old_val, self.get()))
        #     self.parent.update_entry(self.get())


class CardFrame(tk.Frame):

    def __init__(self, *args):
        tk.Frame.__init__(self, *args)
        self.cards = {}
        self.active_card = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def add(self, card_name, frame):
        assert len(self.cards) < 2, self.cards
        assert card_name not in self.cards
        self.cards[card_name] = frame
        if not self.active_card:
            frame.grid(row=0, column=0, sticky='nsew')
            self.active_card = (card_name, frame)

    def show(self, card_name):
        assert card_name in self.cards
        if self.active_card[0] == card_name:
            return
        self.active_card[1].grid_remove()
        card = self.cards[card_name]
        card.grid(row=0, column=0, sticky='nsew')
        self.active_card = (card_name, card)
