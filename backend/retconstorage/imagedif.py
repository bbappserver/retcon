from PIL import Image,ImageFilter,ImageSequence
from math import isclose
import array
try:
    import numpy as np
except ImportError:
        logger.error('Numpy must be installed to visually hash')
        raise ValueError('Numpy must be installed to visually hash')

try:
    import cv2
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.error('OpenCV must be installed to visually hash videos')
    raise ValueError('OpenCV must be installed to visually hash videos')

# TODO this gets iframes, they might be an acceptable substitute for just deltas over a certain level
# import av
# import av.datasets


# content = av.datasets.curated('pexels/time-lapse-video-of-night-sky-857195.mp4')
# with av.open(content) as container:
#     # Signal that we only want to look at keyframes.
#     stream = container.streams.video[0]
#     stream.codec_context.skip_frame = 'NONKEY'

#     for frame in container.decode(stream):

#         print(frame)

#         # We use `frame.pts` as `frame.index` won't make must sense with the `skip_frame`.
#         frame.to_image().save(
#             'night-sky.{:04d}.jpg'.format(frame.pts),
#             quality=80,
#         )

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
        self._im=None
        self._sequence_type=sequence_type
        self.keyframe_delta_threshold=keyframe_delta_threshold
        self.color_depth=color_depth
        self.max_median_delta=max_median_delta

        if color_depth != 256:
            raise NotImplementedError('Colorspaces other than RGB8 not yet supported')
        
        if sequence_type == self.SEQUENCE_TYPE_STILL_IMAGE:
            self._im = Image.open(abspath)
            # self._frames=[self._im]
            # self._keyframes=[self._im]
        elif sequence_type == self.SEQUENCE_TYPE_GIF:
            self._im = Image.open(abspath)
            # self._keyframes=ImageSequence.Iterator(self._im)
            # self._frames=ImageSequence.Iterator(self._im)
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
        elif self._im is not None:
            self._im.close()
    
    def keyframes(self):
        if self._keyframes is None and self._sequence_type == self.SEQUENCE_TYPE_VIDEO:
            return (ImageWrapper(x) for x in self._filter_video_keyframes())
        elif self.SEQUENCE_TYPE_GIF == self._sequence_type:
            # return a new iterator every time, so this call is repeatable
            return (ImageWrapper(x) for x in ImageSequence.Iterator(self._im))
        else:
            self._keyframes=[ImageWrapper(self._im)]
            return self._keyframes
    
    def frames(self):
        if self._frames is None and self._sequence_type == self.SEQUENCE_TYPE_VIDEO:
            # raise NotImplementedError('Frames and keyframes needs to be modified to do this correctly for each source type')
            return (ImageWrapper(x)  for x in self._load_video())
        elif self.SEQUENCE_TYPE_GIF == self._sequence_type:
            # return a new iterator every time, so this call is repeatable
            return (ImageWrapper(x) for x in ImageSequence.Iterator(self._im))
        else:
            self._frames=[ImageWrapper(self._im)]
            return self._frames

    @property
    def shape(self):
        if self.SEQUENCE_TYPE_VIDEO == self._sequence_type:
            try:
                import cv2
            except ImportError:
                import logging
                logger = logging.getLogger(__name__)
                logger.error('OpenCV must be installed to visually hash videos')
                raise ValueError('OpenCV must be installed to visually hash videos')
            cap = self._im
            frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return (frameWidth,frameHeight)
        else:
            return self._im.size
    
    @property 
    def size(self): return self.shape

    @property
    def frame_count(self) -> int:

        if self._sequence_type == self.SEQUENCE_TYPE_VIDEO:
            try:
                import cv2
            except ImportError:
                import logging
                logger = logging.getLogger(__name__)
                logger.error('OpenCV must be installed to visually hash videos')
                raise ValueError('OpenCV must be installed to visually hash videos')
            frameCount = int(self._im.get(cv2.CAP_PROP_FRAME_COUNT))
            return frameCount
        elif self._sequence_type == self.SEQUENCE_TYPE_GIF:
            return len(list(self.frames()))
        else:
            return 1 #stillimage

    def _load_video(self):
        try:
            import cv2
        except ImportError:
            import logging
            logger = logging.getLogger(__name__)
            logger.error('OpenCV must be installed to visually hash videos')
            raise ValueError('OpenCV must be installed to visually hash videos')
        #rewind
        self._im.set(cv2.CAP_PROP_POS_FRAMES,0)
        #
        frameCount = int(self._im.get(cv2.CAP_PROP_FRAME_COUNT))
        fc=0
        ret=True
        while (fc < frameCount  and ret):
            ret,f = self._im.read()
            fc+=1
            yield f
    
    def _filter_video_keyframes(self):

        try:
            import cv2
        except ImportError:
            import logging
            logger = logging.getLogger(__name__)
            logger.error('OpenCV must be installed to visually hash videos')
            raise ValueError('OpenCV must be installed to visually hash videos')
        cap = self._im
        frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        refPhase=True

        fc = 0
        ret = True

        thresh_percent=self.keyframe_delta_threshold
        max_median_delta = round(self.max_median_delta * (self.color_depth -1))

        thresh= thresh_percent* (self.color_depth-1)#color integers are zero indexed(black)

        ret,reff = cap.read()
        if not ret: return 
        yield reff # the first frame is always a keyframe
        while (fc < frameCount-1  and ret):
            ret,f = cap.read()
            #ft = cv2.resize(f,(9,9), interpolation = cv2.INTER_CUBIC)
            delta=f-reff
            abs_delta=np.abs(delta)
            mse = np.mean(abs_delta)
            med=np.median(abs_delta)

            if mse>thresh and med<max_median_delta:
                #Found a keyframe
                yield f
                reff=f #update the reference frame to this keyframe

            fc += 1

        
    

