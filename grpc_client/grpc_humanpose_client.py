import grpc
from . import grpc_humanpose_pb2 as pb2
from . import grpc_humanpose_pb2_grpc as pb2_grpc
import numpy as np
import logging
import traceback
#TODO Fix hyperparameters
_HOST = 'ovaasbackservertest.japaneast.cloudapp.azure.com'
_PORT = '10001'

def run(img:np.array): #[BCHW], shape [1,3,256,456]
    conn = grpc.insecure_channel(_HOST + ':' + _PORT)
    client = pb2_grpc.TransmitDataStub(channel=conn)

    try:
        img = img.tostring() #encode ndarray
        response = client.DoTransmit(pb2.DataRequest(img_nparray=img))
        people = np.fromstring(response.people)
        shape  = np.fromstring(response.shape)
        people = people.reshape(shape)
    except Exception as e:
        logging.error(f'{traceback.format_exc()}')

        people = None
        
    return people

if __name__ == '__main__':
    # for local debug
    img = np.random.rand(1,3,256,456)
    data = run(img)
