from django.db import models,IntegrityError
from sharedstrings import models as sharedstrings
from django.db.models import Lookup
# Create your models here.



class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    labels = models.ManyToManyField("TagLabel",related_name="+")
    canonical_label = models.ForeignKey("TagLabel",null=True,blank=True,on_delete=models.PROTECT,related_name="+")
    definition=models.CharField(max_length=256)
    implies = models.ManyToManyField("self",symmetrical=False,blank=True,related_name="implied_by",help_text="this &Implies; that")
    distinguish_from = models.ManyToManyField("self",symmetrical=True,blank=True, help_text="this ≠ that")
    conflicts_with = models.ManyToManyField("self",symmetrical=True,blank=True,help_text="x &#8853; y")

    class Cyclic(IntegrityError):pass

    def expand_implied(self,extra_fields=('canonical_label')):
        
        fields=['id','implies'].extend(extra_fields)
        expanded=self._expand_implied_r(root=self,root_ids=[],fields=extra_fields)
        return expanded
        
    def _expand_implied_r(self,root=None,expanded=None,expanded_ids=None,root_ids=None,fields=('id','implies')):

        expanded = set() if expanded is None else expanded
        expanded_ids = set() if expanded_ids is None else expanded_ids
        root_ids = list() if root_ids is None else root_ids

        if root is None:
            return expanded #should only happen if root passed in not in recursive step
        
        if root.id in root_ids:
            raise Tag.Cyclic((root,root_ids,expanded))
        else:
            root_ids.append(root.id)
        children=root.implies.all().only(fields)
        for t in children:
            if t.id in expanded_ids:
                continue
            else:
                expanded.add(t)
                expanded_ids.add(t.id)
                self._expand_implied_r(root=t,expanded=expanded,expanded_ids=expanded_ids,root_ids=root_ids,fields=fields)
        return expanded

    def __str__(self):
        return "{}({}) - {}".format(self.canonical_label,self.id,self.definition)

    
    def save(self,*args,**kwargs):
        #a new tag can't possibly be in a cycle because its autoincrement id has not been assigned
        if self.id is not None: 
            #This is an update
            self.expand_implied() #will raise Cyclic if cyclic
        super().save(*args,**kwargs)

class TagLabel(models.Model):
    label = models.CharField(max_length=64)
    language= models.ForeignKey("sharedstrings.Language",related_name="+",on_delete=models.DO_NOTHING)
    
    @property
    def definitions(self):
        return Tag.objects.filter(labels=self) | Tag.objects.filter(canonical_label=self)

    def __str__(self):
        return "{}.{}".format(self.language.isocode,self.label)

class Taggable(models.Model):
    tags=models.ManyToManyField("semantictags.Tag",blank=True)
    ambiguous_tags=models.ManyToManyField("sharedstrings.Strings",blank=True,related_name="+")

    class Meta:
        abstract=True