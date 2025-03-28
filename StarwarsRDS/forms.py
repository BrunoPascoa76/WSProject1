# forms.py

from django import forms

class CharacterForm(forms.Form):
    label = forms.CharField(max_length=100, label="Name")
    gender = forms.CharField(max_length=10, label="Gender")
    hair_color = forms.CharField(max_length=20, label="Hair Color")
    eye_color = forms.CharField(max_length=20, label="Eye Color")
    skin_color = forms.CharField(max_length=20, label="Skin Color")
    description = forms.CharField(widget=forms.Textarea, label="Description")
    height = forms.FloatField(label="Height (cm)")
    weight = forms.FloatField(label="Weight (kg)")
    year_born = forms.IntegerField(label="Year Born")
    year_died = forms.IntegerField(label="Year Died", required=False)
    species=forms.CharField(max_length=100,label="Species",required=False)
    homeworld=forms.CharField(max_length=100,label="Homeworld",required=False)