from django import forms
from semantictags import models
class OpinionForm(forms.Form):
    
    CHOICES=[[None,"-"],[True,"Like"],[False,"Dislike"]]
    opinion = forms.Select(choices=CHOICES)

    tags= forms.ModelMultipleChoiceField(models.Tag)
