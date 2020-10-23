import numpy as np
import cv2
from PIL import Image
import base64
import io


def decode(data):
    img_decode = io.BytesIO(data)
    return img_decode

def to_pil_image(img_bin):
    _decoded = io.BytesIO(img_bin)
    return Image.open(_decoded)

def resize(img:Image,w=456,h=256):
    img = img.resize((w,h),Image.ANTIALIAS)
    # TODO scale+padding is better
    return img

def transformCh(img:Image):
    r,g,b = img.split()
    img = Image.merge("RGB",(b,g,r))
    return img

def encode(img:Image): 
    buffer = io.BytesIO()
    img.save(buffer,format='JPEG')
    byte_data = buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    return base64_str

def transpose(data:np.array):
    # hwc > bchw
    new_shape = (2,0,1)
    r = data.transpose(new_shape)
    r = np.expand_dims(r, axis=0)
    return r
# if __name__ == "__main__":
#     pass
#     # a = Image.open('./r3800.JPG')
#     # a = encode(a)
#     # print(a)