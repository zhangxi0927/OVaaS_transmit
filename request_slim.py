import requests
import os
print(os.getcwd())
with open("./resource/test.JPG","rb") as f:
    jpg = f
    files = {'image':('r3800.JPG',f,'image/jpg',{})}
    # values = {'next':"http://localhost:7071/api/HttpTrigger1"}
    url = "https://ovaashumanpose-test.azurewebsites.net/api/humanpose?"
    r = requests.post(url,files=files)
    print(r.text) 