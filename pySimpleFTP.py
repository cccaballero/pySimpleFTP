import tkinter
from tkinter import Tk
from tkinter import Menu
from tkinter.filedialog import askdirectory
from tkinter import Button
from tkinter import Entry
from tkinter import Label
from tkinter import mainloop
from tkinter import scrolledtext
from tkinter import messagebox

from pyftpdlib import servers
from pyftpdlib.servers import ThreadedFTPServer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.authorizers import DummyAuthorizer

import threading
import sys
import logging
import tempfile
import uuid
import os

class ftp_server(ThreadedFTPServer):
    def __init__(self, port, exposed_dir, username='', password=''):

        self.exposed_dir = exposed_dir

        authorizer = DummyAuthorizer()
        if username:
            authorizer.add_user(username, password, '.', perm=('elradfmwM'))
        else:
            authorizer.add_anonymous(exposed_dir, perm=('elradfmwM'))

        address = ('0.0.0.0', port)
        handler = FTPHandler
        handler.authorizer = authorizer
        ThreadedFTPServer.__init__(self, address, handler)

    def run(self):
        self.serve_forever()

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.close_all()

class TextHandler(logging.Handler):
    # This class allows you to log to a Tkinter Text or ScrolledText widget
    # Adapted from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06

    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text.configure(state='normal')
            self.text.insert(tkinter.END, msg + '\n')
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(tkinter.END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)


def get_folder():
    Tk().withdraw()
    foldername = askdirectory()
    return foldername

ftp = None

def disable_entries():
    port_entry.config(state='disabled')
    user_entry.config(state='disabled')
    password_entry.config(state='disabled')

def enable_entries():
    port_entry.config(state='normal')
    user_entry.config(state='normal')
    password_entry.config(state='normal')

def start_ftp():
    global ftp
    exposed_dir = get_folder()
    try:
        ftp = ftp_server(port_entry.get().strip(), exposed_dir, user_entry.get().strip(), password_entry.get().strip())
        ftp.start()
    except Exception as e:
        messagebox.showinfo('Error', e)
        return
    button.config(text='Stop', command=stop_ftp)
    disable_entries()

def stop_ftp():
    global ftp
    ftp.stop()
    ftp = None
    button.config(text='Start', command=start_ftp)
    enable_entries()

def on_closing():
    if ftp:
        ftp.stop()
    master.destroy()
    sys.exit()

def on_about():
    messagebox.showinfo('About', "SimpleFTP\nAn uncomplicated FTP server for testing propouses.")

if __name__ == '__main__':

    master = Tk()
    master.title('Simple FTP')

    menubar = Menu()

    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="About...", command=on_about)

    menubar.add_cascade(label="Help", menu=helpmenu)

    Label(master, text='Port:').grid(row=0)
    port_entry = Entry(master)
    port_entry.insert(0, '21')
    port_entry.grid(row=0, column=1)

    Label(master, text='User:').grid(row=1)
    user_entry = Entry(master)
    user_entry.grid(row=1, column=1)

    Label(master, text='Password:').grid(row=2)
    password_entry = Entry(master)
    password_entry.grid(row=2, column=1)

    button = Button(master, text='Start', command=start_ftp)
    button.grid(row=3)

    # Add text widget to display logging info
    st = scrolledtext.ScrolledText(state='disabled')
    st.configure(font='TkFixedFont')
    st.grid(column=0, row=4, sticky='w', columnspan=4)

    # Create textLogger
    text_handler = TextHandler(st)

    # Logging configuration
    logging.basicConfig(filename=os.path.join(tempfile.gettempdir(), str(uuid.uuid4())),
        level=logging.INFO)

    # Add the handler to logger
    logger = logging.getLogger()
    logger.addHandler(text_handler)
    
    master.protocol('WM_DELETE_WINDOW', on_closing)

    master.config(menu=menubar)

    mainloop()

    

