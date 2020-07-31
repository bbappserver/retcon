from PIL import Image,ImageFilter,ImageSequence
import array
SOBEL_MAT_X=(
    (1,0,-1),
    (+2,0,-2),
    (1,0,-1)
    )
SOBEL_KERNEL_X=ImageFilter.Kernel((3,3), SOBEL_MAT_X, scale=None, offset=0)
class ImageSequenceSource:

    SEQUENCE_TYPE_STILL_IMAGE=0
    SEQUENCE_TYPE_GIF=0
    SEQUENCE_TYPE_VIDEO=0
    def __init__(self,abspath,sequence_type):
        self.path=abspath
        self._keyframes=None
        im = Image.open(abspath)
        
        if sequence_type == self.SEQUENCE_TYPE_STILL_IMAGE:
            self._frames=[im]
            self._keyframes=[im]
        elif sequence_type == self.SEQUENCE_TYPE_GIF:
            self._keyframes=ImageSequence.Iterator(im)
            self._frames=ImageSequence.Iterator(im)
        else:
            raise NotImplementedError()

    def keyframes(self):
        return self._keyframes
    
    def frames(self):
        return self._frames

    # def _load_video(self):
    #     import cv2
    #     vidcap = cv2.VideoCapture(self.path)
    #     return  (x for x in vidcap.read())
    
    # def _filter_video_keyframes(self):
    #     cap = cv2.VideoCapture('test.mp4')
    #     frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    #     frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    #     frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    #     refPhase=True
    #     ref = np.empty(( frameHeight, frameWidth, 3), np.dtype('uint8'))
    #     f = np.empty(( frameHeight, frameWidth, 3), np.dtype('uint8'))
    #     reft=np.empty(( 9, 9, 3), np.dtype('uint8'))
    #     ft=np.empty(( 9, 9, 3), np.dtype('uint8'))

    #     fc = 0
    #     ret = True

    #     threshF=.55

    #     thresh= threshF* 255 # assume 8bit color space

    #     while (fc < frameCount  and ret):
    #         ret,f = cap.read()
    #         ft = cv2.resize(f,(9,9), interpolation = cv2.INTER_CUBIC)
    #         d=ft-reft
    #         ad=np.abs(d)
    #         mse = np.mean(ad)
    #         stdv=np.median(ad)

    #         if mse>thresh and stdv<251:
    #             yield f

    #         ref=f
    #         reft=ft
    #         fc += 1

        
    

def dhash(image_sequence):
    '''Produce an array of dhashes for the given image sequence 
    image_sequence is a generator of RGB images
    size is 9x8 to generate exactly 64 bits
    https://web.archive.org/save/http://www.hackerfactor.com/blog/?/archives/529-Kind-of-Like-That.html
    '''
    sigs=[]
    for i in image_sequence:
        i=i.resize(9,8,resample=Image.BICUBIC) #shrink
        i=i.convert("L") #Greyscale
        s=i.filter(SOBEL_KERNEL_X) #generate gradient
        sig=0
        i=0

        #test if left >right, if so set bit high
        for row in s:
            prev=None
            for column in row:
                if prev is not None:
                    if column > prev:
                        sig |= 1<<i
                    prev=column
                    i+=1
        sigs.append(sig)
    return sigs

class ImageComparer:
    pass

class ImageSequenceComparer:

    def cmp(self):
        raise NotImplementedError()

        #TODO b should definitely be the shorter one if possible
        i=0
        match_spans=[]
        for fa in a:
            j=0
            for fb in b:
                e = image_distance(a,b)
                start_frames=None
                if e<tolerance:
                    #fa and fb match
                    if start_frames is None:
                        start_frames=(i,j)
                else:
                    if start_frames is not None:
                        #fa and fb stopped matching
                        end_frames=(i,j)

                        #filter out short common sequences too short probably a black frame or something
                        if end_frames[0]-start_frames[0] >30 and end_frames[1]-start_frames[1] >30:
                            t=(start_frames,end_frames)
                            match_spans.append(t)
                            start_frames=None
                            
                        #TODO if match type is random subsequence end early
                        break
                j+=1
            i+=1
        
