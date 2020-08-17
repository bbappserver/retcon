from .models import Episode
from django import forms
from django.db import transaction

# class EpisodeForm(forms.ModelForm):
#     class Meta:
#         model = Episode
class BulkCreateEpisodeForm(forms.ModelForm):
    start_index= forms.IntegerField()
    end_index = forms.IntegerField()
    class Meta:
        model = Episode
        fields=['medium','part_of']

    def save(self,commit=False):
        with transaction.atomic():
            d=self.cleaned_data
            for i in range(d['start_index'],d['end_index']):
                self.order_in_series=i
                super().save(commit=commit)


