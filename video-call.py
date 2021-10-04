#!/usr/bin/python3

import pickle
import cv2
import struct
import socket
from threading import Thread
import sys
from PyQt5 import QtCore, QtGui, QtWidgets



class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(750, 500)
        MainWindow.setWindowTitle("Video call")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.webcam_1 = QtWidgets.QLabel(self.centralwidget)
        self.webcam_1.setGeometry(QtCore.QRect(0, 0, 741, 391))
        #self.webcam_1.setScaledContents(True)
        self.webcam_1.setObjectName("webcam-0")

        self.webcam_0 = QtWidgets.QLabel(self.centralwidget)
        self.webcam_0.setGeometry(QtCore.QRect(0, 0, 191, 151))
        self.webcam_0.setScaledContents(True)
        self.webcam_0.setObjectName("webcam-1")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(0, 401, 291, 41))
        self.lineEdit.setObjectName("lineEdit")

        self.connect_Button = QtWidgets.QPushButton(self.centralwidget)
        self.connect_Button.setGeometry(QtCore.QRect(290, 400, 141, 41))
        self.connect_Button.setObjectName("connection")
        self.connect_Button.setText("push for connection")
        self.connect_Button.clicked.connect(lambda : Thread(target = self.webcam_show_0 , args = ("client" , self.lineEdit.text())).start())

        self.server_Button = QtWidgets.QPushButton(self.centralwidget)
        self.server_Button.setGeometry(QtCore.QRect(437,400,141,41))
        self.server_Button.setObjectName("server")
        self.server_Button.setText("push for start server")
        self.server_Button.clicked.connect(lambda : Thread(target = self.webcam_show_0 , args = ("host" , self.lineEdit.text())).start())

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 750, 30))
        self.menubar.setObjectName("menubar")

        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)


    def webcam_show_0(self , connection_type , ip_port) : # 0 means your webcam not connection webcam .
        if connection_type == "host" :
            ip , port = ip_port.split(" ")
            server = procces("host" , ip , port)
            send_data = server.send_data_h

        elif connection_type == "client" : 
            ip , port = ip_port.split(" ")
            server = procces("client" , ip , port)
            send_data = server.send_data_c

        else : return "There is a problem to for connection_type ."
    
        Thread(target = server.get_data , args = (connection_type , )).start()

        webcam = cv2.VideoCapture(0)
        _ , frame = webcam.read()
        height , width , channel = frame.shape
        bytesPerLine = 3 * width
        while True : 
            _ , frame = webcam.read()
            send_data(frame)
            qImg = QtGui.QImage(frame.data , width , height , bytesPerLine , QtGui.QImage.Format_BGR888)
            self.webcam_0.setPixmap(QtGui.QPixmap(qImg))



    def webcam_show_1(self , frame) : # 1 means webcam of who connect to you
        hight , width , channel = frame.shape
        bytesPerLine = 3 * width
        qImg = QtGui.QImage(frame.data , width , hight , bytesPerLine , QtGui.QImage.Format_BGR888)
        self.webcam_1.setPixmap(QtGui.QPixmap(qImg))





class procces : 
    def __init__(self , connection_type , ip , port) : 
        self.server_config = (ip , int(port)) 
        
        if connection_type == "host" : 
            self.server_socket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
            self.server_socket.bind(self.server_config)
            print("server started ...")
            self.server_socket.listen(1)
            self.client , self.client_info = self.server_socket.accept()
            print(f"{self.client_info} has connected into server")

        elif connection_type == "client" : 
            self.server_socket = socket.socket(socket.AF_INET , socket.SOCK_STREAM) # I change client_socket to server_socket for have one function to send no two .
            self.server_socket.connect(self.server_config)
            print("connected ... ")
        

    def send_data_c(self , frame_data) : 
        data = pickle.dumps(frame_data)
        try :
            self.server_socket.send(struct.pack("L" , len(data)) + data)
        except : print("oh no yamete kodasai")

                                                            #TODO delete this try and except they are so slow bro .  

    def send_data_h(self , frame_data) : 
        data = pickle.dumps(frame_data)
        try :
            self.client.send(struct.pack("L" , len(data)) + data)
        except : print("oh no yamete kodasai")


    def get_data(self , type ) : 
        if type == "host" : 
            socket_connection = self.client
        elif type == "client" : 
            socket_connection = self.server_socket
       
        else : return "There is problem for giving type attribute . "  # Just if the type isn't in the if statment , stop to function .

        data = b""
        payload_size = struct.calcsize("L")
        try : 
            while True :
                while len(data) < payload_size :
                    data += socket_connection.recv(4096)
                
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("L" , packed_msg_size)[0]
                n = 0
                while len(data) < msg_size : 
                    data += socket_connection.recv(4096)
                frame_data = data[:msg_size]
                data = data[msg_size:]
                
                frame = pickle.loads(frame_data)
                if frame :
                    ui.webcam_show_1(frame)
                else : 
                    print("shit we can't get the data ") #TODO DELETE THIS ELSE CONDITION AFTER TEST .
                    print(frame)

        except : 
            self.get_data(type)








if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
