from django.test import TestCase
from retconstorage.imagedif import ImageSequenceComparer,ImageSequenceSource,dhash
from glob import glob
import os.path
# Create your tests here.

class ImageSequenceCompareTest(TestCase):

    basedir=os.path.dirname(__file__)

    def testLoadStilImage(self):
        path=os.path.join(self.basedir, 'test/big*.jpg')
        l=glob(path)
        if len(l)==0:
            raise NotImplementedError("test data not found jpg")
        for p in l:
            with self.subTest("load "+p):
                seq=ImageSequenceSource(p,ImageSequenceSource.SEQUENCE_TYPE_STILL_IMAGE)
                self.assertTrue(len(list(seq.frames()))>0)
                self.assertTrue(len(list(seq.frames()))>0)

    def testLoadAnimatedGIF(self):
        path=os.path.join(self.basedir, 'test/big*.gif')
        l=glob(path)
        if len(l)==0:
            raise NotImplementedError("test data not found GIF")
        for p in l:
            with self.subTest("load "+p):
                seq=ImageSequenceSource(p,ImageSequenceSource.SEQUENCE_TYPE_GIF)
                self.assertTrue(len(list(seq.frames()))>0)
                self.assertTrue(len(list(seq.frames()))>0)

    def testLoadVideo(self):
        path=os.path.join(self.basedir, 'test/big*.mp4')
        l=glob(path)
        if len(l)==0:
            raise NotImplementedError("test data not found mp4")
        for p in l:
            with self.subTest("load "+p):
                seq=ImageSequenceSource(p,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)
                self.assertTrue(len(list(seq.frames()))>0)
                self.assertTrue(len(list(seq.frames()))>0)
        
        path=os.path.join(self.basedir, 'test/big*.avi')
        l=glob(path)
        if len(l)==0:
            raise NotImplementedError("test data not found avi")
        for p in l:
            with self.subTest("load "+p):
                seq=ImageSequenceSource(p,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)
                self.assertTrue(len(list(seq.frames()))>0)
                self.assertTrue(len(list(seq.frames()))>0)

        path=os.path.join(self.basedir, 'test/big*.wmv')
        l=glob(path)
        if len(l)==0:
            raise NotImplementedError("test data not found wmv")
        for p in l:
            with self.subTest("load "+p):
                seq=ImageSequenceSource(p,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)
                self.assertTrue(len(list(seq.frames()))>0)
                self.assertTrue(len(list(seq.frames()))>0)

    def testCompareImageToImage(self):
        raise NotImplementedError(self)

    def testCompareVideoToShrink(self):
        raise NotImplementedError()

    def testCompareVideoToShrinkClipped(self):
        raise NotImplementedError()

    def testCompareVideoShrinkToShrinkClipped(self):
        raise NotImplementedError()

    def testCompareVideoToAnimatedGif(self):
        raise NotImplementedError()

    def testCompareVideoToStill(self):
        raise NotImplementedError()
        #test stills against normal
        #test stills against shrink
        #test stills against shrinkcut
    
    def testCompareStillToStill(self):
        l=[1,2,3,4,5,6,7]
        pairs=itertools.combinations(l)

        with self.subTest('identical'):
            raise NotImplementedError()
            #check image against identical image
        with self.subTest('small'):
            raise NotImplementedError()
            #check image agains shrunk image
        with self.subTest('small-variant'):
            raise NotImplementedError()
            #check image agains variant image
        raise NotImplementedError()

class DhashTest(TestCase):

    def testDhashStill(self):
        raise NotImplementedError
    
    def testDhashAnimatedGIF(self):
        raise NotImplementedError
    
    def testDhashVideo(self):
        raise NotImplementedError
    
    def testDhashcompareStillAndStill(self):
        raise NotImplementedError
    def testDhashcompareStillAndVideo(self):
        raise NotImplementedError
    def testDhashcompareStillAndGIF(self):
        raise NotImplementedError

    def testDhashcompareGIFAndGIF(self):
        raise NotImplementedError

    def testDhashcompareGIFAndVideo(self):
        raise NotImplementedError

    def testDhashcompareVideoAndVideo(self):
        raise NotImplementedError

    def testDhashcompareAll(self):
        '''Check that if all media types are in a table they are detected as overlapping'''
        raise NotImplementedError