def dhash(image_sequence) -> list:
    '''Produce an array of dhashes for the given image sequence 
    image_sequence is a generator of RGB images
    size is 9x8 to generate exactly 64 bits
    https://web.archive.org/save/http://www.hackerfactor.com/blog/?/archives/529-Kind-of-Like-That.html
    '''
    sigs=[]
    
    for s in image_sequence.keyframes():
        sig=0
        i=0
        
        s.resize((9,8)) #shrink
        s.convert("L") #Greyscale
        s.filter(SOBEL_KERNEL_X)
        s=s.as_array()

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

def bit_hamming_distance(a,b,nbits=64)->int:
    c= a^b
    return bit_count(c,nbits=nbits)

def bit_count(x,nbits=64)->int:
    if nbits == 64: return bit_coutnt_fast_64(n)
    n=0
    for i in range(n):
        if x&1==1:
            n+=1
        x>>=1
    
    return n

def bit_coutnt_fast_64(n):
    '''
    Integer sorcery counts bits efficiently in a 64 bit number
    https://stackoverflow.com/questions/9829578/fast-way-of-counting-non-zero-bits-in-positive-integer'''
    n = (n & 0x5555555555555555) + ((n & 0xAAAAAAAAAAAAAAAA) >> 1)
    n = (n & 0x3333333333333333) + ((n & 0xCCCCCCCCCCCCCCCC) >> 2)
    n = (n & 0x0F0F0F0F0F0F0F0F) + ((n & 0xF0F0F0F0F0F0F0F0) >> 4)
    n = (n & 0x00FF00FF00FF00FF) + ((n & 0xFF00FF00FF00FF00) >> 8)
    n = (n & 0x0000FFFF0000FFFF) + ((n & 0xFFFF0000FFFF0000) >> 16)
    n = (n & 0x00000000FFFFFFFF) + ((n & 0xFFFFFFFF00000000) >> 32) # This last & isn't strictly necessary.
    return n

