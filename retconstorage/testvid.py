import cv2
import numpy as np
import time
#cap = cv2.VideoCapture('teststat.mp4')
cap = cv2.VideoCapture('test.mp4')
frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

refPhase=True
ref = np.empty(( frameHeight, frameWidth, 3), np.dtype('uint8'))
f = np.empty(( frameHeight, frameWidth, 3), np.dtype('uint8'))
reft=np.empty(( 9, 9, 3), np.dtype('uint8'))
ft=np.empty(( 9, 9, 3), np.dtype('uint8'))

fc = 0
ret = True

threshF=.55

thresh= threshF* 255 # assume 8bit color space

keyframes=[]

#cv2.namedWindow('frame 10')
# while (fc < frameCount  and ret):
#     if refPhase: 
#         ret,ref = cap.read()
#         reft = cv2.resize(ref,(9,9), interpolation = cv2.INTER_CUBIC)
#         refPhase=False
    
#     else:
#         ret,f = cap.read()
#         if(fc>1):
#             ft = cv2.resize(f,(9,9), interpolation = cv2.INTER_CUBIC)
#             mse = np.median(np.abs(ft-reft))
#             #print(mse)
#             if(mse>thresh):
#                 print("Frame:%d %g"%(fc,mse))
#                 refPhase=True
#                 keyframes.append(f)
#                 cv2.imshow('frame 10', f)
#                 cv2.waitKey(0)
#     fc += 1
# print(len(keyframes))

# cap.release()


while (fc < frameCount  and ret):
    ret,f = cap.read()
    ft = cv2.resize(f,(9,9), interpolation = cv2.INTER_CUBIC)
    d=ft-reft
    ad=np.abs(d)
    mse = np.mean(ad)
    stdv=np.median(ad)

    if mse>thresh and stdv<251:
        print("Frame:%d %g %g"%(fc,mse,stdv))
        #print(ad)
        keyframes.append(f)
        #dreft=cv2.resize(reft,(900,900), interpolation = cv2.INTER_CUBIC)
        # cv2.imshow('before', ref)
        # cv2.waitKey(500)
        # #dreft=cv2.resize(ft,(900,900), interpolation = cv2.INTER_CUBIC)
        # cv2.imshow('before', f)
        # cv2.waitKey(500)
    ref=f
    reft=ft
    fc += 1


print(len(keyframes))

cap.release()


class ImageSequenceStream:
    '''Wrapper object for animated GIF,Ugoira or video file'''

    def __getitem__(self,i):
        pass

    def isImageFile(self):
        pass
    def isVideoFile(self):
        pass
    def seek(self,i):
        #capture.set(cv2.CAP_PROP_POS_FRAMES, i)
        pass

    def __len__(self):
        pass
        

class ImageComparer:
    pass
class ImageSequenceStreamComparer:
    
    DIFFERENT=0
    PARTIAL_OVERLAP=1
    IDENTICAL=2
    def __init__(self,a,b,early_stop=IDENTICAL):
        if len(a)>len(b):
            self.short = b
            self.long =a
        else:
            self.short=a
            self.long =b
    
    def next(self):
        pass

    def has_next(self):
        pass
        