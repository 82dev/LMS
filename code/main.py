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
    'lfg': '#1d2021',
}

def execommit(con, cursor, command):
    cursor.execute(command)
    con.commit()

def get_all_books(cursor):
    cursor.execute("select * from Books;")
    return cursor.fetchall()
def get_all_book_names(cursor):
    return [b[1] for b in get_all_books(cursor)]
def get_all_book_ids(cursor):
    return [b[0] for b in get_all_books(cursor)]

def get_all_issued_books(cursor, user):
    cursor.execute("select * from Books where IssBy="+user[0]+";")
    return cursor.fetchall()
def get_all_issued_book_names(cursor, user):
    return [b[1] for b in get_all_issued_books(cursor, user)]

def get_issuable_bookdata(cursor):
    cursor.execute("select BookID, Title from Books where IssBy is NULL;")
    d = cursor.fetchall();
    return ([b[1] for b in d], [b[0] for b in d])

def get_uname_from_id(cursor, uid):
    cursor.execute("select UName from Users where UID=" + uid + ";")
    return cursor.fetchone()[0]

def get_issued_bookdata(cursor, user):
    cursor.execute("select BookID, Title from Books where IssBy=" + str(user[0]) + ";")
    d = cursor.fetchall()
    return ([b[1] for b in d], [b[0] for b in d])

def add_book(con, cursor, title, author, year):
    cursor.execute("SELECT MAX(BookID) from Books;")
    q = cursor.fetchall();
    bookid = 0
    if len(q) > 0:
        bookid = q[0][0] + 1
    
    command = "insert into Books Values(" + str(bookid) + ',"' + title + '","' + author + '",' + year + ', NULL)'  
    execommit(con, cursor, command)

def remove_book(con, cursor, bookid, root):
    execommit(con, cursor, "delete from Books where BookID=" + str(bookid)+";")
    root.destroy()
    
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

def register_user(con, cursor, uname, pwd) -> (int, str):
    cursor.execute("SELECT MAX(UID) from Users;")
    uid = cursor.fetchall()[0][0] + 1
    hpwd = encrypt_pwd(uname, pwd)
    cursor.execute("INSERT INTO Users Values(" + str(uid) + ',"' + uname + '",' + str(hpwd) + ')')
    con.commit()
    return (uid, uname)


def check_login(con, cursor, uname, pwd) -> (bool, (int, str)):
    cursor.execute("SELECT UID, pwd from Users where UName='" + uname + "'")
    q = cursor.fetchall()
    if q == []:
        print("Username not found!")
        return (False, None)

    uid,hash = q[0]

    hpwd = encrypt_pwd(uname, pwd)

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

def issue_book(con, cursor, user, bookid, root) -> bool:
    """
        True if issued succesfully.
        False if book is already issued.
    """
    if is_issued(con, cursor, user, bookid):
        print("This book is already issued!")
        return False

    execommit(con, cursor, "UPDATE Books SET IssBy=" + str(user[0]) + " WHERE BookID=" + str(bookid) + ";")
    root.destroy()

def return_book(con, cursor, user, bookid) -> bool:
    if not issued_by(con, cursor, user, bookid):
        print("Not issued by the user!")
        return False
    execommit(con, cursor, "UPDATE Books SET IssBy=NULL WHERE BookID=" + str(bookid) + ";")
    return True

# TODO: cosmetics
# TODO: maybe diff scheme for admin
# admin = True iff admin
def seeBooksWin(con, cursor, admin):
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
    table[4] = ['Issued', 12] if not admin else ['Issued By', 12]

    for i in range(len(table)):
      Label(labelFrame, width=table[i][1], text=table[i][0]).grid(row=0, column=i)


    for i in range(rows):
        for j in range(5):
            text = books[i][j]
            if text == None:
                text = "None"
            elif admin and j == 4:
                text = get_uname_from_id(cursor, str(text))
            if not admin and j == 4:
                text = "No" if text == "None" else "Yes"

            e = Label(labelFrame,width = table[j][1], text=text, bg='#928374')
            e.grid(row=i+1, column=j)


def registerBooks(con, cursor, tit, aut, yea, root):
    title = tit.get()
    author = aut.get()
    year = yea.get()
    tit.delete(0, END)
    aut.delete(0, END)
    yea.delete(0, END)
    add_book(con, cursor, title, author, year)
    root.destroy()