class ImageWrapper:
    '''Depending on whether an image originates from PIL or OpenCV it has a different format and operations.
    This class is a wrapper making them behave the same so analysis algorithms don't have to be concerned about this.
    It closely mirrors PIL's Image interface.'''

    IMAGE_TYPE_PIL=0
    IMAGE_TYPE_NUMPY_RGB8=1
    IMAGE_TYPE_NUMPY_GREY8=2
    def __init__(self,img,bit_depth=8):
        self._source_img=img
        self._source_img_type=None
        self._img=img
        self._type=None
        if bit_depth != 8:
            raise NotImplementedError("Non 8 bit images not currently supported")
        if issubclass(type(img),Image.Image): 
            self._type=self.IMAGE_TYPE_PIL
            self._source_img_type=self.IMAGE_TYPE_PIL
        elif issubclass(type(img),np.ndarray):
            if len(img.shape)==2:
                self._type=self.IMAGE_TYPE_NUMPY_GREY8
                self._source_image_type=self.IMAGE_TYPE_NUMPY_GREY8
            elif img.shape[2] == 3:
                self._type=self.IMAGE_TYPE_NUMPY_RGB8
                self._source_image_type=self.IMAGE_TYPE_NUMPY_RGB8
        else:
            raise ValueError("Unsupported image representation")

        # if self._type != self.IMAGE_TYPE_PIL and not issubclass(type(self._img),np.ndarray):
        #     breakpoint
    
    def as_array(self,copy=True,refcheck=True):
        '''Returns this image as a 3D numpy array of bands'''
        if self._type != self.IMAGE_TYPE_PIL:
            return self._img
        else:
            if copy:
                return np.array(np.copy(self._img))
            else:
                np.array(self._img,refcheck=refcheck)


    def as_PIL_Image(self):
        if self._type == self.IMAGE_TYPE_PIL:
            return self._img
        elif self._type==self.IMAGE_TYPE_NUMPY_RGB8:
            return Image.fromarray(np.copy(self._img), 'RGB')
        elif self._type==self.IMAGE_TYPE_NUMPY_GREY8:
            return Image.fromarray(np.copy(self._img), 'L')
        else:
            raise ValueError('self._type set incorectly')

    def convert(self,colorspace):
        '''Changes the colorspace of the returned image matching PIL.Image.convert'''
        self._img=self.as_PIL_Image()
        self._type=self.IMAGE_TYPE_PIL
        self._img=self._img.convert(colorspace)

    def resize(self,dim,resample=3): 
        '''Changes the colorspace of the returned image matching PIL.Image.resize'''
        #3 is the default mode for pil resize
        self._img=self.as_PIL_Image()
        self._type=self.IMAGE_TYPE_PIL
        self._img=self._img.resize(dim,resample=resample)
    
    def filter(self,kernel):
        '''Changes the colorspace of the returned image matching PIL.Image.convert'''
        self._img=self.as_PIL_Image()
        self._type=self.IMAGE_TYPE_PIL
        self._img=self._img.filter(kernel)


