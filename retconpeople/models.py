from django.db import models
from django.db import transaction
from django.core.exceptions import ValidationError
from sharedstrings import models as sharedstrings
from semantictags import models as semantictags
from django.core.exceptions import ObjectDoesNotExist
import re
import uuid
# Create your models here.
# class Strings(models.Model):
#     id = models.AutoField(primary_key=True)
#     name = models.CharField()

class UrlPattern(models.Model):
    pattern = models.CharField(max_length=1024)
    website = models.ForeignKey("Website",on_delete=models.CASCADE,related_name='user_id_patterns')


class Website(models.Model):
    BRIEF_TRUNCATE_LENGTH=100 #TODO get from settings
    id = models.AutoField(primary_key=True)
    parent_site = models.ForeignKey("self",on_delete=models.DO_NOTHING,null=True,blank=True,related_name="child_sites")
    domain= models.CharField(max_length=256,help_text="e.g. twitter.com",unique=True)
    #A domain should consist only of tld and name not subdomain
    name = sharedstrings.SharedStringField()
    tld = sharedstrings.SharedStringField()
    user_id_format_string = models.CharField(max_length=1024,null=True,blank=True)
    description=models.CharField(max_length=255)
    tags=models.ManyToManyField("semantictags.Tag",related_name="+",blank=True)

    def save(self, *args, **kwargs):
        if self.tld is None:
            try:
                self.auto_replace_tld()
            except:
                pass #if tldextract not present silently fail or error
        if isinstance(self.name,str):
            value, created = sharedstrings.Strings.objects.get_or_create(name=self.name)
            self.name=value

        super().save(*args, **kwargs)  # Call the "real" save() method.
        
    def calculate_tld(self):
        import tldextract #this import is intentionally here as an optional requirement
        return tldextract.extract(self.domain).suffix

    def auto_replace_tld(self):
        value=self.calculate_tld()
        value, created = sharedstrings.Strings.objects.get_or_create(name=value)
        self.tld=value

    def substitute_username_pattern(self,args):
        raise NotImplementedError()
    def substitute_user_number_pattern(self,args):
        raise NotImplementedError()

    @classmethod
    def parse_url(cls,url):
        raise NotImplementedError()
        #get patterns test patterns
        #test
        #if is int produce a Usernummber
        #else produce a username
        #note this pair may already exist so get_or_create
    
    #TODO on save update url pattern cache
    @classmethod
    def reload_pattern_cache(cls):
        raise NotImplementedError()

    @classmethod
    def list_patterns(cls):
        raise NotImplementedError()

    def parent_site_name(self):
        '''Used for display in tabular views'''
        return self.parent_site.domain if self.parent_site else None

    def brief(self):
        s=self.description
        if len(self.description)>=self.BRIEF_TRUNCATE_LENGTH:
            s=s[:self.BRIEF_TRUNCATE_LENGTH]
            return s+'…'
        else:
            return s

    def __str__(self):
        return "{} ({})".format(self.name,self.domain)

