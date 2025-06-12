
from ui import UI ,BaseRoot
import os
try:
    import requests
except Exception as e:
    print(e)
    os.system(f"{os.sys.executable} -m pip install requests")
root = BaseRoot()
app = UI(root)
root.mainloop()