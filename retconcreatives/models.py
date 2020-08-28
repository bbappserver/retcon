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
    parent = models.ForeignKey("self",null=True,blank=True,on_delete=models.PROTECT)
    def __str__(self):
        return '{}'.format(self.name)
    class Meta:
        ordering = ('name',)

class Company(semantictags.Taggable):
    id = models.AutoField(primary_key=True)
    name=sharedstrings.SharedStringField()
    # name = models.ForeignKey("sharedstrings.Strings",related_name="+",on_delete=models.PROTECT)
    case_sensitive_name = models.BooleanField(null=False,blank=False,default=False)

    parent=models.ForeignKey("self",on_delete=models.PROTECT,null=True,blank=True,related_name="children")
    website = models.ForeignKey("retconpeople.Website",on_delete=models.PROTECT,null=True,blank=True)
    defunct = models.BooleanField(null=True,blank=True)
    external_representation= models.ManyToManyField("remotables.ContentResource",related_name="+",blank=True)

    def __str__(self):
        return self.name.name
    
    def pull_associated_people(self):
        raise NotImplementedError()
    
    def pull_associated_works(self):
        raise NotImplementedError()

    class Meta:
        ordering=['name__name']

class Title(models.Model):
    name = models.CharField(max_length=64)
    language = models.ForeignKey("sharedstrings.Language",on_delete=models.SET_NULL,null=True,related_name="+")
    creative_work= models.ForeignKey("CreativeWork",on_delete=models.CASCADE,related_name="localized_titles")

class CreativeWork(semantictags.Taggable):

    DATE_PRECISION_YEAR='y'
    DATE_PRECISION_MONTH='m'
    DATE_PRECISION_DAY='d'

    DATE_PRECISION_CHOICES=(
        (DATE_PRECISION_YEAR,'Year'),
        (DATE_PRECISION_MONTH,'Month'),
        (DATE_PRECISION_DAY,'Day')
    )
    name = models.CharField(max_length=64)
    published_on=models.DateField(null=True,blank=True)
    published_on_precision=models.CharField(max_length=1,blank=True,null=True,choices=DATE_PRECISION_CHOICES)
    published_by = models.ManyToManyField("Company",blank=True,related_name='published_%(class)s')
    created_by = models.ForeignKey("retconpeople.Person",on_delete=models.PROTECT,null=True,blank=True,related_name="+")
    # representes_collections = models.ManyToManyField('retconstorage.Collection')
    # representes_remotables = models.ManyToManyField('retconremotables.RemoteEntity')
    external_representation= models.ManyToManyField("remotables.ContentResource",related_name="+",blank=True)
    files= models.ManyToManyField("retconstorage.ManagedFile",related_name="+",blank=True)

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

    @classmethod
    def fuzzy_search(cls,fuzzy_name):
        '''Returns a dictionary of <Creativework.id,hit_count>'''
        tokens=fuzzy_name.split(" ")
        res={}
        for t in tokens:
            for x in cls.objects.filter(name__icontains=t):
                if x.id in res:
                    res[x]+=1
                else:
                    res[x]=1
        return x
    
    def publisher_names(self):
        return [x.name for x in self.published_by.all()]
    
    def clean(self):
        # Don't allow draft entries to have a pub_date.
        if self.published_on is not None and self.published_on_precision is None:
            raise ValidationError(_('If a work has a publication date it must also have a precision.'))
        if self.published_on is None and self.published_on_precision is not None:
            raise ValidationError(_("Must specify a date for publication precision,for don't care use any valid number e.g 01"))
        
    # class Meta:
    #     constraints = [
    #         models.CheckConstraint(check=(models.Q(published_on=None, published_on_precision=None)|models.Q(published_on__isnull=False,published_on_precision__isnull=False)), name='date_and_precision'),
    #     ]


