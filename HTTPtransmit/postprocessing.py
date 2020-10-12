# from pose_extractor import extract_poses
import cv2
import numpy as np

# TODO

class post_processing():
    def __init__(self,img_np,PAFs,heatmaps):
        self.PAFs = PAFs
        self.heatmaps = heatmaps
        self.img_np = img_np


    def renderPeople(self,img, people, scaleFactor=4, threshold=0.5):

        limbIds = [
            [ 1,  2], [ 1,  5], [ 2,  3], [ 3,  4], [ 5,  6], [ 6,  7], [ 1,  8], [ 8,  9], [ 9, 10], [ 1, 11],
            [11, 12], [12, 13], [ 1,  0], [ 0, 14], [14, 16], [ 0, 15], [15, 17], [ 2, 16], [ 5, 17] ]

        limbColors = [
            (255,  0,  0), (255, 85,  0), (255,170,  0),
            (255,255,  0), (170,255,  0), ( 85,255,  0),
            (  0,255,  0), (  0,255, 85), (  0,255,170),
            (  0,255,255), (  0,170,255), (  0, 85,255),
            (  0,  0,255), ( 85,  0,255), (170,  0,255),
            (255,  0,255), (255,  0,170), (255,  0, 85)]

        # 57x32 = resolution of HM and PAF
        scalex = img.shape[1]/(57 * scaleFactor)
        scaley = img.shape[0]/(32 * scaleFactor)
        for person in people:
            for i, limbId in enumerate(limbIds[:-2]):
                x1, y1, conf1 = person[limbId[0]*3:limbId[0]*3+2 +1]
                x2, y2, conf2 = person[limbId[1]*3:limbId[1]*3+2 +1]
                if conf1>threshold and conf2>threshold:
                    cv2.line(img, (int(x1*scalex),int(y1*scaley)), (int(x2*scalex),int(y2*scaley)), limbColors[i], 2)

    # PAF_blobName = 'Mconv7_stage2_L1'
    # HM_blobName  = 'Mconv7_stage2_L2'
    # PAF_shape    =  [1,38,32,57]
    # HM_shape     =  [1,19,32,57]
    def main(self):
        img = self.img_np
        img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)

        people = extract_poses(self.heatmaps[:-1], self.PAFs, 4)
        renderPeople(img, people, 4, 0.2)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img

# test

img = np.random.random([1,3,256,456])

PAFs = np.random.random([1,38,32,57])
heatmaps = np.random.random([1,19,32,57])

test = post_processing(img_np=img,PAFs=PAFs,heatmaps=heatmaps).main()

print(type(test))