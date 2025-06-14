import socket
import threading
from utils.socketsServer.typecommu import TypeCommu
import json
class Server:
    ClientSocket:dict = {}
    count: int = 0
    profile_name: str = "default"
    sha256:str=None
    canRun :bool = True
    ddns:str ='0.0.0.0'
    port:str|None = None
    def __init__(self, host='0.0.0.0', port=65432):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        self.ddns = self.get_local_ipv4()
    def get_local_ipv4(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # This doesn't need to reach 8.8.8.8; it's just used to determine the outbound interface
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip    
    def start(self):
        self.log(f'Server started at {self.host}:{self.port}')
        thread = threading.Thread(target=self.socket_run)
        thread.daemon = True
        thread.start()
    def log(self,*x):
        pass
    def socket_run(self):
        while self.canRun:
            try:
                conn, addr = self.server_socket.accept()
                thread = threading.Thread(target=self.client_socket, args=(conn, addr))
                thread.daemon = True
                thread.start()
            except OSError as e:
                break
            except Exception as e:
                self.log("socket Error:",e)
                
    def client_socket(self,conn:socket.socket, addr):
        self.log(f'Connection from {addr}')
        myid = self.count
        self.ClientSocket[myid] = conn
        self.count += 1
        while self.canRun:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                self.commuJson(data.decode(),myid)
            except Exception as e:
                print("Error client id [",myid,"]:",e)
                self.canRun = False
                conn:socket.socket = self.ClientSocket.pop(myid)
                conn.close()
    def commuJson(self, data,id):
        try:
            json_data = json.loads(data)
            match TypeCommu(json_data.get("type")):
                case TypeCommu.TYPE_SYNC:
                    data = {"id":id, "type": TypeCommu.TYPE_SYNC.value, "profile_name": self.profile_name, "download_url": self.getDownloadUrl(),"sha256":self.sha256}
                    self.ClientSocket[id].send(json.dumps(data).encode())
                case TypeCommu.TYPE_DOWNLOADING:
                    self.log("Downloading... client id: ",id)
                case TypeCommu.TYPE_DOWNLOADED:
                    self.log("DOWNLOADED client id:", id)
        except json.JSONDecodeError:
            self.log("Invalid JSON data received.")
            return None

    def setProfile(self, profile_name: str):
        self.profile_name = profile_name
    def controller(self, type: TypeCommu):
        match type:
            case TypeCommu.TYPE_SYNC:
                    data = {"type": TypeCommu.TYPE_SYNC.value, "profile_name": self.profile_name, "download_url": self.getDownloadUrl(),"sha256":self.sha256}
                    self.sendallclient(data)
            case TypeCommu.TYPE_PROFILE_DELETE:
                    data = {"type": TypeCommu.TYPE_PROFILE_DELETE.value, "profile_name": self.profile_name}
                    self.sendallclient(data)

    def sendallclient(self, data: str):
        for id, client in self.ClientSocket.items():
            data["id"] = id
            try:
                client.send(json.dumps(data).encode())
            except Exception as e:
                self.log(f"Error sending data to client {id}: {e}")
                del self.ClientSocket[id]
    def stop(self):
        self.canRun = False
        self.server_socket.close()
    def getDownloadUrl(self):
        return f"{self.getDdns()}/{self.profile_name}.zip"
    def setDDNS(self,x:str):
        try:
            self.ddns,self.prot = x.split(":")
        except ValueError as e:
            self.ddns = x.split(":")[0]
    def getDdns(self):
        if self.port!=None:
            return f"{self.ddns}:{self.port}"
        else:
            return f"{self.ddns}:4000"

            