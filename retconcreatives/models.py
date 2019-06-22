from django.db import models
from sharedstrings import models as sharedstrings
from retconpeople import models as people
from semantictags import models as semantictags
# Create your models here.

class Studio(semantictags.Taggable):
    id = models.AutoField(primary_key=True)
    name = models.ForeignKey("sharedstrings.Strings",related_name="+",on_delete=models.DO_NOTHING)
    case_sensitive_name = models.BooleanField()

    parent_studio=models.ForeignKey("self",on_delete=models.DO_NOTHING,null=True,related_name="child_studios")
    website = models.ForeignKey("retconpeople.Website",on_delete=models.DO_NOTHING,null=True)

class CreativeWork(semantictags.Taggable):
    published_on=models.DateTimeField(null=True)

class Series(semantictags.Taggable):
    pass

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


    name = models.ForeignKey("sharedstrings.Strings",on_delete=models.DO_NOTHING)
    part_of=models.ForeignKey("Series",on_delete=models.DO_NOTHING,null=True)
    previous_episode=models.ForeignKey("self",on_delete=models.DO_NOTHING,null=True,related_name="next_episode")
    medium= models.PositiveSmallIntegerField(choices=MEDIUM_CHOICES)

class Book(Episode):
    pass

class Comicbook(Book):
    pass

class AudioBook(CreativeWork):
    reading_of=models.ForeignKey("Book",on_delete=models.DO_NOTHING)

class Movie(Episode):
    pass

class TVEpisode(Movie):
    pass

class Software(Episode):
    pass

class WebVideo(Episode):
    pass

class Actor(people.Person):
    acted_in = models.ManyToManyField("Episode")
