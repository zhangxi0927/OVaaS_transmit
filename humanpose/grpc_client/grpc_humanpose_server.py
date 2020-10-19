# this file run on the model server
import grpc
import time
import datetime
from concurrent import futures
import grpc_humanpose_pb2 as pb2
import grpc_humanpose_pb2_grpc as pb2_grpc
import numpy as np
import io
# FIXIT: change Hyperparameters
_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_HOST = 'localhost'
_PORT = '10004'
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