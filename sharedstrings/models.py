from django.db import models
from django import forms
from django.contrib.admin.widgets import AutocompleteMixin
# Create your models here.


class Strings(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return '{}'.format(self.name)



class Language(models.Model):
    '''
    List of languages by iso code (2 letter only because country code
    is not needed.
    This should be popluated by getting data from django.conf.locale.LANG_INFO
    '''
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256,
                            null=False,
                            blank=False,
                            verbose_name=('Language name')
                            )
    name_local = models.CharField(max_length=256,
                                  null=False,
                                  blank=True,
                                  default='',
                                  verbose_name=('Language name (in that language)'))
    isocode = models.CharField(max_length=7,
                               null=False,
                               blank=False,
                               unique=True,
                               verbose_name=('ISO 639-1 Language code'),
                               help_text=(
                                   '2 character language code without country')
                               )
    sorting = models.PositiveIntegerField(blank=False,
                                          null=False,
                                          default=0,
                                          verbose_name=('sorting order'),
                                          help_text=(
                                              'increase to show at top of the list')
                                          )

    def __str__(self):
        return '%s (%s)' % (self.name, self.name_local)

    class Meta:
        verbose_name = ('language')
        verbose_name_plural = ('languages')
        ordering = ('-sorting', 'name', 'isocode', )


class SharedStringTextInput(forms.TextInput):
    def __init__(self, *args, **kwargs):
        self.choices = []
        super().__init__(*args, **kwargs)

    class Media:
        js = ('jquery-1.12.4.js',
              'jquery-ui.min.js',
              'sharedstringfield.js')
        css = {
            'all': ('sharedstringfield.css', 'jquery-ui.css')
        }


class SharedStringFormField(forms.CharField):
    widget = SharedStringTextInput

    def __init__(self, queryset, *, empty_label='---------', required=True, widget=None, label=None, initial=None, help_text='', to_field_name=None, limit_choices_to=None, **kwargs):
        super().__init__(max_length=None, min_length=None, strip=True,
                         empty_value='',required=required, widget=SharedStringTextInput, **kwargs)
        # super().__init__(queryset, *, empty_label=empty_label, required=required, widget=widget, label=label, initial=initial, help_text=help_text, to_field_name=to_field_name, limit_choices_to=limit_choices_to, **kwargs)

    def widget_attrs(self, widget):
        from rest_framework.reverse import reverse
        attrs = super().widget_attrs(widget)
        if self.max_length is not None and not widget.is_hidden:
            # The HTML attribute is maxlength, not max_length.
            attrs['maxlength'] = str(self.max_length)
        if self.min_length is not None and not widget.is_hidden:
            # The HTML attribute is minlength, not min_length.
            attrs['minlength'] = str(self.min_length)
        c = attrs['class'] if 'class' in attrs else ''
        attrs['class'] = c+" autocompleteInput"
        attrs['autocomplete-source'] = reverse('strings-list')
        return attrs

    # def prepare_value(self, value):
    #     return super().prepare_value(Strings.objects.get(value).name)

    def to_python(self, value):
        if isinstance(value, str):
            if len(value) ==0:
                return None
            value, created = Strings.objects.get_or_create(name=value)
        return value

    def prepare_value(self, value):
        if value is None:
            return value
        elif  isinstance(value,int): 
                obj = Strings.objects.get(pk=int(value))
                return obj.name
        elif isinstance(value,str):
            if len(value)==0:
                return None
        return value


class SharedStringField(models.ForeignKey):
    def __init__(self, **kwargs):
        d = {'to': "sharedstrings.Strings",'related_name': "+",'on_delete': models.PROTECT}
        if 'blank' not in kwargs: d['blank'] = True 
        if 'null' not in kwargs: d['null'] = True
        kwargs.update(d)
        super().__init__(**kwargs)

    def formfield(self, **kwargs):
            # This is a fairly standard way to set up some defaults
            # while letting the caller override them.
        defaults = {'form_class': SharedStringFormField}
        defaults.update(kwargs)
        d= super().formfield(**defaults)
        d.required=not self.blank
        return d

    def to_python(self, value):
        
        if value is None:
            return super().to_python(None)
        if isinstance(value,int):
            return super().to_python(value)

        
        if isinstance(value, str):
            if len(value)==0:
                return super().to_python(None)
            value, created = Strings.objects.get_or_create(name=value)
        return super().to_python(value)

    def get_prep_value(self, value):

        if isinstance(value, str):
            value, created = Strings.objects.get_or_create(name=value)
            return super().get_prep_value(value)
        return super().get_prep_value(value)

    
    def get_lookup(self, lookup_name):
        if lookup_name == 'icontains':
            return SurrogateIContainsStringLookup
        if lookup_name == 'contains':
            return SurrogateContainsStringLookup
        if lookup_name == 'exact':
            return SurrogateExactStringLookup
        
        else:
            return super().get_lookup(lookup_name)
        # surrogate=Strings._meta.get_field('name')
        # l=surrogate.get_lookup(lookup_name)
        # return l
class SurrogateIContainsStringLookup(models.lookups.In):
    
    def __init__(self,lhs,rhs, *kwargs):
        self.params=[]
        rhs= [x.id for x in Strings.objects.filter(name__icontains=rhs).distinct()]
        return super().__init__(lhs,rhs,*kwargs)

    lookup_name = 'icontains'

class SurrogateContainsStringLookup(models.lookups.In):
    
    def __init__(self,lhs,rhs, *kwargs):
        self.params=[]
        rhs= [x.id for x in Strings.objects.filter(name__icontains=rhs).distinct()]
        return super().__init__(lhs,rhs,*kwargs)

    lookup_name = 'contains'

class SurrogateExactStringLookup(models.lookups.In):
    
    def __init__(self,lhs,rhs, *kwargs):
        self.params=[]
        rhs= [x.id for x in Strings.objects.filter(name=rhs).distinct()]
        return super().__init__(lhs,rhs,*kwargs)

    lookup_name = 'exact'