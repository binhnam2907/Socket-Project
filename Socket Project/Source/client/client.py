import socket
from tkinter import *
from tkinter import messagebox
import os
from struct import unpack
import pickle  # convert list to string

ClientSocket = 0

def serverdown():
    messagebox.showinfo("Server", "Your server has been closed")
    back("search")
    back("login")

def updateScrollRegion(canvas):
    canvas.update_idletasks()
    canvas.config(scrollregion=scrollable_frame.bbox())

def CntToServer(host, port):
    global ClientSocket
    ClientSocket = socket.socket()
    try:
        ClientSocket.connect((host, port))
        return 'Connected'
    except socket.error as e:
        return 'Cannot connect to server'

def createScrollFrame(frame):
    canvas = Canvas(frame)
    scrollable_frame = Frame(canvas)

    ScrollBarH = Scrollbar(frame)
    ScrollBarV = Scrollbar(frame)
    canvas.config(xscrollcommand=ScrollBarH.set, yscrollcommand=ScrollBarV.set, highlightthickness=0, height=100)

    ScrollBarH.config(orient=HORIZONTAL, command=canvas.xview)
    ScrollBarV.config(orient=VERTICAL, command=canvas.yview)

    ScrollBarH.pack(fill=X, side=BOTTOM, expand=FALSE)
    ScrollBarV.pack(fill=Y, side=RIGHT, expand=FALSE)

    canvas.pack(fill=BOTH, side=LEFT, expand=TRUE)
    canvas.create_window(0, 0, window=scrollable_frame, anchor=NW)
    return canvas, scrollable_frame

def connect():
    try:
        str = ip_inp.get()
        arr = str.split(':')
        host = arr[0]
        port = int(arr[1])
        respone = CntToServer(host, port)
        if respone == 'Connected':
            ip_inp.delete('0', END)
            login_frm.tkraise()
            connect_status.configure(text=respone + ' to server')
            messagebox.showinfo("Status", "Connected to server")
        elif respone == 'Cannot connect to server':
            messagebox.showwarning("Connect to server", "Cannot connect to server \nPlease try again or change IP:Host")
    except:
        messagebox.showwarning("Connect to server", "Invalid IP:Host")

def login():
    username = username_inp.get()
    pw = pw_inp.get()

    arr = ['login', username, pw]
    try:
        ClientSocket.sendall(pickle.dumps(arr))
    except:
        serverdown()
        return
   
    respone = ClientSocket.recv(1024).decode('utf-8')

    if (respone == 'Logged in successfully!'):
        username_inp.delete(0, 'end')
        pw_inp.delete(0, 'end')
        # add check in here
        search_frm.tkraise()
        messagebox.showinfo("Login", respone)
    else:
        messagebox.showwarning("Login", respone)

def register():
    username = username_inp.get()
    pw = pw_inp.get()

    arr = ['register', username, pw]
    try: 
        ClientSocket.sendall(pickle.dumps(arr))
    except:
        serverdown()
        return
    respone = ClientSocket.recv(1024).decode('utf-8')

    if respone == 'True':
        messagebox.showinfo("Register", "Your account has been created")
    else:
        messagebox.showwarning("Register", "Your account hasn't been created!\nPlease check username")

def search():
    search = search_inp.get()
    arr = ['search', search]
    try:
        ClientSocket.sendall(pickle.dumps(arr))
    except:
        serverdown()
        return

    if (scrollable_frame.winfo_exists()):
        for widgets in scrollable_frame.winfo_children():
            widgets.destroy()
    respone = ClientSocket.recv(8)
    (length,) = unpack('>Q',respone) #>Q = unsigned long long number (max number)
    data = b''
    buffersize = 1024
    while len(data) < length:
        readbuf = length - len(data) #find latest pack size to read
        if readbuf <= 33: break #added latest data, <= 33 because some of data is truncated as define a variable to store it or lost during transfer to router, 33 is in server and client in 1PC, 17 is in 2 PC have server or client (debugged to see more detail)
        data += ClientSocket.recv(buffersize if readbuf > buffersize else readbuf)
        
    ClientSocket.sendall(b'\00') #sent ack to know EOF
    inforarr = pickle.loads(data)
    if inforarr == False:
        messagebox.showwarning("Search", 'No infor available')
        return
    elif inforarr == None:
        messagebox.showwarning("Search", 'Wrong search syntax')
        return
    else:
        arr = ['searchheader']
        try:
            ClientSocket.sendall(pickle.dumps(arr))
        except:
            serverdown()
            return
        respone = ClientSocket.recv(1024)
        headertable = pickle.loads(respone)
        for i in range(len(headertable)):
            Label(scrollable_frame, text=headertable[i]).grid(
                row=0, column=i+1)

        for i in range(len(inforarr)):
            j = 1
            for k in headertable:
                val = inforarr[i][k.lower()]
                Label(scrollable_frame, text=val).grid(row=i+1, column=j, sticky='w', padx=5, pady=5)
                j = j+1
            Button(scrollable_frame, text='Download', command=lambda filename=inforarr[i]['filename']:
                   downloadInfor(filename)).grid(row=i+1, column=j, sticky='n', padx=5, pady=5)
        updateScrollRegion(canvas)
        search_res_frm.pack(fill='x', padx=10, pady=10)

