from typing import  Tuple
from utils import ProfileMod
import threading
import os
import json
import requests
import uuid
class MangagerProfile(ProfileMod):
    isProcess:bool = False
    def __init__(self):
        super().__init__()

    def checkProfileAll(self):
        profile_delete = []
        for profile in self.get_profiles():
            if profile!="default":
                if os.path.exists(self.get_profilename_path(profile)):
                    if not os.path.exists(os.path.join(self.get_profilename_path(profile), f"{profile}.zip")) or not os.path.exists(os.path.join(self.get_profilename_path(profile), f"data.json")):
                        profile_delete.append(profile)
                else:
                    profile_delete.append(profile)  
        for x in profile_delete:
            self.remove_profile(x)
    def checkProfile(self, profile_name: str) -> bool:
        if profile_name not in self.get_profiles() :
            return False
        else:
            return True
    def checkProfilePathandZip(self,profile_name:str)->Tuple[bool,bool]:
        pro = False
        zipfile = False
        if os.path.exists(self.get_profilename_path(profile_name=profile_name)):
            pro=True
        if os.path.exists(self.get_zip_file_profile_path(profile_name)):
            zipfile=True
        return pro,zipfile
    def doMakeFolderProfile(self,profile_name):
        a,b= self.checkProfilePathandZip(profile_name)
        print(a,b)
        if not a:
            self.log("Fix bug:Forlder ")
            os.makedirs(self.get_profilename_path(profile_name=profile_name))
        if not b:
            self.log("Fix bug:create bank zipfile")
            with open(self.get_zip_file_profile_path(profile_name),"w") as f:
                f.write("bank file")
            f.close()
    def createProfile(self, profile_name: str):
        if not self.checkProfile(profile_name):
            self.log("Create Profile:",profile_name)
            self.add_profile(profile_name)
            self.zipfileNow(profile_name)
        else:
           self.updateProfile(profile_name)
    def updateProfile(self,profile_name: str):
        th = threading.Thread(target=self.tryzip, args=[profile_name])
        th.start()
    def tryzip(self, profile_name: str):
        sha256,zip_path=self.zip_task(profile_name, "backup") 
        if not self.checkProfileZip(sha256,profile_name):
            self.log("Have Change!")
            with open(os.path.join(self.get_profilename_path(profile_name), "data.json"), "w") as f:
                json.dump({"sha256": sha256}, f, indent=4)
                f.close()
            os.remove(os.path.join(self.get_profilename_path(profile_name), f"{profile_name}.zip"))
            os.rename(zip_path, os.path.join(self.get_profilename_path(profile_name), f"{profile_name}.zip"))  
            self.log("Have Change file Sucesseed!")
        else:
            self.log("Don't Have Anything Change!")  
            os.remove(zip_path)  
            self.log("Delete Backup file Sucesseed!") 
    def checkProfileZip(self,sha256,profile_name: str) -> bool:
        if os.path.exists(os.path.join(self.get_profilename_path(profile_name), f"data.json")):
            with open(os.path.join(self.get_profilename_path(profile_name), "data.json"), "r") as f:
                data = json.load(f)
                if data.get("sha256") == sha256:
                    return True
                else:
                    return False
        else:
            return False
    def donwloadFile(self, download_url: str, profile_name: str)->str:
            self.log("Download Mode ...")
            self.downloading()
            try:
                response = requests.get(f"http://{download_url}", stream=True)
                zip_path = os.path.join(self.get_profilename_path(profile_name=profile_name), f"{profile_name}_bak_{uuid.uuid1()}.zip")
                print(zip_path)
                total_size = int(response.headers.get('content-length', 0))
                downloaded_size = 0
                with open(zip_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            percent = (downloaded_size / total_size) * 100 if total_size else 0
                            self.perCentdownload(percent)
                f.close()
            except Exception as e:
                print(e)
                self.log(e)
            self.log("Download Mode Sucessed!!")
            self.downlaoded()
            return zip_path
    def createProfileClient(self, sha256, download_url, profile_name: str):
        self.isProcess = True
        if not self.checkProfile(profile_name):
            self.log("You don't have this profile!")
            self.add_profile(profile_name)
            profile_dir = self.get_profilename_path(profile_name)
            os.makedirs(profile_dir)
            self.log("Added Profile")
            zip_path=self.donwloadFile(download_url, profile_name)
            sha=self.write_zip_checksum(zip_path=zip_path, path_folder=profile_dir)
            if sha != sha256:
                self.saveSha256(sha=sha256,profile_name=profile_name)
        else:
            profile_dir = self.get_profilename_path(profile_name)
            self.doMakeFolderProfile(profile_name)
            sha=self.zip_checksum_backup(zip_path=self.get_zip_file_profile_path(profile_name))
            if sha != sha256:
                self.log("this Profile isn't same host!")
                old_file =os.path.join(profile_dir, f"{profile_name}_bak_{uuid.uuid1()}.zip")
                os.rename(os.path.join(profile_dir, f"{profile_name}.zip"), old_file)
                new_file = self.donwloadFile(download_url, profile_name)
                os.rename(new_file, os.path.join(profile_dir, f"{profile_name}.zip"))
                os.remove(old_file)
                self.saveSha256(sha=sha,profile_name=profile_name)
            else:
                self.log("Nothing change!")
        self.isProcess = False
    def perCentdownload(self,c):
        pass
    
    def saveSha256(self,sha,profile_name):
        self.log(profile_name,":","sha256->data.json")
        with open(os.path.join(self.get_profilename_path(profile_name=profile_name),"data.json"), "w") as data_file:
            json.dump({"sha256": sha}, data_file, indent=4)
        data_file.close()
    def getSha256(self,profile_name):
        data:dict
        with open(os.path.join(self.get_profilename_path(profile_name=profile_name),"data.json"),"r") as f:
            data=json.load(f)
        f.close()
        return data.get("sha256")
    def get_zip_file_profile_path(self,profile_name):
        return os.path.join(self.get_profilename_path(profile_name),f"{profile_name}.zip")
    def downloading(self):
        pass
    def downlaoded(self):
        pass