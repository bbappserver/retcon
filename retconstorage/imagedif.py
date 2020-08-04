from PIL import Image,ImageFilter,ImageSequence
import array

SOBEL_MAT_X=(
    1,0,-1,
    2,0,-2,
    1,0,-1)

SOBEL_KERNEL_X=ImageFilter.Kernel((3,3), SOBEL_MAT_X, scale=None, offset=0)
class ImageSequenceSource:

    SEQUENCE_TYPE_STILL_IMAGE=0 #A still immage is an image sequence of length 1
    SEQUENCE_TYPE_GIF=1
    SEQUENCE_TYPE_VIDEO=2
    def __init__(self,abspath,sequence_type,keyframe_delta_threshold=.55,max_median_delta=.98,color_depth=256):
        '''
        If a frame changes more than kerframe_delta_threshold it will be considered a keyframe.
        A common transition is to flash momentarily to white, but it is useless to consider this a keyframe.
        With a max_median_delta if most of the frame has a sudden significant change this will not be counted as a keyframe.
        The next keyframe will happen once transitioning stops and tha algorithm detects normal change from actual content frames.
        '''
        self.path=abspath
        self._frames=None
        self._keyframes=None
        self._sequence_type=sequence_type
        self.keyframe_delta_threshold=keyframe_delta_threshold
        self.color_depth=color_depth
        self.max_median_delta=max_median_delta

        if color_depth != 256:
            raise NotImplementedError('Colorspaces other than RGB8 not yet supported')
        
        if sequence_type == self.SEQUENCE_TYPE_STILL_IMAGE:
            self._im = Image.open(abspath)
            self._frames=[self._im]
            self._keyframes=[self._im]
            self._im.close()
        elif sequence_type == self.SEQUENCE_TYPE_GIF:
            self._im = Image.open(abspath)
            self._keyframes=ImageSequence.Iterator(self._im)
            self._frames=ImageSequence.Iterator(self._im)
            self._im.close()
        elif sequence_type == self.SEQUENCE_TYPE_VIDEO:
            try:
                import cv2
                self._im= cv2.VideoCapture(abspath)
            except ImportError:
                import logging
                logger = logging.getLogger(__name__)
                logger.error('OpenCV must be installed to visually hash videos')
                raise ValueError('OpenCV must be installed to visually hash videos')

        else:
            raise NotImplementedError()

    def __del__(self):
        if self._sequence_type == self.SEQUENCE_TYPE_VIDEO:
            self._im.release()
        else:
            self._im.close()
    
    def keyframes(self):
        if self._keyframes is None and self._sequence_type == self.SEQUENCE_TYPE_VIDEO:
            return self._filter_video_keyframes()
        else:
            return self._keyframes
    
    def frames(self):
        if self._frames is None and self._sequence_type == self.SEQUENCE_TYPE_VIDEO:
            self._frames=self._load_video()
        return self._frames

    def _load_video(self):
        try:
            import cv2
        except ImportError:
            import logging
            logger = logging.getLogger(__name__)
            logger.error('OpenCV must be installed to visually hash videos')
            raise ValueError('OpenCV must be installed to visually hash videos')
        frameCount = int(self._im.get(cv2.CAP_PROP_FRAME_COUNT))
        fc=0
        ret=True
        while (fc < frameCount  and ret):
            ret,f = self._im.read()
            fc+=1
            yield f
    
    def _filter_video_keyframes(self):
        try:
            import numpy as np
        except ImportError:
                logger.error('Numpy must be installed to visually hash videos')
                raise ValueError('Numpy must be installed to visually hash videos')
        cap = self._im
        frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        refPhase=True

        #TODO This assumes RGB8
        ref = np.empty(( frameHeight, frameWidth, 3), np.dtype('uint8'))
        f = np.empty(( frameHeight, frameWidth, 3), np.dtype('uint8'))
        reft=np.empty(( 9, 9, 3), np.dtype('uint8'))
        ft=np.empty(( 9, 9, 3), np.dtype('uint8'))

        fc = 0
        ret = True

        thresh_percent=self.keyframe_delta_threshold
        max_median_delta = round(self.max_median_delta * (self.color_depth -1))

        thresh= thresh_percent* (self.color_depth-1)#color integers are zero indexed(black)

        while (fc < frameCount  and ret):
            ret,f = cap.read()
            ft = cv2.resize(f,(9,9), interpolation = cv2.INTER_CUBIC)
            delta=ft-reft
            abs_delta=np.abs(delta)
            mse = np.mean(abs_delta)
            med=np.median(abs_delta)

            if mse>thresh and med<max_median_delta:
                yield f

            ref=f
            reft=ft
            fc += 1

        
    

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


class ImageSequenceComparer:

    def __init__(self,sequence_a,sequence_b):
        self._a=sequence_a
        self._b=sequence_b

    def cmp(self):
        raise NotImplementedError()
        a=self._a
        b=self._b
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
        
