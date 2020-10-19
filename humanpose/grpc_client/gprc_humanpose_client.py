import grpc
import grpc_humanpose_pb2 as pb2
import grpc_humanpose_pb2_grpc as pb2_grpc
import numpy as np
#TODO Fix hyperparameters
_HOST = 'localhost'
_PORT = '8008'
# _PATH = 'image/test.jpg'

def run(img:np.arrays): #[BCHW], shape [1,3,256,456]
    conn = grpc.insecure_channel(_HOST + ':' + _PORT)
    client = pb2_grpc.TransmitDataStub(channel=conn)
    print(type(img))

    try:
        response = client.DoTransmit(pb2.DataRequest(img_nparray=img))
        
        people = response.people
    except:
        # TODO add error log
        people = None
    return people

# here maybe need fix
if __name__ == '__main__':
    data = run(_PATH)
