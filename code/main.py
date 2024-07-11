from colors import *
import helpers

import tkinter as tk
from functools import partial


## TODO:
# -[ ]- A good theme switching system

root = None

# 0: Dark, 1: Light
mode = 0

def setup():
    root.title("Hello WOrlsd")
    root.geometry("800x600")
    root.configure(
        background=root_bg[mode]
    )
    root.maxsize(800, 600)
    root.minsize(800, 600)

def mode_button():
    global mode
    mode = 1-mode
    setup()

uvar = None
pvar = None

def validate_login():
    name = uvar.get()
    uvar.set("")
    pwd = pvar.get()
    pvar.set("")
    ##Validation Logic
    print(name, pwd)
    
def main():
    #Setup Window
    global root
    root = tk.Tk()
    setup()
    
    #Setup widgets
    # tk.Button(root, text="M",
    #     command= mode_button
    # ).grid(row=0, column=200)

    global uvar
    global pvar
    uvar = tk.StringVar()
    pvar = tk.StringVar()

    tk.Label(root, text="Username").place(relx=0.01, rely=0.02)
    username = tk.Entry(root, textvariable=uvar).place(relx=0.1, rely=0.02)

    tk.Label(root, text="Password").place(relx=0.01, rely=0.08)
    passwd = tk.Entry(root, show="*", textvariable=pvar).place(relx=0.1, rely=0.08)

    tk.Button(root, text="Submit", command=validate_login).place(relx=0.12, rely=0.16)
    
    root.mainloop()

if __name__ == "__main__":
    main()