class Person(models.Model):
    id = models.AutoField(primary_key=True)
    first_name=sharedstrings.SharedStringField(blank=True,null=True)
    last_name=sharedstrings.SharedStringField()
    pseudonyms = models.ManyToManyField("sharedstrings.Strings",related_name="+",blank=True)
    description=models.CharField(max_length=512,blank=True)
    merged_into=models.ForeignKey("self",related_name="merged_from",on_delete=models.DO_NOTHING,null=True,blank=True)
    distinguish_from = models.ManyToManyField("self",symmetrical=True,blank=True,help_text="Indicate people of similar names who should not be confused")
    tags=models.ManyToManyField("semantictags.Tag",related_name="+",blank=True)
    ambiguous_tags=models.ManyToManyField("sharedstrings.Strings",blank=True)

    uuid=models.UUIDField(default=uuid.uuid4,blank=True,unique=True)

    external_representation= models.ManyToManyField("remotables.ContentResource",related_name="+",blank=True)
    canonicalize=False

    def get_usernames(self):
        raise NotImplementedError()
        l=[]
        for c in self._collect_children():
            l.append(c.usernames)
        return l

    def _collect_children(self):
        l=[]
        for c in self.merges_from:
            l.append(c._collect_children())
            l.append(c)
        l.append(self)
        return l
        
    def _merge_into(self,target):
        if self.merged_into is None:
            self.merged_into = target
        else:
            raise ValueError("Merge cannot be performed because this model is already merged")

    def merge_with(self,target):
        if target.id < self.id: 
            self._merge_into(target)
        else:
            target._merge_into(self)
        
        target.save(update_fields=['merged_into'])
    
    def clean(self):

        #Cheap test first, aways need to do, doesn't hit db
        if self.merged_into_id is not None:
            if self.merged_into_id == self.id:
                raise ValidationError({'merged_into': ('Cannot merge into self')})
            if self.merged_into.merged_into.id is not None:
                raise ValidationError({'merged_into': ('Cannot merge into merged object')})

        if self.pk is not None:
            #this is an update
            if self.merged_into is not None:
                #django normally updates without select, but we need to select
                current = Person.objects.get(id=self.id)
                if  current.merged_into_id is not None:
                    if not self.canonicalize and  (current.merged_into_id !=self.merged_into_id):
                        raise ValidationError({'merged_into': ('Changing merge target violates integrity.')})
                    else:
                        #Do a long scan for the current name
                        target=self
                        visited=[]
                        while target.merged_into_id is not None:
                            visited.append(target.id)

                            #check both current and next id so we don't have to do unnecessary fetch
                            if target.id in visited or target.merged_into_id in visited:
                                raise ValidationError({'merged_into': ('Cycle detected:{}'.format(visited))})
                            target = target.merged_into
                        self.merged_into_id=target.id
    def initials(self):
        return self.first_name[0] if self.first_name else ""
    
    @property
    def formatted_name(self,shorten=False):
        if self.last_name is None:
            if self.first_name is not None:
                return self.first_name  
            else:
                try:
                    if self.pseudonyms.count()>0:
                        o= self.pseudonyms.all()[0]
                        return o.name
                except:
                    try:
                        un=self.usernames
                        u=un[0]
                        o=un.name.get()
                        return o.name
                    except:
                        return "?"
        else:
            if self.first_name is not None:
                if shorten:
                    "{}.{}".format(self.first_name[0].upper(),self.last_name)
                return "{}, {}".format(self.last_name,self.first_name)
    @property
    def brief(self,length=64,include_ellipsis=True):
        s=self.description
        if len(s)>length:
            if include_ellipsis:
                s=s[0:length-2]+u"…"
            else:
                s=s[0:length-1]
        return s
        
        

    def __str__(self):
        return "{}: {}".format(self.formatted_name,self.brief)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def pull_associated_works(self):
        raise NotImplementedError()
    def pull_associated_companies(self):
        raise NotImplementedError()

    def wanted_id_count(self):
        return self.usernames.filter(wanted=True).count()+self.user_numbers.filter(wanted=True).count()

    class DuplicateIdentityError(ValueError):
        def __init__(self,identities):
            self.identities=identities
    @classmethod
    def create_from_identifiers(cls,urls=[],user_identifiers=[],fail_on_missing_domain=True):
        '''returns (Created,Partial,Person,UserLabel[])'''
        try:
            person_created=False
            person_partial=False
            with transaction.atomic():
                name_sites=list(cls.urls_to_name_site_pair(urls))
                name_sites.extend(user_identifiers)
                pid = cls.search_by_identifiers(urls=[],user_identifiers=name_sites,expect_single=True)
                if len(pid)>0:
                    pid=pid[0]
                else:
                    person_created=True
                    pid=Person()
                    pid.save()
                
                for name,domain in name_sites:
                    
                    site=domain
                    if isinstance(site,str):
                        try:
                            site=Website.objects.get(domain=site)
                        except ObjectDoesNotExist as e:
                            if fail_on_missing_domain:
                                raise e
                            else:
                                person_partial=True
                                continue
                    
                    try:
                        name=int(name)
                        un,l_created=UserNumber.objects.get_or_create(number=name,website=site)
                        un.save()
                        pid.user_numbers.add(un)
                        
                        
                    except ValueError:
                        ns,l_created=sharedstrings.Strings.objects.get_or_create(name=name)
                        ns.save()
                        un,l_created=UserName.objects.get_or_create(name=ns,website=site)
                        un.save()
                        pid.usernames.add(un)
                        
                pid.save()
            return (person_created,person_partial,pid)

        except Person.DuplicateIdentityError as e:
            raise e

    @classmethod
    def urls_to_name_site_pair(cls,urls=[]):
        
        if len(urls)>0:
            user_url_patterns= UrlPattern.objects.all()
            #TODO maybe optimal to filter domainname first at scale

            for p in user_url_patterns:
                
                #NB match only looks at the start of the string but this is optimal
                #since we're looking at full urls
                for url in urls:
                    out=re.match(re.compile(p.pattern),url)
                    if out is None:
                        continue
                    name=out.group(1)
                    try:
                        name=int(name)
                        t=(name,p.website)
                        yield t
                    except:
                        t=(name,p.website)
                        yield t
        
    
        
    
    @classmethod
    def search_by_identifiers(cls,urls=[],user_identifiers=[],expect_single=False):
        '''Search for persons with identities exiting early if duplicating and expect_single'''
        identities=set()
        names=set()

        for name,domain_name in user_identifiers:
            try:
                try:
                    name=int(name)
                    if isinstance(domain_name,Website):
                        un=UserNumber.objects.get(number=name,website=domain_name)
                    else:
                        un=UserNumber.objects.get(number=name,website__domain=domain_name)
                except ValueError:
                    if isinstance(domain_name,Website):
                        un=UserName.objects.get(name__name=name,website=domain_name)
                    else:
                        un=UserName.objects.get(name__name=name,website__domain=domain_name)
            except ObjectDoesNotExist:
                #Found no such pair
                continue

            identities.add(un.belongs_to)
            if expect_single and len(identities)>1:
                raise Person.DuplicateIdentityError(list(identities))
        
        if len(urls)>0:
            user_url_patterns=UrlPattern.objects.all()
            #TODO maybe optimal to filter domainname first at scale

            for p in user_url_patterns:
                #NB match only looks at the start of the string but this is optimal
                #since we're looking at full urls
                regex=re.compile(p.pattern)

                for url in urls:
                    #do regex match to extract site and identifier.
                    out=re.match(regex,url)
                    if out is None:
                        continue
                    
                    name=out.group(1)
                    try:
                        name=int(name)
                        un=UserNumber.objects.get(number=name,website=p.website)
                    except ObjectDoesNotExist:
                            #The regex matched, but no identity,keep looking at the other urls
                            pass
                    except ValueError:
                        try:
                            un=UserName.objects.get(name=name,website=p.website)
                            identities.add(un.belongs_to)
                        except ObjectDoesNotExist:
                            #The regex matched, but no identity,keep looking at the other urls
                            pass
                    if expect_single and len(identities)>1:
                        raise Person.DuplicateIdentityError(list(identities))
        #sanity check
        if expect_single and len(identities)>1:
                raise Person.DuplicateIdentityError(list(identities))
        return list(identities)

    class Meta:
        # ordering=['id']
        pass


