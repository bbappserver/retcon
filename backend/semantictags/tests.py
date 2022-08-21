from django.test import TestCase
from django.db import IntegrityError
from .models import Tag,TagLabel
from sharedstrings.models import Language
# Create your tests here.

class TestTag(TestCase):

    def testExpandImplies(self):
        # any_lang=Language.objects.first()
        # l=TagLabel(label="dummy",language=any_lang)
        a=Tag(definition="a")
        b=Tag(definition="b")
        c=Tag(definition="c")
        d=Tag(definition="d")
        a.save()
        b.save()
        c.save()
        d.save()

        a.implies.add(b)
        a.save()

        b.implies.add(c)
        b.implies.add(d)
        b.save()

        with self.subTest('leaf c'):
            s=c.expand_implied()
            self.assertTrue(len(s)==0)
        with self.subTest('leaf d'):
            s=d.expand_implied()
            self.assertTrue(len(s)==0)
        with self.subTest('intermediate'):
            s=b.expand_implied()
            self.assertTrue(len(s)==2)
            ids=[x.id for x in s]
            self.assertTrue(c.id in ids)
            self.assertTrue(d.id in ids)
            self.assertFalse(b.id in ids)
            self.assertFalse(a.id in ids)
        with self.subTest('root'):
            s=a.expand_implied()
            self.assertTrue(len(s)==3)
            ids=[x.id for x in s]
            self.assertTrue(c.id in ids)
            self.assertTrue(d.id in ids)
            self.assertTrue(b.id in ids)
            self.assertFalse(a.id in ids)
        with self.subTest("acyclic"):
            c.implies.add(a)
            with self.assertRaises(IntegrityError):
                c.save()
            



