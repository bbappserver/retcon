from django.test import TestCase as djTest
from rest_framework.test import DjangoClient
from retcon.test.CRUDTest import APICRUDTest
from unittest import TestCase,skip
from retconstorage.imagedif import ImageSequenceComparer,ImageSequenceSource,dhash
from glob import glob
import os.path

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

    @skip("This takes a while, only run if it isn't actually working")
    def testCompareVideoToSelf(self):
        pa=os.path.join(self.basedir, 'test/bigbuckclipped.mp4')
        pb=os.path.join(self.basedir, 'test/bigbuckclipped.mp4')
        a= ImageSequenceSource(pa,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)
        b= ImageSequenceSource(pb,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)
        overlap=ImageSequenceComparer(a,b).cmp()
        i=0
        for e in overlap:
            i+=1
            if i>1:
                self.assertTrue(i==1,"There should be only one overlap interval for identical videos")
        self.assertTrue(i==1,"There should be only one overlap interval for identical videos")

    @skip("Only needed to prove that iterating two video sequences works, but its long so skip it if this is working.")
    def testDirectCompareVideoToSelf(self):
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
            self.assertFalse(fa is fb,"Two image sequences must not return the same underlying object per frame")
            self.assertTrue(np.array_equal(fa,fb),"Frames should always match for identical video streams")

    def testCompareVideoToShrink(self):
        pa=os.path.join(self.basedir, 'test/bigbuckclipped.mp4')
        pb=os.path.join(self.basedir, 'test/bigbuckclippedshrink.mp4')
        a= ImageSequenceSource(pa,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)
        b= ImageSequenceSource(pb,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)
        
        overlap=ImageSequenceComparer(a,b).cmp()
        for e in overlap:
            self.assertTrue(e is not None,"Expected overlap but there was none.")
            break



    def testCompareVideoToShrinkClipped(self):
        pa=os.path.join(self.basedir, 'test/bigbuckclipped.mp4')
        pb=os.path.join(self.basedir, 'test/bigbuckclippedshrinkcut.mp4')
        a= ImageSequenceSource(pa,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)
        b= ImageSequenceSource(pb,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)
        
        overlap=ImageSequenceComparer(a,b).cmp()
        for e in overlap:
            self.assertTrue(e is not None,"Expected overlap but there was none.")
            break

    @skip("Only run if broken, very time consuming")
    def testCompareVideoShrinkToShrinkClipped(self):
        pa=os.path.join(self.basedir, 'test/bigbuckclippedshrink.mp4')
        pb=os.path.join(self.basedir, 'test/bigbuckclippedshrinkcut.mp4')
        a= ImageSequenceSource(pa,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)
        b= ImageSequenceSource(pb,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)

        overlap=ImageSequenceComparer(a,b).cmp()
        for e in overlap:
            self.assertTrue(e is not None,"Expected overlap but there was none.")
            break
    
    @skip("Only run if broken, very time consuming")
    def testCompareVideoToAnimatedGif(self):
        pa=os.path.join(self.basedir, 'test/bigbuckclipped.mp4')
        pb=os.path.join(self.basedir, 'test/bigbuckclippedshrinkcut.gif')
        a= ImageSequenceSource(pa,ImageSequenceSource.SEQUENCE_TYPE_VIDEO)
        b= ImageSequenceSource(pb,ImageSequenceSource.SEQUENCE_TYPE_GIF)
        overlap=ImageSequenceComparer(a,b).cmp()
        for e in overlap:
            self.assertTrue(e is not None,"Expected overlap but there was none.")
            break

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