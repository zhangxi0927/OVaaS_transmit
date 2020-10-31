import logging

import azure.functions as func
import numpy as np
from PIL import Image
import io

from . import preprocessing as prep
from . import postprocessing as posp
from time import time

import grpc
from tensorflow import make_tensor_proto, make_ndarray
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc

from . import pose_extractor

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
_HOST = 'ovaasbackservertest.japaneast.cloudapp.azure.com'
_PORT = '10002'

def main(req: func.HttpRequest) -> func.HttpResponse:
    _NAME = 'image'
    

    logging.info("Python HTTP trigger function processed a request")

    method = req.method
    url = req.url
    params = req.params
    try:
        files = req.files[_NAME]
        if files:
            # pre processing
            img_bin = files.read()  # get image_bin form request
            img = prep.to_pil_image(img_bin)
            img = prep.resize(img)  # w,h = 456,256
            img_np = np.array(img)
            img_np = np.float32(img_np)
            img_np = prep.transpose(img_np)  # hwc > bchw [1,3,256,456]
            # print(img_np.shape)
            
            request = predict_pb2.PredictRequest()
            request.model_spec.name = 'human-pose-estimation'
            request.inputs["data"].CopyFrom(make_tensor_proto(img_np, shape=img_np.shape))
            # send to infer model by grpc
            start = time()
            channel = grpc.insecure_channel("{}:{}".format(_HOST, _PORT))
            stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
            result = stub.Predict(request, 10.0)
            if not result:
                timecost = time()-start
                logging.warning(f"Inference complete,But no person detected,Takes{timecost}")
                return func.HttpResponse(f'No person detected',status_code=200)
            
            paf = make_ndarray(result.outputs["Mconv7_stage2_L1"])
            heatmaps = make_ndarray(result.outputs["Mconv7_stage2_L2"])
            
            timecost = time()-start
            logging.info(f"Inference complete,Takes{timecost}")

            # post processing
            people = pose_extractor.extract_poses(heatmaps[:-1], paf[0], 4)
            img_fin = posp.post_processing(img_np, people).res

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