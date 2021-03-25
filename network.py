from PyQt5.QtCore import pyqtSignal, QObject

class network(QObject):
    received = pyqtSignal(str) #str is the received message
    #int for the next three signals is message id from the send function
    undelivered = pyqtSignal(int) #emit when timeout is off and the message isn't delivered
    delivered = pyqtSignal(int) #emit when delivered
    read = pyqtSignal(int) #emit when read

    def __init__(self):
        super(network, self).__init__()
        #TODO
        #self.received.emit("Hello, world!")

    def send(id, str):
        pass