class ImageSequenceComparer:

    def __init__(self,sequence_a : ImageSequenceSource,sequence_b : ImageSequenceSource):
        self._a=sequence_a
        self._b=sequence_b

    def image_distance(self,a,b,depth=255) -> float:
        e=a-b
        return np.median(e)/depth

    def cmp(self,tolerance=.03,min_frames=5,look_ahead=10)-> list:
        
        #For still images, just fudege the frames to 1
        if self._a.frame_count == 1 or self._b.frame_count == 1:
            min_frames=1
        
        if self._a.frame_count<min_frames or self._b.frame_count < min_frames:
            return []

        # b should definitely be the shorter duration if possible
        if self._b.frame_count > self._a.frame_count:
            a=self._b
            b=self._a
        else:
            a=self._a
            b=self._b

        #Match dimensions
        dim_a = a.shape
        dim_b = b.shape
        dimensions_mismatch=dim_a != dim_b
        if dimensions_mismatch:
            w=0
            h=0
            if dim_a[0] <= dim_b[0]: 
                w=dim_a[0]
            else: 
                w=dim_b[0]
            
            if dim_a[1] <= dim_b[1]: 
                h=dim_a[1]
            else: 
                h=dim_b[1]
        
        
        target_colorspace="RGB"

        a=a.frames()
        b=b.frames()

        na=[]
        nb=[]
        
        # #DEBUG, no colorspace ordimension conversion
        # na=[x.as_array() for x in a]
        # nb=[x.as_array() for x in b]

        # #DEBUG equality check
        # for i in range(len(na)):
        #     if not np.array_equal(na[i],nb[i]):
        #         print("Array mismatch")

        for f in a:
            if dimensions_mismatch:
                f.resize((w,h))
            f.convert(target_colorspace)
            na.append(f.as_array())
        
        for f in b:
            if dimensions_mismatch:
                f.resize((w,h))
            f.convert(target_colorspace)
            nb.append(f.as_array())

        i=0
        j=0
        match_spans=[]
        start_frames=None
        #TODO be smarter about freeing passed frames
        # el=[] #DEBUG collect errors
        N=len(na)
        while i < N:
            j=0
            for M in range(len(nb)):
                fb=nb[j]
                #this occurs every iteration as i can be updated in the inner loop
                #it is important that frame a be updated every time since i might follow j
                #before fa was only being updated in the outer loop and this caused errors
                fa=na[i]

                e = self.image_distance(fa,fb)
                # el.append(e) #DEBUG collect errors
                if e<tolerance:
                    #fa and fb match
                    if start_frames is None:
                        #Look ahead to see if this was really the best match
                        #or just coincidentally similar
                        #stream b is repeated constantly so we only have to consider i and fa
                        #consider not just this frame but the error of the frame after it, as this framem ight be a conincidence
                        if not isclose(e,0):
                            i, e = self.look_ahead(e, na, i, fb, look_ahead, nb, j)
                        #end lookahead
                        start_frames=(i,j)
                else:
                    if start_frames is not None:
                        #fa and fb stopped matching
                        end_frames=(i,j)

                        #filter out short common sequences too short probably a black frame or something
                        if end_frames[0]-start_frames[0] >min_frames:
                            t=(start_frames,end_frames)
                            yield t
                        start_frames=None
                
                if e<tolerance:
                    i+=1 # i moves with j while frames match
                    
                j+=1

            #Grab the trailing span
            if start_frames is not None:
                end_frames=(i,j)
                if end_frames[0]-start_frames[0] >min_frames:
                    t=(start_frames,end_frames)
                    yield t
            i+=1

    def look_ahead(self, e, na, i, fb, look_ahead, nb, j):
        #Look ahead to see if this was really the best match
        #or just coincidentally similar
        #stream b is repeated constantly so we only have to consider i and fa

        try:
            base_i=i
            e_cand_cum = e
            for ela in range(1,look_ahead):
                e_cand_cum += self.image_distance(na[base_i+ela],fb[base_i+ela])
            
            for la in range(1,look_ahead):
                fa_alt=na[base_i+la]
                e_alt = self.image_distance(fa_alt,fb)
                e_alt_cum=e_alt
                for ela in range(1,look_ahead):
                    #consider not just this frame but the error of the frames after it,
                    # as this frame might be a conincidence
                    fa_alt_ahead=na[base_i+la+ela]
                    fb_alt_ahead=nb[j+ela]
                    e_alt_cum += self.image_distance(fa_alt_ahead,fb_alt_ahead)
                if e_alt_cum < e_cand_cum:
                    #Found a better frame
                    i=base_i+la
                    e=e_alt
                    e_cand_cum=e_alt_cum
        except IndexError:
            #whoops overstepped the frames, no biggy
            pass
        return i, e
    
    def refine_match_spans(self,spans):
        '''More agressivly try to match spans based on preliminary findings by cmp()'''
        raise NotImplementedError()

        if len(spans) <=1:
            return spans
        
        a=spans[0]
        newspans=[]
        i=0
        t=None
        while i <len(spans):
            b=spans[i]
            
            if b[0][0]-a[1][0] < 2:
                x_start=a[0][0]
                x_end=b[1][0]

                y_start=a[0][1]
                y_end=b[1][1]
                t=((x_start,y_start),(x_end,y_end))
                a=t
            else:
                if t is None:
                    newspans.append(b)
                else:
                    newspans.append(t)
                t=None
                a=b
            i+=1

        #This will generate spans that don't quite line up because x will be longer than y
        #Do a new error calculation on these spans
        raise NotImplementedError()

        #return results
        return newspans

        #IF intervals overlap try to merge them and look for a minimized error
        #If a 1 or 2 frame gap occurs, bridge it

    def still_match(self):
        '''convenience method for still images'''
        return self.cmp()[0]==((0,0),(1,1))
        
