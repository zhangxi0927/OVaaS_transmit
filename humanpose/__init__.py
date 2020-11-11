import logging

import azure.functions as func
import numpy as np
from PIL import Image
import io
import sys
import os

from . import preprocessing as prep
from . import postprocessing as posp
from time import time

import grpc
from tensorflow import make_tensor_proto, make_ndarray
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc

import traceback
import cv2

try:
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
                img_cv_copied = cv2.cvtColor(np.asarray(img),cv2.COLOR_RGB2BGR)
                img = prep.resize(img)  # w,h = 456,256
                img_np = np.array(img)
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
                
                pafs = make_ndarray(result.outputs["Mconv7_stage2_L1"])[0]
                heatmaps = make_ndarray(result.outputs["Mconv7_stage2_L2"])[0]

                # logging.info(f"PAF{pafs.shape},\nheatmap{heatmaps.shape}")
                
                timecost = time()-start
                logging.info(f"Inference complete,Takes{timecost}")

                # post processing
                c = posp.estimate_pose(heatmaps,pafs)
                response_image = posp.draw_to_image(img_cv_copied,c)
                # response_image = cv2.resize(response_image,dsize=(0,0),fx=3,fy=3)
                # cv2.imshow('test',response_image)
                # cv2.waitKey(0)
                # cv2.destroyAllWindows()
                # cv2.imwrite(f,response_image,[cv2.IMWRITE_JPEG_QUALITY, 70])
                # print(response_image)
                imgbytes = cv2.imencode('.jpg',response_image)[1].tobytes()
                # print(type(imgbytes))
                # print(imgbytes)
                MIMETYPE =  'image/jpeg'
                return func.HttpResponse(body=imgbytes, status_code=200,mimetype=MIMETYPE,charset='utf-8')

            else:
                return func.HttpResponse(f'no image files', status_code=400)
        except Exception as e:
            logging.error(f"Error:{e}\n\
                            url:{url}\n\
                            method:{method}\n\
                            params:{params}")
            return func.HttpResponse(f'Service Error.check the log.', status_code=500)
except Exception as e:
    logging.error(f"{traceback.format_exc()}")
    # img.show() #for local debug