def addBooksWin(con, cursor):
    root = Tk()
    root.title("Add Books")
    root.geometry("800x600")
    root.configure(bg="#d5c4a1")
    root.resizable(0, 0)
    
    heading = Label(root, fg='#fbfafa', bg=colors['dbg'], text='AddBooks', font=('Helvetica', 25), padx=70, pady=20)
    heading.place(relx=0.33, rely=0.1)

    
    labelFrame = Frame(root,bg=colors['lbg'])
    labelFrame.place(relx=0.1,rely=0.4,relwidth=0.8,relheight=0.4)
      
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
    SubmitBtn = Button(root,text="SUBMIT",bg='#d5c4a1', fg='#1d2021',command=lambda : registerBooks(con, cursor, bookInfo2, bookInfo3, bookInfo4, root))
    SubmitBtn.place(relx=0.43,rely=0.9, relwidth=0.18,relheight=0.08)

def removeBookWin(con, cursor):
    root = Tk()
    root.title("Remove Book")
    root.geometry("800x600")
    root.configure(bg="#d5c4a1")
    root.resizable(0, 0)
    
    heading = Label(root, fg='#fbfafa', bg=colors['dbg'], text='Remove Book', font=('Helvetica', 25), padx=70, pady=20)
    heading.place(relx=0.33, rely=0.1)

    
    labelFrame = Frame(root,bg=colors['lbg'])
    labelFrame.place(relx=0.1,rely=0.4,relwidth=0.8,relheight=0.4)

    var = StringVar(root)
    books = get_all_book_names(cursor)
    bids = get_all_book_ids(cursor)
    var.set(books[0])
    opts = OptionMenu(labelFrame, var, *books)
    opts.pack()

    removeBtn = Button(root,text="REMOVE",bg='#d5c4a1', fg='#1d2021',command=lambda : remove_book(con, cursor, bids[books.index(var.get())], root))
    removeBtn.place(relx=0.43,rely=0.9, relwidth=0.18,relheight=0.08)

def logged_in(con, cursor, user: (int, str)):
    if user[1] == 'osoi':
        admin_logged_in(con, cursor, user)
    else:
        user_logged_in(con, cursor, user)

def admin_logged_in(con, cursor, user):
    root = Tk()
    root.title("Welcome, osoi")
    root.geometry("800x600")
    root.resizable(0,0)

    root.configure(bg=colors['dbg'])

    heading = Label(root, fg='#fbfafa', bg='#7c6f64', text='Dashboard', font=('Helvetica', 25), padx=70, pady=20)
    heading.place(relx=0.33, rely=0.1)
    
    addBookBtn = Button(root,
                      text="Add Book",
                      background=colors['dbg'],
                      fg=colors['lfg'],
                      font=("Times New Roman", 20),
                      width=30,
                      pady=12,

                      command=lambda : addBooksWin(con, cursor)
                      )
    addBookBtn.place(relx=0.313, rely=0.39)
    removeBookBtn = Button(root,
                      text="Remove Book",
                      background=colors['dbg'],
                      fg=colors['lfg'],
                      font=("Times New Roman", 20),
                      width=30,
                      pady=12,

                      command=lambda : removeBookWin(con, cursor)
                      )
    removeBookBtn.place(relx=0.313, rely=0.49)
    viewBookBtn = Button(root,
                      text="View Books",
                      background=colors['dbg'],
                      fg=colors['lfg'],
                      font=("Times New Roman", 20),
                      width=30,
                      pady=12,

                      command=lambda : seeBooksWin(con, cursor, True)
                      )
    viewBookBtn.place(relx=0.313, rely=0.59)


