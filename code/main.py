import mysql.connector as sqltor
from tkinter import *
from PIL import ImageTk, Image

#Osoi > Users
#+-------+-------------+------+-----+---------+-------+
#| Field | Type        | Null | Key | Default | Extra |
#+-------+-------------+------+-----+---------+-------+
#| UID   | int(11)     | NO   | PRI | NULL    |       |
#| UName | varchar(30) | YES  |     | NULL    |       |
#| pwd   | int(11)     | YES  |     | NULL    |       |
#+-------+-------------+------+-----+---------+-------+

#Osoi > Books
#+--------+-------------+------+-----+---------+-------+
#| Field  | Type        | Null | Key | Default | Extra |
#+--------+-------------+------+-----+---------+-------+
#| BookID | int(11)     | NO   | PRI | NULL    |       |
#| Title  | varchar(30) | YES  |     | NULL    |       |
#| Author | varchar(30) | YES  |     | NULL    |       |
#| Year   | int(11)     | YES  |     | NULL    |       |
#| IssBy  | int(11)     | YES  |     | NULL    |       |
#+--------+-------------+------+-----+---------+-------+

#User : (UId, UName)

colors = {
    'lbg': '#d5c4a1',
    'dbg': '#7c6f64',
}

def execommit(con, cursor, command):
    cursor.execute(command)
    con.commit()

def get_all_books(cursor):
    cursor.execute("select * from Books;")
    return cursor.fetchall()

def add_book(con, cursor, title, author, year):
    cursor.execute("SELECT MAX(BookID) from Books;")
    q = cursor.fetchall();
    bookid = 0
    if len(q) > 0:
        bookid = q[0][0] + 1
    
    command = "insert into Books Values(" + str(bookid) + ',"' + title + '","' + author + '",' + year + ', NULL)'  
    execommit(con, cursor, command)

def remove_book(con, cursor, bookid):
    execommit(con, cursor, "delete from Books where BookID=" + str(bookid)+";")
    
# TODO: encryption
# length probelm
# TODO: disallow '!' in uname and pwd
def encrypt_pwd(uname, pwd) -> int:
    """
        This implements djb2
    """
    
    ct = ''

    pt = uname + '!' + pwd
    
    hash = 5381;

    for c in pt:
        hash = ((hash << 1) + hash) + ord(c)
    
    return hash

def register_user(con, cursor, uname, pwd):
    cursor.execute("SELECT MAX(UID) from Users;")
    uid = cursor.fetchall()[0][0] + 1
    hpwd = encrypt_pwd(uname, pwd)
    cursor.execute("INSERT INTO Users Values(" + str(uid) + ',"' + uname + '",' + str(hpwd) + ')')
    con.commit()


def check_login(con, cursor, uname, pwd) -> (bool, (int, str)):
    cursor.execute("SELECT UID, pwd from Users where UName='" + uname + "'")
    q = cursor.fetchall()
    if q == []:
        print("Username not found!")
        return (False, None)

    uid,hash = q[0]

    hpwd = hash_pwd(uname, pwd)

    if hash == hpwd:
        print("Welcome, ", uname, sep='')
        return (True, (uid, uname))
    else:
        print("Incorrect password!")
        return (False, None)


def is_issued(con, cursor, user, bookid) -> bool:
    cursor.execute("select 1 from Books where IssBy is NULL and BookID=" + str(bookid))
    #returns [] if IssBy is not NUll, and [(1,)] when it is.
    return True if len(cursor.fetchall()) == 0 else False

def issued_by(con, cursor, user, bookid) -> bool:
    cursor.execute("select 1 from Books where IssBy=" + str(user[0]) + " and BookID=" + str(bookid))
    #returns [] if IssBy is userid, and [(1,)] when it isnt.
    return True if len(cursor.fetchall()) != 0 else False

def issue_book(con, cursor, user, bookid) -> bool:
    """
        True if issued succesfully.
        False if book is already issued.
    """
    if is_issued(con, cursor, user, bookid):
        print("This book is already issued!")
        return False

    execommit(con, cursor, "UPDATE Books SET IssBy=" + str(user[0]) + " WHERE BookID=" + str(bookid) + ";")

def return_book(con, cursor, user, bookid) -> bool:
    if not issued_by(con, cursor, user, bookid):
        print("Not issued by the user!")
        return False
    execommit(con, cursor, "UPDATE Books SET IssBy=NULL WHERE BookID=" + str(bookid) + ";")
    return True

# TODO: cosmetics
# TODO: maybe diff scheme for admin
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
    labelFrame.place(relx=0.1,rely=0.4,relwidth=1,relheight=0.4)

    table = [
        ['Book ID', 12],
        ['Title', 20],
        ['Author', 12],
        ['Year', 12],
        ['Issued By', 12]
    ]

    for i in range(len(table)):
      Label(labelFrame, width=table[i][1], text=table[i][0]).grid(row=0, column=i)


    for i in range(rows):
        for j in range(5):
            e = Label(labelFrame,width = table[j][1], text=books[i][j], bg='#928374')
            e.grid(row=i+1, column=j)


def registerBooks(con, cursor, tit, aut, yea):
    title = tit.get()
    author = aut.get()
    year = yea.get()
    tit.delete(0, END)
    aut.delete(0, END)
    yea.delete(0, END)
    add_book(con, cursor, title, author, year)

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
    SubmitBtn = Button(root,text="SUBMIT",bg='#d5c4a1', fg='#1d2021',command=lambda : registerBooks(con, cursor, bookInfo2, bookInfo3, bookInfo4))
    SubmitBtn.place(relx=0.43,rely=0.9, relwidth=0.18,relheight=0.08)
    

  

def main():
    # IMPORTANT: Change the user and passwd (and\or collation if problems) vvv
    con = sqltor.connect(host="localhost", user="3curtain", passwd="3curtain", database="Osoi", collation='utf8mb4_general_ci')
    if not con.is_connected():
        print('Error in Connection')
        return
    cursor = con.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS Books(BookID int primary key, Title varchar(30), Author varchar(30), Year int, IssBy int);")
    cursor.execute("CREATE TABLE IF NOT EXISTS Users(UID int primary key, UName varchar(30), pwd bigint);")
    cursor.execute("INSERT IGNORE INTO Users Values(0, 'osoi', 702074847096)")
    con.commit()

    # return_book(con, cursor, (0, "Osoi"), 0)
    # register_user(con, cursor, "osoi", "findusinfiji")
    print(encrypt_pwd("osoi", "findusinfiji"))
    exit(0)
    
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

    con.close()

if __name__ == "__main__":
    main()
