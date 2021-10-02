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

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(0, 0, 741, 391))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")

        self.connect_Button = QtWidgets.QPushButton(self.centralwidget)
        self.connect_Button.setGeometry(QtCore.QRect(290, 400, 141, 41))
        self.connect_Button.setObjectName("connection")
        self.connect_Button.setText("push for connection")

        self.server_Button = QtWidgets.QPushButton(self.centralwidget)
        self.server_Button.setGeometry(QtCore.QRect(437,400,141,41))
        self.server_Button.setObjectName("server")
        self.server_Button.setText("push for start server")

        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(0, 401, 291, 41))
        self.lineEdit.setObjectName("lineEdit")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 750, 30))
        self.menubar.setObjectName("menubar")

        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)


    def webcam_show_0(self , frame) : # 0 means your webcam not connection webcam
       
        
        webcam = cv2.VideoCapture(0)
        _ , frame = webcam.read()
        height , width , channel = frame.shape
        self.label.setGeometry(QtCore.QRect(0 , 0, width , height))
        bytesPerLine = 3 * width
        while True : 
            _ , frame = webcam.read()
            #TODO : ADD PROCCESS CLASS , WE NEED FOR SENDING DATA .
            qImg = QtGui.QImage(frame.data , width , height , bytesPerLine , QtGui.QImage.Format_BGR888)
            self.label.setPixmap(QtGui.QPixmap(qImg))



    def webcam_show_1(self , frame) : # 1 means webcam of who connect to you
        hight , width , channel = frame.shape
        bytesPerLine = 3 * width
        qImg = QtGui.QImage(frame.data , width , hight , bytesPerLine , QtGui.QImage.Format_BGR888)
        self.label.setPixmap(QtGui.QPixmap(qImg))



class procces : 
    def __init__(self , connection_type , port , ip = "127.0.0.1") : 
        self.server_config = (ip , port) 
        
        if connection_type == "host" : 
            self.server_socket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
            self.server_socket.bind(self.server_config)
            print("server started ...")
            self.server_socket.listen(1)
            self.client , self.client_info = self.server_socket.accept()
            print(f"{self.client_info} has connected into server")

        elif connection_type == "client" : 
            self.client_socket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
            self.client_socket.connect(self.server_config)
        

    def host_send_data(self , frame_data) : 
        data = pickle.dumps(frame_data)
        self.server_socket.send(struct.pack("L" , len(data)) + data)


    def client_send_data(self , frame_data) : 
        data = pickle .dumps(frame_data)
        self.client_socket.send(struct.pack("L" , len(data)) + data)


    def get_data(self) : 
        data = b""
        payload_size = struct.calcsize("L")
        while True :
            while len(data) < payload_size :
                data += self.client_socket.recv(4096)
            
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("L" , packed_msg_size)[0]
            n = 0
            while len(data) < msg_size : 
                data += self.client_socket.recv(4096)
            frame_data = data[:msg_size]
            data = data[msg_size:]
            
            frame = pickle.loads(frame_data)
            ui.webcam_show_1(frame)








if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
