from django.db import models
from django.conf import settings
import django.utils
import django.core
from sharedstrings import models as sharedstrings
from retconpeople import models as people
from semantictags import models as semantictags
# Create your models here.

class Genre(models.Model):
    name = sharedstrings.SharedStringField()
    decription= models.CharField(max_length=128)
    parent = models.ForeignKey("self",null=True,blank=True,on_delete=models.DO_NOTHING)
    def __str__(self):
        return '{}'.format(self.name)
    class Meta:
        ordering = ('name',)

class Company(semantictags.Taggable):
    id = models.AutoField(primary_key=True)
    name=sharedstrings.SharedStringField()
    # name = models.ForeignKey("sharedstrings.Strings",related_name="+",on_delete=models.DO_NOTHING)
    case_sensitive_name = models.BooleanField()

    parent=models.ForeignKey("self",on_delete=models.DO_NOTHING,null=True,blank=True,related_name="children")
    website = models.ForeignKey("retconpeople.Website",on_delete=models.DO_NOTHING,null=True,blank=True)

    def __str__(self):
        return self.name.name

class Title(models.Model):
    name = models.CharField(max_length=64)
    language = models.ForeignKey("sharedstrings.Language",on_delete=models.SET_NULL,null=True,related_name="+")
    creative_work= models.ForeignKey("CreativeWork",on_delete=models.CASCADE,related_name="localized_titles")

class CreativeWork(semantictags.Taggable):
    name = models.CharField(max_length=64)
    published_on=models.DateField(null=True,blank=True)
    published_by = models.ManyToManyField("Company",blank=True,related_name='published_%(class)s')
    created_by = models.ForeignKey("retconpeople.Person",on_delete=models.PROTECT,null=True,blank=True,related_name="+")
    # representes_collections = models.ManyToManyField('retconstorage.Collection')
    # representes_remotables = models.ManyToManyField('retconremotables.RemoteEntity')
    def local_name(self,language=django.utils.translation.get_language()):
        try:
            short_code=language[:2]
            return Title.objects.get(language__isocode=short_code,creative_work=self).name
        except django.core.exceptions.ObjectDoesNotExist:
            return None
    
    def preferred_name(self,language=django.utils.translation.get_language()):
        n=self.local_name(language=language)
        if n is None:
            return self.name
        return n


class Series(CreativeWork):
    parent_series = models.ForeignKey("self",blank=True,null=True,on_delete=models.PROTECT,related_name='child_series')
    related_series = models.ManyToManyField("self", through='RelatedSeries',symmetrical=False,through_fields=('from_series', 'to_series'),related_name='related_from_series')

    produced_by = models.ManyToManyField("Company",blank=True,related_name='produced')
    

    def __str__(self):
        if self.published_on is not None:
            return "{}({})".format(self.preferred_name(),self.published_on.year)
        else:
            return "{}(Unknown Year)".format(self.preferred_name(),)
    
    class Meta:
        verbose_name_plural = "series"

class RelatedSeries(models.Model):
    RELATIONS=(
        (0,'adaptation'),
        (1,'spinoff'),
        (2,'sequel')
    )
    to_series=models.ForeignKey("Series",on_delete=models.DO_NOTHING)
    from_series=models.ForeignKey("Series",related_name='based_off',on_delete=models.DO_NOTHING)
    relationship=models.PositiveSmallIntegerField(choices=RELATIONS,help_text='e.g. <to_work> is a sequel to <from_work>')    

class Episode(CreativeWork):

    #Mediums, sorted approximatly by year introduced
    ANTHOLOGY=0
    BOOK=1 #Any written media that is not an anthology
    AUDIO=2 #Songs to radioplays
    COMIC_BOOK=3 #Includes manga
    MOVIE=4 #Self contained film
    TV=5 #Anthology of film meant for broadcast
    SOFTWARE=6 #Software which is not explcitly a video game
    VIDEO_GAME=7
    WEBCOMIC=8 #Comics published as a web anthology
    WEBSERIES=9 #e.g. a series of youtube videos

    MEDIUM_CHOICES = [
        (ANTHOLOGY,"Anthology"),
        (AUDIO,"Audio"),
        (COMIC_BOOK,"Comic book / Manga"),
        (BOOK,"Book"),
        (MOVIE,"Movie"),
        (SOFTWARE,"Software"),
        (TV,"Television"),
        (VIDEO_GAME,"Video Game"),
        (WEBCOMIC,"Webcomic"),
        (WEBSERIES,"Webseries")
    ]
    #End mediums


    part_of=models.ForeignKey("Series",on_delete=models.DO_NOTHING,null=True)
    order_in_series=models.PositiveSmallIntegerField(null=True,blank=True)
    medium= models.PositiveSmallIntegerField(choices=MEDIUM_CHOICES)

    class Meta:
        unique_together=[('part_of','order_in_series')]

    def __str__(self):
        return self.preferred_name()

class Book(Episode):
    authors = models.ManyToManyField('retconpeople.Person')
    pass

class Illustration(CreativeWork):
    illustrators = models.ManyToManyField('retconpeople.Person')

class Comicbook(Book):
    pass

class AudioBook(CreativeWork):
    reading_of=models.ForeignKey("Book",on_delete=models.DO_NOTHING)

class Movie(Episode):
    pass

class TVEpisode(Movie):
    pass

class Software(Episode):
    SFT_PLATFORM_HELP='Platforms this sofware runs on including consoles and operating systems'
    platforms= models.ManyToManyField('self',blank=True,related_name='+',help_text=SFT_PLATFORM_HELP)
    pass

class WebVideo(Episode):
    pass

class Actor(people.Person):
    acted_in = models.ManyToManyField("Episode")

#class Author(people.Person):

    #Authors may have a single colection designetd as tjings they have authored
    #This is only good for fuzzy authorship, and sould ideally not benecessary so we'll leave 
    # It commented out until we're sure there is a usecase.
    #authorshipCollection = models.OneToOneField('retconstorage.Collection')
