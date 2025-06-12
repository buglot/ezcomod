import socket
import threading
from utils import TypeCommu
from utils import MangagerProfile
import json
class ClientServer:
    myid:int| None = None
    connect_:bool = False
    _close :bool = False
    def __init__(self, ip,port):
        self.ip = ip
        self.port = port
    
    def connect(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.ip, self.port))
        print(f"Connected to server at {self.ip}:{self.port}")
        threading.Thread(target=self.receive_loop, daemon=True).start()

    def send(self, data):
        if self.connect_:
            self.client_socket.sendall(data.encode())
        else:
            while not self._close:
                if self.connect_:
                    self.client_socket.sendall(data.encode())
                    break
    def receive_loop(self):
        self.connect_ = True
        while not self._close:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    self.log("Server closed the connection.")
                    break
                self.controller(data.decode())
            except Exception as e:
                self.log(f"Error receiving data: {e}")
                self.connect_=False
                break
    def set_myid(self, myid: int):
        self.myid = myid
    def controller(self, data): 
        try:
            json_data = json.loads(data)
        except json.JSONDecodeError:
            self.log("Invalid JSON data received.")
            return None
        match TypeCommu(json_data.get("type")):
            case TypeCommu.TYPE_SYNC:
                self.set_myid(json_data.get("id"))
                self.doSync(json_data)
            case TypeCommu.TYPE_PROFILE_DELETE:
                self.doProfileDelete(json_data)
    def sendCommu(self,Type:TypeCommu):
        match Type:
            case TypeCommu.TYPE_SYNC:
                self.send(json.dumps({"type":TypeCommu.TYPE_SYNC.value}))
            case TypeCommu.TYPE_DOWNLOADED:
                self.send(json.dumps({"type":TypeCommu.TYPE_DOWNLOADED.value,"id":self.myid}))
            case TypeCommu.TYPE_DOWNLOADING:
                self.send(json.dumps({"type":TypeCommu.TYPE_DOWNLOADING.value,"id":self.myid}))
    def doSync(self,json_data):
        pass
    def doProfileDelete(self,json_data):
        pass
    def log(self,*x):
        pass
    def stop(self):
        self.connect_=False
        self._close = True
        self.client_socket.close()