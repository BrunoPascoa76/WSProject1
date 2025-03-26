# forms.py

from django import forms

class CharacterForm(forms.Form):
    label = forms.CharField(max_length=100)
    species = forms.CharField(max_length=100)
    homeworld = forms.CharField(max_length=100)
    gender = forms.CharField(max_length=10)
    hair_color = forms.CharField(max_length=20)
    eye_color = forms.CharField(max_length=20)
    skin_color = forms.CharField(max_length=20)
    description = forms.CharField(widget=forms.Textarea)
    height = forms.FloatField()
    weight = forms.FloatField()
    year_born = forms.IntegerField()
    year_died = forms.IntegerField()
