# this file run on the model server
import grpc
import time
import datetime
from concurrent import futures
import grpc_humanpose_pb2 as pb2
import grpc_humanpose_pb2_grpc as pb2_grpc
import numpy as np
import io

###2020/10/19
from tensorflow import make_tensor_proto, make_ndarray
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc
from pose_extractor import extract_poses
##

# FIXIT: change Hyperparameters
_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_HOST = 'localhost'
_PORT = '10001'
_SHAPE = [1, 3, 256, 456]

class TransmitData(pb2_grpc.TransmitDataServicer):
    def DoTransmit(self, request, context):
        img_array = request.img_nparray #type:nparray
        # print(pb2.DataResponse(result=img_array.upper()))
        '''
        TODO 
            put img_array in humanpose_model.py
            and get return
        ''' 
        ##2020/10/19
        channel = grpc.insecure_channel(_HOST + ':' + _PORT)
        stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
        request = predict_pb2.PredictRequest()
        request.model_spec.name = "human-pose-estimation"
        request.inputs["data"].CopyFrom(make_tensor_proto(img_array, shape=(img_array.shape)))
        result = stub.Predict(request, 10.0)
        output_paf = make_ndarray(result.outputs["Mconv7_stage2_L1"])
        people = extract_poses(heatmaps[:-1], output_paf[0], 4) 
        ##
        # from humanpose import inference
        # people = inference(img_array)


        return pb2.DataResponse(people = people)


def serve():
    grpcServer = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    pb2_grpc.add_TransmitDataServicer_to_server(TransmitData(), grpcServer)
    grpcServer.add_insecure_port(_HOST + ':' + _PORT)
    grpcServer.start()
    try:
        while True:
            print(f'start===============>{_HOST}:{_PORT}')
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        grpcServer.stop(0)

# here maybe need fix
if __name__ == '__main__':
    serve()
