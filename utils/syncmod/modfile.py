import os
import json
import zipfile
import threading
import hashlib
import uuid
import shutil
class Modfile:
    _file_path: str="C:\Program Files (x86)\Steam\steamapps\common\Stardew Valley\Mods"
    _file_path_2: str="C:\Program Files\Steam\steamapps\common\Stardew Valley\Mods"
    lock: bool = False
    isProcess:bool = False
    def __init__(self):
        self._file_path = self._file_path if os.path.exists(self._file_path) else self._file_path_2
        if not os.path.exists(self._file_path):
            self.log(f"Neither of the default paths exist: {self._file_path}, {self._file_path_2}")
            raise FileNotFoundError(f"Neither of the default paths exist: {self._file_path}, {self._file_path_2}")

    def set_file_path(self, path: str):
        if os.path.exists(path):
            self._file_path = path
            self.lock = False
        else:
            self.log(f"The specified path does not exist: {path}")
            raise FileNotFoundError(f"The specified path does not exist: {path}")
            
    def get_file_path(self) -> str:
        return self._file_path
    def log(self,*x):
        pass
    def makefolder(self,path):
        if not os.path.exists(path):
            os.makedirs(path)
            self.log("Make Folder:",path)
       
    def deletefolder(self,path):
        if os.path.exists(path):
            if os.path.isdir(path):
                self.log("Delete Folder:",path)
                shutil.rmtree(path)
    def doUpdate(self):
        pass
class ProfileMod(Modfile): 
    profile_name:list[str] = ["default",]
    data: dict = {"profile_name":[],"now":""}
    nowProfile:str = "default"
    def __init__(self):
        super().__init__()
        if (not os.path.exists(os.path.join(self.get_file_path(),"profile.json")) or not os.path.exists(os.path.join(self.get_file_path(),"profile")) or not 
                              os.path.exists(os.path.join(self.get_file_path(),"profile","default")) or not os.path.exists(os.path.join(self.get_profilename_path("default"),"default.zip"))):
            self.data["profile_name"] = self.profile_name
            self.data["profile_name"] = self.nowProfile
            self.ProfileJsonWrite(self.data)
            self.makefolder(os.path.join(self.get_file_path(),"profile"))
            self.makefolder(os.path.join(self.get_file_path(),"profile","default"))
            if not os.path.exists(os.path.join(self.get_profilename_path("default"),"default.zip")):
                self.zipfileNow(profile_name="default")
            self.chackNowProfile()
        else:
            with open(os.path.join(self.get_file_path(),"profile.json"), "r") as f:
                self.data = json.load(f)
                f.close()
            self.profile_name = self.data["profile_name"]
            try:
                self.nowProfile = self.data["now"]
            except:
                self.data["now"] = "default"
                self.ProfileJsonWrite(self.data)
            self.chackNowProfile()
    def get_path_profile(self) -> str:
        return os.path.join(self.get_file_path(), "profile")
    def add_profile(self, profile_name: str):
        if profile_name not in self.profile_name:
            self.profile_name.append(profile_name)
            self.data["profile_name"] = self.profile_name
            self.ProfileJsonWrite(self.data)
            self.log(profile_name,"-> profile.json")    
            self.makefolder(os.path.join(self.get_profilename_path(profile_name)))
        else:
            raise ValueError(f"Profile '{profile_name}' already exists.")
    def remove_profile(self, profile_name: str):
        self.isProcess =True
        if profile_name=="default":
            raise ValueError(f"You cant deleted `default` profile")
        if profile_name in self.profile_name:
            self.profile_name.remove(profile_name)
            self.data["profile_name"] = self.profile_name
            self.ProfileJsonWrite(self.data)
            self.deletefolder(os.path.join(self.get_file_path(),"profile",profile_name))
            self.doUpdate()
        else:
            raise ValueError(f"Profile '{profile_name}' does not exist.")
        self.isProcess =False
    def get_profiles(self) -> list[str]:
        return self.profile_name
    def get_profilename_path(self, profile_name: str) -> str:
        if profile_name in self.profile_name:
            return os.path.join(self.get_file_path(), "profile", profile_name)
        else:
            raise ValueError(f"Profile '{profile_name}' does not exist.")
    zipfileIsFinished: bool = True
    def zip_task(self,profile_name,mode="w")->str:
        self.zipfileIsFinished: bool = False
        self.isProcess = True
        path_folder = self.get_profilename_path(profile_name)
        zip_path = os.path.join(path_folder, f"{profile_name}.zip")
        if mode == "backup":
            zip_path = os.path.join(path_folder, f"{profile_name}_bak_{uuid.uuid1()}.zip")
        self.log(f"[{profile_name}]","Zipping File:",profile_name,f"-> {zip_path}")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.get_file_path()):
                if os.path.abspath(root) == os.path.abspath(self.get_path_profile()):
                    continue
                for file in files:
                    file_path = os.path.join(root, file)
                    if file=="profile.json":
                        continue
                    if "profile" not in os.path.relpath(file_path, self.get_file_path()).split(os.sep):
                        arcname = os.path.relpath(file_path, self.get_file_path())
                        zipf.write(file_path, arcname)
        zipf.close()
        self.log(f"[{profile_name}]","Zip File Sucessed!:",f"{profile_name}.zip")
        if mode == "backup":
            sumsha256=self.zip_checksum_backup(zip_path=zip_path)
        else:
            sumsha256=self.write_zip_checksum(zip_path=zip_path,profile_name=profile_name)
        self.zipfileIsFinished: bool = True
        self.isProcess = False
        self.doUpdate()
        return sumsha256,zip_path
    def zipfileNow(self, profile_name: str):
        thread = threading.Thread(target=self.zip_task,args=(profile_name,))
        thread.start()
    def saveSha256(self,sha,profile_name):
        self.log(f"[{profile_name}]","sha256->data.json")
        with open(os.path.join(self.get_profilename_path(profile_name=profile_name),"data.json"), "w") as data_file:
            json.dump({"sha256": sha}, data_file, indent=4)
        data_file.close()

    def write_zip_checksum(self,zip_path,profile_name)->str:
        with open(zip_path, "rb") as f:
            checksum = self.zip_checksum_backup(zip_path)
            self.saveSha256(checksum,profile_name)
        f.close()
        return checksum
    def zip_checksum_backup(self,zip_path)->str:
        sha256_hash = hashlib.sha256()
        try:
            with open(zip_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
                checksum = sha256_hash.hexdigest()
            f.close()
        except:
            checksum = ""
        self.log("sha256 checkSumFile:",checksum)
        return checksum
    def unzipfile(self, profile_name: str) -> bool:
        zip_path = os.path.join(self.get_profilename_path(profile_name), f"{profile_name}.zip")
        if not os.path.exists(zip_path):
            raise FileNotFoundError(f"Zip file does not exist: {zip_path}")
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(os.path.join(self.get_file_path()))
            zipf.close()
        return True
    def ProfileJsonWrite(self,data:dict):
        with open(os.path.join(self.get_file_path(),"profile.json"), "w") as f:
                json.dump(self.data, f, indent=4)
        f.close()
    def chackNowProfile(self):
        try:
            self.get_profilename_path(self.nowProfile)
        except ValueError as e:
            self.nowProfile = "default"

        if not os.path.exists(os.path.join(self.get_profilename_path(self.nowProfile),f"{self.nowProfile}.zip")):
            self.nowProfile = "default"