def downloadInfor (name):
    if not os.path.exists('./infordownload'): #create folder if no exist
        os.makedirs('./infordownload')
   
    arr = ['download', name]
    try:
        ClientSocket.sendall(pickle.dumps(arr))
    except:
        serverdown()
        return

    respone = ClientSocket.recv(8)
    (length,) = unpack('>Q',respone)
    data = b''
    buffersize = 1024*10
    while len(data) < length:
        readbuf = length - len(data) #find latest pack size to read
        if readbuf <= 33: break #added latest data
        data += ClientSocket.recv(buffersize if readbuf > buffersize else readbuf)
         
    ClientSocket.sendall(b'\00') #sent ack to know EOF

    file = open('./infordownload/'+name, 'wb')
    file.write(data)
    file.close()
    
    messagebox.showinfo("Status", "Downloaded file (" + name + ') to ./infordownload')

def back(frame):
    global ClientSocket
    if frame == 'login':
        ClientSocket.close()
        username_inp.delete(0, 'end')
        pw_inp.delete(0, 'end')
        connect_frm.tkraise()
    elif frame == 'search':
        search_inp.delete(0,END)
        if (scrollable_frame.winfo_exists()):
            for widgets in scrollable_frame.winfo_children():
                widgets.destroy()
        login_frm.tkraise()

root = Tk()
root.title("Danh ba so - SOCKET PROJECT")
####### socket connection ######


connect_frm = LabelFrame(root)
connect_frm.grid(pady=5, padx=5, row=0, column=0, sticky=NSEW)
Label(connect_frm, text='Type your server IP and host, ex: 127.0.0.1:12341').pack(pady=10)
ip_inp = Entry(connect_frm)
ip_inp.insert('0', '127.0.0.1:1233')
ip_inp.pack(pady=5)
connect_btn = Button(connect_frm, text='Connect', fg='red', command=connect)
connect_btn.pack(pady=5, padx=5)

####### socket connection ######


############## Login frame ####################

login_frm = Frame(root)
login_frm.grid(pady=5, padx=5, row=0, column=0, sticky=NSEW)
Button(login_frm, text='<< Disconnect', command=lambda x='login': back(x)).pack(
    side=TOP, anchor=NW)
connect_status = Label(login_frm, text='', fg='red')
connect_status.pack(side=TOP, pady=5)
login_lbl_frm = LabelFrame(login_frm, text='Login')
login_lbl_frm.pack(padx=5, pady=5)
username_lbl = Label(login_lbl_frm, text="Username")
username_lbl.grid()
username_inp = Entry(login_lbl_frm)
username_inp.insert(0, 'admin')
username_inp.grid(row=0, column=2, padx=10)
pw_lbl = Label(login_lbl_frm, text="Password")
pw_lbl.grid()
pw_inp = Entry(login_lbl_frm)
pw_inp.insert(0, 'admin')
pw_inp.grid(row=1, column=2, padx=10)
login_btn = Button(login_lbl_frm, text="Login", fg="red", command=login)


# set Button grid

login_btn.grid(row=2, column=2, sticky='w', padx=10)
reg_btn = Button(login_lbl_frm, text="Register", fg="red", command=register)


# set Button grid


reg_btn.grid(row=2, column=2, sticky='e', pady=5, padx=10)

############## end Login frame ####################


###### search frame ##########
search_frm = Frame(root)
search_frm.grid(pady=5, padx=5, row=0, column=0, sticky=NSEW)

Button(search_frm, text='<< Logout', command=lambda x='search': back(x)).pack(side=TOP, anchor=NW)

success = Label(search_frm)
success.pack(padx=5)

search_lbl_frm = LabelFrame(search_frm, text='Search')
search_lbl_frm.pack(pady=5, padx=5, expand='true')

#####
search_info = Frame(search_lbl_frm)
search_info.pack(pady=5, padx=5, fill='x')
searchrule = ['Cách search:', 'F_ID 0 để hiển thị hết thành viên', 'F_Name : Name là tên thành viên(không dấu). VD: F_Name "Le Nguyen Binh Nam"',
              'F_Mail: Mail là thư điện tử. VD: F_Mail "20127567@student.hcmus.edu.vn"', 'F_MSSV: MSSV của thành viên. VD: F_MSSV 20127567']

for x in searchrule:
    Label(search_info, text=x).grid(sticky='w')
#####

#####


search_inp_frm = Frame(search_lbl_frm)
search_inp_frm.pack(fill='x', padx=5, pady=5)
search_lbl = Label(search_inp_frm, text="Type here: ")
search_lbl.grid(sticky='w')
search_inp = Entry(search_inp_frm)
search_inp.insert(0, 'F_ID 0')
search_inp.grid(row=0, column=2)
search_btn = Button(search_inp_frm, text='Search', command=search)
search_btn.grid(row=0, column=3, padx=5)


######


###### result frame ##########
search_res_frm = LabelFrame(search_lbl_frm, text='Result')
search_res_frm.pack(fill='x', padx=10, pady=10)
canvas, scrollable_frame = createScrollFrame(search_res_frm)
###### result frame ##########
connect_frm.tkraise()
###### search frame ##########
root.mainloop()