class Series(CreativeWork):

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
    CARTOON=10
    WEBCARTOON=11
    MEDIUM_CHOICES = [
        (ANTHOLOGY,"Anthology"),
        (AUDIO,"Audio"),
        (COMIC_BOOK,"Comic book / Manga"),
        (BOOK,"Book"),
        (MOVIE,"Movie"),
        (SOFTWARE,"Software"),
        (TV,"Television"),
        (CARTOON,"Cartoon / Anime"),
        (VIDEO_GAME,"Video Game"),
        (WEBCOMIC,"Webcomic"),
        (WEBSERIES,"Webseries"),
        (WEBCARTOON,"Web Cartoon")
    ]

    parent_series = models.ForeignKey("self",blank=True,null=True,on_delete=models.PROTECT,related_name='child_series')
    related_series = models.ManyToManyField("self", through='RelatedSeries',symmetrical=False,through_fields=('from_series', 'to_series'),related_name='related_from_series')

    produced_by = models.ManyToManyField("Company",blank=True,related_name='produced')
    medium= models.PositiveSmallIntegerField(choices=MEDIUM_CHOICES,null=True,blank=True)

    #finished_publication= models.BooleanField(null=True,blank=True)
    

    def __str__(self):
        if self.published_on is not None:
            return "{}({})".format(self.preferred_name(),self.published_on.year)
        else:
            return "{}(Unknown Year)".format(self.preferred_name(),)
    
    def save(self, *args, **kwargs):

        #check for cycles
        cur=self
        while cur.parent_series_id is not None:
            if cur.parent_series_id == self.id: #This is intentionally lazy so we don't have to join
                raise django.db.IntegrityError("A series parent chain may not form a cycle.")
            cur=cur.parent_series

        #only reached on no cycle
        super().save(*args, **kwargs)  # Call the "real" save() method.


    class Meta:
        verbose_name_plural = "series"

class RelatedSeries(models.Model):
    RELATIONS=(
        (0,'adaptation'),
        (1,'spinoff'),
        (2,'sequel')
    )
    to_series=models.ForeignKey("Series",on_delete=models.PROTECT)
    from_series=models.ForeignKey("Series",related_name='based_off',on_delete=models.PROTECT)
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
    CARTOON=10
    WEBCARTOON=11

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
        (WEBSERIES,"Webseries"),
        (WEBCARTOON,"Web Cartoon")
    ]
    #End mediums


    part_of=models.ForeignKey("Series",on_delete=models.PROTECT,null=True,blank=True,related_name='episodes')
    order_in_series=models.PositiveSmallIntegerField(null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    medium= models.PositiveSmallIntegerField(choices=MEDIUM_CHOICES)

    #cover_images= models.ManyToManyField("retconstorage.ManagedFile",related_name="+",blank=True)
    #promotional_images= models.ManyToManyField("retconstorage.ManagedFile",related_name="+",blank=True)

    class Meta:
        unique_together=[('part_of','order_in_series')]

    def __str__(self):
        return self.preferred_name()

#TODO MIGRATE MEDIUMS TO SUBTYPES
class Recording(Episode):
    production_number=models.IntegerField(null=True,blank=True)

class Writing(Episode):
    authors = models.ManyToManyField('retconpeople.Person')
    class Meta:
        abstract=True

class Book(Writing):
    pass

class Software(Episode):
    SFT_PLATFORM_HELP='Platforms this sofware runs on including consoles and operating systems'
    platforms= models.ManyToManyField('self',blank=True,related_name='+',help_text=SFT_PLATFORM_HELP)
    pass

class Illustration(CreativeWork):
    illustrators = models.ManyToManyField('retconpeople.Person')

class Comicbook(Book):
    pass

class AudioBook(CreativeWork):
    reading_of=models.ForeignKey("Book",on_delete=models.PROTECT)

class MovieManager(models.Manager):
    def get_queryset(self):
        return super(MovieManager, self).get_queryset().filter(
            medium=Episode.MOVIE)

class Movie(Episode):
    objects=MovieManager()
    def __init__(self,*args,**kwargs):
        kwargs['medium']=Episode.MOVIE
        super().__init__(*args,**kwargs)
    class Meta:
        proxy=True

class TVEpisode(Episode):
    class Meta:
        proxy=True


class WebVideo(Recording):
    pass

class Franchise(models.Model):
    name = sharedstrings.SharedStringField()
    description = models.CharField(max_length=64)

class Character(models.Model):
    name = sharedstrings.SharedStringField()
    description = models.CharField(max_length=64)
    franchise = models.ForeignKey("Franchise",on_delete=models.SET_NULL,null=True,blank=True)

    def __str__(self):
        return "{}:{}".format(self.name,self.description)


class Portrayal(models.Model):
    episode = models.ForeignKey("Episode",on_delete=models.PROTECT)
    actor = models.ForeignKey("retconpeople.Person",on_delete=models.PROTECT)
    role = models.ForeignKey("Character",on_delete=models.SET_NULL,null=True,blank=True)

#class Author(people.Person):

    #Authors may have a single colection designetd as tjings they have authored
    #This is only good for fuzzy authorship, and sould ideally not benecessary so we'll leave 
    # It commented out until we're sure there is a usecase.
    #authorshipCollection = models.OneToOneField('retconstorage.Collection')

