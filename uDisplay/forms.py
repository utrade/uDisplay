"""
   uDisplay/forms.py
   Login page form
   Created by Mayank Jain
"""

from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=254, label="Username", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
