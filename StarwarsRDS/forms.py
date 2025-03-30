# forms.py

from django import forms

class CharacterForm(forms.Form):
    label = forms.CharField(max_length=100, label="Name")
    gender = forms.CharField(max_length=10, label="Gender")
    hair_color = forms.CharField(max_length=20, label="Hair Color",required=False)
    eye_color = forms.CharField(max_length=20, label="Eye Color",required=False)
    skin_color = forms.CharField(max_length=20, label="Skin Color",required=False)
    description = forms.CharField(widget=forms.Textarea, label="Description")
    height = forms.FloatField(label="Height (cm)",required=False)
    weight = forms.FloatField(label="Weight (kg)",required=False)
    year_born = forms.IntegerField(label="Year Born",required=False)
    year_died = forms.IntegerField(label="Year Died", required=False)
    species=forms.CharField(max_length=100,label="Species",required=False)
    homeworld=forms.CharField(max_length=100,label="Homeworld",required=False)