def returnBookWin(con, cursor, user):
    root = Tk()
    root.title("Issue Book")
    root.geometry("800x600")
    root.resizable(0,0)

    root.configure(bg=colors['lbg'])

    heading = Label(root, fg='#fbfafa', bg='#7c6f64', text='Issue Book', font=('Helvetica', 25), padx=70, pady=20)
    heading.place(relx=0.33, rely=0.1)
    
    labelFrame = Frame(root,bg='#d5c4a1')
    labelFrame.place(relx=0.1,rely=0.4,relwidth=0.8,relheight=0.4)

    #Book selector
    bookLabel = Label(labelFrame,text="Book: ", bg='#d5c4a1', fg='#282828')
    bookLabel.place(relx=0.05,rely=0.2, relheight=0.08)

    (books, bids) = get_issued_bookdata(cursor, user)
    
    selectedBook = StringVar(root)
    selectedBook.set(books[0])
    
    bookdd = OptionMenu(labelFrame, selectedBook, *books)
    bookdd.place(relx=0.3,rely=0.2)

    returnBtn= Button(root,text="Issue",bg='#d5c4a1', fg='#1d2021',command=lambda : return_book(con, cursor,user, bids[books.index(selectedBook.get())], root))
    returnBtn.place(relx=0.43,rely=0.9, relwidth=0.18,relheight=0.08)

def user_logged_in(con, cursor, user):
    root = Tk()
    root.title("Welcome, " + user[1])
    root.geometry("800x600")
    root.resizable(0,0)

    root.configure(bg=colors['lbg'])

    heading = Label(root, fg='#fbfafa', bg='#7c6f64', text='Dashboard', font=('Helvetica', 25), padx=70, pady=20)
    heading.place(relx=0.33, rely=0.1)
    

    issueBookBtn = Button(root,
                      text="Issue Book",
                      background=colors['dbg'],
                      fg=colors['lfg'],
                      font=("Times New Roman", 20),
                      width=30,
                      pady=12,

                      command=lambda : issue_book_win(con, cursor, user)
                      )
    issueBookBtn.place(relx=0.313, rely=0.39)
    returnBookBtn = Button(root,
                      text="Return Book",
                      background=colors['dbg'],
                      fg=colors['lfg'],
                      font=("Times New Roman", 20),
                      width=30,
                      pady=12,

                      command=lambda : returnBookWin(con, cursor, user)
                      )
    returnBookBtn.place(relx=0.313, rely=0.49)
    viewBookBtn = Button(root,
                      text="View Books",
                      background=colors['dbg'],
                      fg=colors['lfg'],
                      font=("Times New Roman", 20),
                      width=30,
                      pady=12,

                      command=lambda : seeBooksWin(con, cursor, False)
                      )
    viewBookBtn.place(relx=0.313, rely=0.59)


def issue_book_win(con, cursor, user):
    root = Tk()
    root.title("Issue Book")
    root.geometry("800x600")
    root.resizable(0,0)

    root.configure(bg=colors['lbg'])

    heading = Label(root, fg='#fbfafa', bg='#7c6f64', text='Issue Book', font=('Helvetica', 25), padx=70, pady=20)
    heading.place(relx=0.33, rely=0.1)
    
    labelFrame = Frame(root,bg='#d5c4a1')
    labelFrame.place(relx=0.1,rely=0.4,relwidth=0.8,relheight=0.4)

    #Book selector
    bookLabel = Label(labelFrame,text="Book: ", bg='#d5c4a1', fg='#282828')
    bookLabel.place(relx=0.05,rely=0.2, relheight=0.08)

    (books, bids) = get_issuable_bookdata(cursor)
    
    selectedBook = StringVar(root)
    selectedBook.set(books[0])
    
    bookdd = OptionMenu(labelFrame, selectedBook, *books)
    bookdd.place(relx=0.3,rely=0.2)

    issueBtn= Button(root,text="Issue",bg='#d5c4a1', fg='#1d2021',command=lambda : issue_book(con, cursor,user, bids[books.index(selectedBook.get())], root))
    issueBtn.place(relx=0.43,rely=0.9, relwidth=0.18,relheight=0.08)

