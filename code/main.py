import tkinter as tk

def main():
    #Start app
    root = tk.Tk()
    root.title("Hello WOrlsd")
    label = tk.Label(root, text="Bye World").pack()
    root.mainloop()

if __name__ == "__main__":
    main()
