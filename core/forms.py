from django import forms
from django.contrib.auth.models import User

from .models import SafeTrip, EmergencyContact, RouteFeedback, SafetySurvey

class RouteFeedbackForm(forms.ModelForm):
    class Meta:
        model = RouteFeedback
        fields = ['route_name', 'issue_category', 'what_went_wrong', 'suggested_alternative']
        widgets = {
            'route_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Route name (e.g. MG Road)'}),
            'issue_category': forms.Select(attrs={'class': 'form-control'}),
            'what_went_wrong': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'What went wrong?'}),
            'suggested_alternative': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Suggested better route'}),
        }

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']

class SafeTripForm(forms.ModelForm):
    class Meta:
        model = SafeTrip
        fields = ['route_name', 'start_point', 'end_point']
        widgets = {
            'route_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Home to Mall'}),
            'start_point': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Starting location'}),
            'end_point': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Destination'}),
        }

class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        fields = ['name', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
        }


class SafetySurveyForm(forms.ModelForm):
    class Meta:
        model = SafetySurvey
        fields = [
            'route_name', 'lighting_rating', 'crowd_level',
            'experienced_harassment', 'harassment_details',
            'experienced_teasing', 'teasing_details',
            'felt_unsafe', 'unsafe_details',
            'overall_safety_rating', 'time_of_travel', 'additional_comments'
        ]
        widgets = {
            'route_name': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'lighting_rating': forms.RadioSelect(),
            'crowd_level': forms.RadioSelect(),
            'experienced_harassment': forms.RadioSelect(),
            'harassment_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Please describe (optional)'}),
            'experienced_teasing': forms.RadioSelect(),
            'teasing_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Please describe (optional)'}),
            'felt_unsafe': forms.RadioSelect(),
            'unsafe_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'What made you feel unsafe? (optional)'}),
            'overall_safety_rating': forms.RadioSelect(),
            'time_of_travel': forms.RadioSelect(),
            'additional_comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any other feedback or suggestions?'}),
        }
