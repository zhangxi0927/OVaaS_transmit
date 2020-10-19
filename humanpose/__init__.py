import logging

import azure.functions as func
import numpy as np
from PIL import Image
import io
from .preprocessing import *   # Custom modules need to be prefixed with dot.and should use form[]import .I do not kown why
from .postprocessing import post_processing
from grpc_client.client import run as client
from time import time

'''
Post Analysis:

    header: content-type:multipart/form-data
    body: 	
    Content-Disposition: form-data; name="image"; filename="xxx.jpeg or xxx.png"
        Content-Type: image/jpeg or image/png
        
        image binary file
    *****************************************************
    file size: <500kb
    file analysis: .jpg/.jpeg only


'''


def main(req: func.HttpRequest) -> func.HttpResponse:
    _NAME = 'image'

    logging.info("Python HTTP trigger function processed a request")
    # header = req.headers.items()
    # for i in header:
    #     print(i)
    method = req.method
    url    = req.url
    params = req.params
    try:
        files = req.files[_NAME]
        if files:
            #pre processing
            img_bin = files.read()      #get image_bin form request
            img = to_pil_image(img_bin)
            img = resize(img) # w,h = 456,256        
            img_np = np.array(img)
            img_np = transpose(img_np) #hwc > bchw [1,3,256,456]
            # print(img_np.shape)

            # send to infer model by grpc
            start = time()
            people = client(img_np)
            timecost = time()-start
            logging.info(f"Inference complete,Takes{timecost}")

            #post processing
            img_fin = post_processing(img_np,people).res
            MIMEType = 'image/jpeg'
            return func.HttpResponse(body=img_fin,status_code=200,mimetype=MIMEType)

        else:
            return func.HttpResponse(f'no image files',status_code=400)
    except Exception as e:
        logging.debug(f"Error:{e}\n\
                        url:{url}\n\
                        method:{method}\n\
                        params:{params}")
        return func.HttpResponse(f'Service Error.check the log.',status_code=500)



    # img.show() #for local debug


    
    