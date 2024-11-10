import mysql.connector as sqltor
from tkinter import *
from PIL import ImageTk, Image

#Osoi > Books
#+--------+-------------+------+-----+---------+-------+
#| Field  | Type        | Null | Key | Default | Extra |
#+--------+-------------+------+-----+---------+-------+
#| BookID | int(11)     | NO   | PRI | NULL    |       |
#| Title  | varchar(30) | YES  |     | NULL    |       |
#| Author | varchar(30) | YES  |     | NULL    |       |
#| Year   | int(11)     | YES  |     | NULL    |       |
#+--------+-------------+------+-----+---------+-------+

def get_all_books(cursor):
    cursor.execute("select * from Books;")
    return cursor.fetchall()

def add_book(con, cursor, bookid, title, author, year):
    command = "insert into Books Values(" + bookid + ',"' + title + '","' + author + '",' + year + ')'  
    cursor.execute(command)
    con.commit()

def seeBooksWin(con, cursor):
    root = Tk()
    root.title("See Books")
    root.geometry("800x600")
    root.configure(bg="#d5c4a1")
    root.resizable(0, 0)
    
    books = get_all_books(cursor)
    rows = len(books)

    heading = Label(root, fg='#fbfafa', bg='#7c6f64', text='See Books', font=('Helvetica', 25), padx=70, pady=20)
    heading.place(relx=0.33, rely=0.1)

    labelFrame = Frame(root,bg='#d5c4a1')
    labelFrame.place(relx=0.1,rely=0.4,relwidth=0.8,relheight=0.4)

    Label(labelFrame, width=20, text='Book ID').grid(row=0, column=0)
    Label(labelFrame, width=20, text='Title').grid(row=0, column=1)
    Label(labelFrame, width=20, text='Author').grid(row=0, column=2)
    Label(labelFrame, width=20, text='Year').grid(row=0, column=3)

    for i in range(rows):
        for j in range(4):
            e = Label(labelFrame,width=20, text=books[i][j], bg='#928374')
            e.grid(row=i+1, column=j)


def registerBooks(con, cursor, bid, tit, aut, yea):
    bookid = str(int(bid.get()))
    title = tit.get()
    author = aut.get()
    year = yea.get()
    bid.delete(0, END)
    tit.delete(0, END)
    aut.delete(0, END)
    yea.delete(0, END)
    add_book(con, cursor, bookid, title, author, year)

def addBooksWin(con, cursor):
    root = Tk()
    root.title("Add Books")
    root.geometry("800x600")
    root.configure(bg="#d5c4a1")
    root.resizable(0, 0)
    
    heading = Label(root, fg='#fbfafa', bg='#7c6f64', text='AddBooks', font=('Helvetica', 25), padx=70, pady=20)
    heading.place(relx=0.33, rely=0.1)

    
    labelFrame = Frame(root,bg='#d5c4a1')
    labelFrame.place(relx=0.1,rely=0.4,relwidth=0.8,relheight=0.4)

    # Book ID
    lb1 = Label(labelFrame,text="Book ID : ", bg='#d5c4a1', fg='#282828')
    lb1.place(relx=0.05,rely=0.2, relheight=0.08)
        
    bookInfo1 = Entry(labelFrame, bg='#928374')
    bookInfo1.place(relx=0.3,rely=0.2, relwidth=0.62, relheight=0.08)
        
    # Title
    lb2 = Label(labelFrame,text="Title : ", bg='#d5c4a1', fg='#282828')
    lb2.place(relx=0.05,rely=0.35, relheight=0.08)
        
    bookInfo2 = Entry(labelFrame, bg='#928374')
    bookInfo2.place(relx=0.3,rely=0.35, relwidth=0.62, relheight=0.08)
        
    # Book Author
    lb3 = Label(labelFrame,text="Author : ", bg='#d5c4a1', fg='#282828')
    lb3.place(relx=0.05,rely=0.50, relheight=0.08)

    bookInfo3 = Entry(labelFrame, bg='#928374')
    bookInfo3.place(relx=0.3,rely=0.50, relwidth=0.62, relheight=0.08)

    # Year
    lb4 = Label(labelFrame,text="Year : ", bg='#d5c4a1', fg='#282828')
    lb4.place(relx=0.05,rely=0.65, relheight=0.08)
        
    bookInfo4 = Entry(labelFrame, bg='#928374')
    bookInfo4.place(relx=0.3,rely=0.65, relwidth=0.62, relheight=0.08)

    #Submit Button
    SubmitBtn = Button(root,text="SUBMIT",bg='#d5c4a1', fg='#1d2021',command=lambda : registerBooks(con, cursor, bookInfo1, bookInfo2, bookInfo3, bookInfo4))
    SubmitBtn.place(relx=0.43,rely=0.9, relwidth=0.18,relheight=0.08)
    
  

def main():
    # IMPORTANT: Change the user and passwd (and\or collation if problems) vvv
    con = sqltor.connect(host="localhost", user="3curtain", passwd="3curtain", database="Osoi", collation='utf8mb4_general_ci')
    if not con.is_connected():
        print('Error in Connection')
        return
    cursor = con.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS Books(BookID int primary key, Title varchar(30), Author varchar(30), Year int);")
    con.commit
    
    root = Tk()
    root.title("osoi")
    root.geometry("1280x720")
    
    bg = ImageTk.PhotoImage(Image.open("main_page.jpg"))
    # Create Canvas 
    canvas1 = Canvas( root, width = 1280,height = 720) 
  
    canvas1.pack(fill = "both", expand = True) 
  
    # Display image 
    canvas1.create_image( 0, 0, image = bg, anchor = "nw") 

    seeBookPhoto = ImageTk.PhotoImage(Image.open("seeBooksBtn.png"))
    seeBookBtn = Label(root, image=seeBookPhoto, borderwidth=0, highlightthickness=0)
    seeBookBtn.place(relx=0.39,rely=0.39)
    seeBookBtn.bind('<Button-1>', lambda ev: seeBooksWin(con, cursor))
    
    addBookPhoto = ImageTk.PhotoImage(Image.open("addBooksBtn.png"))
    addBookBtn = Label(root, image=addBookPhoto, borderwidth=0, highlightthickness=0)
    addBookBtn.place(relx=0.39,rely=0.56)
    addBookBtn.bind('<Button-1>', lambda ev: addBooksWin(con,cursor))
    
    root.mainloop()

if __name__ == "__main__":
    main()
