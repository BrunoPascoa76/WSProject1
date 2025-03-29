# forms.py

from django import forms

class CharacterAttributesForm(forms.Form):
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

class CharacterRelationsForm(forms.Form):
    species = forms.ChoiceField(choices=[], widget=forms.RadioSelect)  # Use RadioSelect for clickable options
    homeworld = forms.ChoiceField(choices=[], widget=forms.RadioSelect)  # Use RadioSelect for clickable options

    def __init__(self, *args, **kwargs):
        available_species = kwargs.pop('available_species', [])
        available_homeworlds = kwargs.pop('available_homeworlds', [])
        super().__init__(*args, **kwargs)

         # Populate species choices dynamically
        self.fields['species'].choices = [(species_url, species_data['name']) for species_url, species_data in available_species.items()]
        
        # Populate homeworld choices dynamically
        self.fields['homeworld'].choices = [(planet_url, planet_data['name']) for planet_url, planet_data in available_homeworlds.items()]

class CharacterInsertForm(forms.Form):
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
