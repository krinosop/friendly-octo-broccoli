from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Play, Director, Actor, Casting, Performance, ActorRole, GENRE_CHOICES

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            from django.contrib.auth.models import Group
            role = self.cleaned_data['role']
            if role == 'actor':
                group = Group.objects.get(name='Actor')
            elif role == 'director':
                group = Group.objects.get(name='Director')
            else:
                group = Group.objects.get(name='Administrator')
            user.groups.add(group)
        return user

class PlayForm(forms.ModelForm):
    genre = forms.ChoiceField(
        choices=GENRE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Play
        fields = ['title', 'director', 'genre', 'duration', 'description', 'venue_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'director': forms.Select(attrs={'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'venue_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

class DirectorForm(forms.ModelForm):
    class Meta:
        model = Director
        fields = ['first_name', 'last_name', 'date_of_birth', 'gender', 'years_of_experience', 'contact_info']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

class ActorForm(forms.ModelForm):
    class Meta:
        model = Actor
        fields = ['first_name', 'last_name', 'date_of_birth', 'gender', 'contact_info']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

class CastingForm(forms.ModelForm):
    class Meta:
        model = Casting
        fields = ['actor', 'play', 'role', 'casting_date', 'status']
        widgets = {
            'casting_date': forms.DateInput(attrs={'type': 'date'}),
        }

class PerformanceForm(forms.ModelForm):
    actors = forms.ModelMultipleChoiceField(
        queryset=Actor.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Performance
        fields = ['play', 'date', 'status', 'tickets_available', 'ticket_price', 'actors']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def save(self, commit=True):
        performance = super().save(commit=False)
        if commit:
            performance.save()
            if self.cleaned_data.get('actors'):
                performance.actors.set(self.cleaned_data['actors'])
        return performance

class ActorRoleForm(forms.ModelForm):
    class Meta:
        model = ActorRole
        fields = ['actor', 'play', 'role_name'] 