def login_win(con, cursor, start_root):
    root = Tk()
    root.title("Add Books")
    root.geometry("800x600")
    root.configure(bg=colors['lbg'])
    root.resizable(0, 0)


    heading = Label(root, fg='#fbfafa', bg='#7c6f64', text='Login', font=('Helvetica', 25), padx=70, pady=20)
    heading.place(relx=0.33, rely=0.1)

    labelFrame = Frame(root,bg='#d5c4a1')
    labelFrame.place(relx=0.1,rely=0.4,relwidth=0.8,relheight=0.4)

    # Username
    unameLabel = Label(labelFrame,text="Username : ", bg='#d5c4a1', fg='#282828')
    unameLabel.place(relx=0.05,rely=0.2, relheight=0.08)
        
    unameEntry = Entry(labelFrame, bg='#928374')
    unameEntry.place(relx=0.3,rely=0.2, relwidth=0.62, relheight=0.08)
        
    # Password
    passwordLabel = Label(labelFrame,text="Password : ", bg='#d5c4a1', fg='#282828')
    passwordLabel.place(relx=0.05,rely=0.35, relheight=0.08)

    passwordEntry = Entry(labelFrame, bg='#928374', show='*')
    passwordEntry.place(relx=0.3,rely=0.35, relwidth=0.62, relheight=0.08)

    def loginBtnOnClick():
        start_root.destroy()
        # TODO: uname, pwd mistakes
        logged_in(con, cursor, check_login(con, cursor, unameEntry.get(), pwd=passwordEntry.get())[1])
        root.destroy()

    loginBtn = Button(root, text="LOGIN", bg=colors['lbg'], fg=colors['lfg'], command=loginBtnOnClick)
    loginBtn.place(relx=0.43,rely=0.9, relwidth=0.18,relheight=0.08)

# TODO: Checkings 
def register_win(con, cursor, start_root):
    root = Tk()
    root.title("Register")
    root.geometry("800x600")
    root.configure(bg=colors['lbg'])
    root.resizable(0,0)

    heading = Label(root, fg='#fbfafa', bg='#7c6f64', text='Register', font=('Helvetica', 25), padx=70, pady=20)
    heading.place(relx=0.33, rely=0.1)

    labelFrame = Frame(root,bg='#d5c4a1')
    labelFrame.place(relx=0.1,rely=0.4,relwidth=0.8,relheight=0.4)

    # Username
    unameLabel = Label(labelFrame,text="Username : ", bg='#d5c4a1', fg='#282828')
    unameLabel.place(relx=0.05,rely=0.2, relheight=0.08)
        
    unameEntry = Entry(labelFrame, bg='#928374')
    unameEntry.place(relx=0.3,rely=0.2, relwidth=0.62, relheight=0.08)
        
    # Password
    passwordLabel = Label(labelFrame,text="Password : ", bg='#d5c4a1', fg='#282828')
    passwordLabel.place(relx=0.05,rely=0.35, relheight=0.08)

    passwordEntry = Entry(labelFrame, bg='#928374', show='*')
    passwordEntry.place(relx=0.3,rely=0.35, relwidth=0.62, relheight=0.08)

    def registerBtnOnClick():
        uname = unameEntry.get()
        pwd = passwordEntry.get()

        user = register_user(con, cursor, uname, pwd)
        user_logged_in(con, cursor, user)
        start_root.destroy()
        root.destroy()

    registerBtn= Button(root, text="REGISTER", bg=colors['lbg'], fg=colors['lfg'], command=registerBtnOnClick)
    registerBtn.place(relx=0.43,rely=0.9, relwidth=0.18,relheight=0.08)

def start_page(con, cursor):
    root = Tk()
    root.title("Osoi")
    root.geometry("1280x720")
    root.configure(background=colors['lbg'])

    bg = ImageTk.PhotoImage(Image.open("main_page_blank.jpg"))
    canvas1 = Canvas(root,width=1280, height=720)
    canvas1.pack(fill="both", expand=True)
    canvas1.create_image(0,0, image=bg, anchor="nw")

    loginBtn = Button(root,
                      text="Login",
                      background=colors['dbg'],
                      fg=colors['lfg'],
                      font=("Times New Roman", 20),
                      width=30,
                      pady=12,
                      cursor='heart',

                      command=lambda : login_win(con, cursor, root)
                      )
    loginBtn.place(relx=0.313, rely=0.39)

    registerBtn = Button(root,
                      text="Register",
                      background=colors['dbg'],
                      fg=colors['lfg'],
                      font=("Times New Roman", 20),
                      width=30,
                      pady=12,
                      cursor='heart',

                      command=lambda: register_win(con, cursor, root)
                      )
    registerBtn.place(relx=0.313, rely=0.53)
    
    root.mainloop()

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
    # print(encrypt_pwd("osoi", "findusinfiji"))
    # exit(0)

    start_page(con, cursor)
  
    con.close()

if __name__ == "__main__":
    main()
