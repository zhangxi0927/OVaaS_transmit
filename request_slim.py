import requests
with open("r3800.JPG","rb") as f:
    jpg = f
    files = {'image':('r3800.JPG',f,'image/jpg',{})}
    # values = {'next':"http://localhost:7071/api/HttpTrigger1"}
    url = "https://ovaasmidtranstest.azurewebsites.net/api/HttpTrigger1"
    r = requests.post(url,files=files)
    print(r.text) 