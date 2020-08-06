from django.test import TestCase as djTest
from unittest import TestCase
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
                self.assertTrue(len(list(seq.frames()))>2)
                self.assertTrue(len(list(seq.frames()))>2)

    def testLoadVideo(self):
        path=os.path.join(self.basedir, 'test/big*.mp4')
        l=glob(path)
        if len(l)==0:
            raise NotImplementedError("test data not found mp4")
        for p in l:
            with self.subTest("load "+p):
                seq=ImageSequenceSource(p,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)
                self.assertTrue(len(list(seq.frames()))>5)
                with self.subTest("repeat "+p):
                    self.assertTrue(len(list(seq.frames()))>5)
        
        path=os.path.join(self.basedir, 'test/big*.avi')
        l=glob(path)
        if len(l)==0:
            raise NotImplementedError("test data not found avi")
        for p in l:
            with self.subTest("load "+p):
                seq=ImageSequenceSource(p,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)
                self.assertTrue(len(list(seq.frames()))>5)
                with self.subTest("repeat "+p):
                    self.assertTrue(len(list(seq.frames()))>5)

        path=os.path.join(self.basedir, 'test/big*.wmv')
        l=glob(path)
        if len(l)==0:
            raise NotImplementedError("test data not found wmv")
        for p in l:
            with self.subTest("load "+p):
                seq=ImageSequenceSource(p,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)
                self.assertTrue(len(list(seq.frames()))>5)
                with self.subTest("repeat "+p):
                    self.assertTrue(len(list(seq.frames()))>5)

    def testCompareVideoToSelf(self):
        pa=os.path.join(self.basedir, 'test/bigbuckclipped.mp4')
        pb=os.path.join(self.basedir, 'test/bigbuckclipped.mp4')
        a= ImageSequenceSource(pa,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)
        b= ImageSequenceSource(pb,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)

        import numpy as np
        fla=list(a.frames())
        flb=list(b.frames())
        for i in range(a.frame_count):
            fa=fla[i].as_array()
            fb=flb[i].as_array()
            self.assertTrue(np.array_equal(fa,fb))
        
        a= ImageSequenceSource(pa,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)
        b= ImageSequenceSource(pb,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)

        
        overlap=ImageSequenceComparer(a,b).cmp()
        self.assertTrue(len(overlap)==1)
    def testCompareVideoToShrink(self):
        pa=os.path.join(self.basedir, 'test/bigbuckclipped.mp4')
        pb=os.path.join(self.basedir, 'test/bigbuckclippedshrink.mp4')
        a= ImageSequenceSource(pa,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)
        b= ImageSequenceSource(pb,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)
        
        overlap=ImageSequenceComparer(a,b).cmp()
        self.assertTrue(len(overlap)>0)


    def testCompareVideoToShrinkClipped(self):
        pa=os.path.join(self.basedir, 'test/bigbuckclipped.mp4')
        pb=os.path.join(self.basedir, 'test/bigbuckclippedshrinkcut.mp4')
        a= ImageSequenceSource(pa,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)
        b= ImageSequenceSource(pb,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)
        
        overlap=ImageSequenceComparer(a,b).cmp()
        self.assertTrue(len(overlap)>0)

    def testCompareVideoShrinkToShrinkClipped(self):
        pa=os.path.join(self.basedir, 'test/bigbuckclippedshrink.mp4')
        pb=os.path.join(self.basedir, 'test/bigbuckclippedshrinkcut.mp4')
        a= ImageSequenceSource(pa,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)
        b= ImageSequenceSource(pb,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)

        overlap=ImageSequenceComparer(a,b).cmp()
        self.assertTrue(len(overlap)>0)
    def testCompareVideoToAnimatedGif(self):
        pa=os.path.join(self.basedir, 'test/bigbuckclipped.mp4')
        pb=os.path.join(self.basedir, 'test/bigbuckclippedshrinkcut.gif')
        a= ImageSequenceSource(pa,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)
        b= ImageSequenceSource(pb,ImageSequenceSource.SEQUENCE_TYPE_GIF)

        overlap=ImageSequenceComparer(a,b).cmp()
        self.assertTrue(len(overlap)>0)

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

    basedir=os.path.dirname(__file__)

    def testDhashStill(self):
        path=os.path.join(self.basedir, 'test/big*.jpg')
        l=glob(path)
        for p in l:
            with self.subTest("load "+p):
                a= ImageSequenceSource(p,ImageSequenceSource.SEQUENCE_TYPE_STILL_IMAGE)
                h=dhash(a)
                self.assertTrue(len(h)==1)
    
    def testDhashAnimatedGIF(self):
        path=os.path.join(self.basedir, 'test/big*.gif')
        l=glob(path)
        for p in l:
            with self.subTest("load "+p):
                a= ImageSequenceSource(p,ImageSequenceSource.SEQUENCE_TYPE_GIF)
                h=dhash(a)
                self.assertTrue(len(h)>1)
    
    def testDhashVideo(self):
        path=os.path.join(self.basedir, 'test/big*.mp4')
        l=glob(path)
        for p in l:
            with self.subTest("load "+p):
                a= ImageSequenceSource(p,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)
                h=dhash(a)
                self.assertTrue(len(h)>1)
    
    # def testDhashcompareStillAndStill(self):
    #     raise NotImplementedError
    # def testDhashcompareStillAndVideo(self):
    #     raise NotImplementedError
    # def testDhashcompareStillAndGIF(self):
    #     raise NotImplementedError

    # def testDhashcompareGIFAndGIF(self):
    #     raise NotImplementedError

    # def testDhashcompareGIFAndVideo(self):
    #     raise NotImplementedError

    # def testDhashcompareVideoAndVideo(self):
    #     raise NotImplementedError

    # def testDhashcompareAll(self):
    #     '''Check that if all media types are in a table they are detected as overlapping'''
    #     raise NotImplementedError