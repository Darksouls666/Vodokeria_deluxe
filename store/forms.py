from django import forms
from .models import CustomerRegister
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SesionForm(forms.ModelForm):
    
    class Meta:
        model = CustomerRegister
        fields = '__all__'

# PRUEBAS DE INICIO DE SESION

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', "email", "password1", "password2"]