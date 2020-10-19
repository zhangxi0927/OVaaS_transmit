import logging

import azure.functions as func
import numpy as np
from PIL import Image
import io
# Custom modules need to be prefixed with dot.and should use form[]import .I do not kown why
from . import preprocessing
from . import postprocessing
from time import time

import grpc
from tensorflow import make_tensor_proto, make_ndarray
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc

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

channel = grpc.insecure_channel("{}:{}".format('172.17.0.3', 9000))
stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)


def main(req: func.HttpRequest) -> func.HttpResponse:
    _NAME = 'image'
    request = predict_pb2.PredictRequest()
    request.model_spec.name = 'human-pose-estimation'

    logging.info("Python HTTP trigger function processed a request")
    # header = req.headers.items()
    # for i in header:
    #     print(i)
    method = req.method
    url = req.url
    params = req.params
    try:
        files = req.files[_NAME]
        if files:
            # pre processing
            img_bin = files.read()  # get image_bin form request
            img = preprocessing.to_pil_image(img_bin)
            img = preprocessing.resize(img)  # w,h = 456,256
            img_np = np.array(img)
            img_np = preprocessing.transpose(
                img_np)  # hwc > bchw [1,3,256,456]
            # print(img_np.shape)
            request.inputs["data"].CopyFrom(
                make_tensor_proto(img_np, shape=(img_np.shape)))
            # send to infer model by grpc
            start = time()
            people = stub.Predict(request, 10.0)
            timecost = time()-start
            logging.info(f"Inference complete,Takes{timecost}")

            # post processing
            img_fin = postprocessing.post_processing(img_np, people).res
            MIMEType = 'image/jpeg'
            return func.HttpResponse(body=img_fin, status_code=200, mimetype=MIMEType)

        else:
            return func.HttpResponse(f'no image files', status_code=400)
    except Exception as e:
        logging.info(f"Error:{e}\n\
                        url:{url}\n\
                        method:{method}\n\
                        params:{params}")
        return func.HttpResponse(f'Service Error.check the log.', status_code=500)

    # img.show() #for local debug
