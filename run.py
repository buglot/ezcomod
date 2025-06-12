import os
import subprocess
try:
    import requests
except Exception as e:
    print(e)
    os.system(f"{os.sys.executable} -m pip install requests")

subprocess.call("python main.py")