class UserLabel(models.Model):
    #TODO django3
    # class Roles(models.IntegerChoices):
    #     SFW=0
    #     NSFW=1
    #     NSFW_EXTRME=2
    # class Status(models.IntegerChoice):
    #     ACTIVE=0
    #     INNACTIVE=1
    #     DEAD=2
    ROLES=(
        (None,""),
        (0,"SFW"),
        (1,"NSFW"),
        (2,"NSFW Extreme")
    )
    STATUS=(
        (None,""),
        (0,"Active"),
        (1,"Inactive"),
        (2,"Dead")
    )
    status=models.IntegerField(choices=STATUS,null=True,default=None,blank=True)
    role=models.IntegerField(choices=ROLES,null=True,default=None,blank=True)
    wanted = models.BooleanField(null=True,blank=True)
    class Meta:
        abstract=True

class UserName(UserLabel):
    id = models.AutoField(primary_key=True)
    website=models.ForeignKey("Website",related_name="user_names",on_delete=models.PROTECT,null=False)
    name = sharedstrings.SharedStringField(null=False)
    tags=models.ManyToManyField("semantictags.Tag",related_name="+")
    belongs_to=models.ForeignKey("Person",related_name='usernames',on_delete=models.CASCADE,null=True,blank=True)

    def get_url(self):
        raise NotImplementedError()
    
    def __str__(self):
        return "{}@{}".format(self.name,str(self.website))

    class Meta:
        unique_together = ['website', 'name']

class UserNumber(UserLabel):
    id = models.AutoField(primary_key=True)
    website=models.ForeignKey("Website",related_name="user_numbers",on_delete=models.CASCADE)
    number = models.BigIntegerField()
    belongs_to=models.ForeignKey("Person",related_name='user_numbers',on_delete=models.DO_NOTHING,null=True,blank=True)

    class Meta:
        unique_together = ['website', 'number']
    
    def __str__(self):
        return str(self.number)

# class UserIdentifierManager(models.Manager):
#     pass

# class UserIdentifier(models.Model):
#     objects= UserIdentifierManager()
#     def get_usernumber(self):
#         try:
#             name = int(self.name)
#             return name
#         except:
#             return False
#         raise Exception("It shouldn't be possible to reach this line")
        

#     class Meta:
#         unmanaged=True