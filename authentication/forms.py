from django import forms
from supervisor.models import Supervisor
from django.contrib.auth.hashers import check_password

class SupervisorLoginForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'id': 'email',
                'name': 'email',
                'placeholder': 'Email',
                'class': 'login__input'
            }
        )
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'id': 'password',
                'name': 'password',
                'placeholder': 'Password',
                'class': 'login__input'
            }
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            try:
                supervisor = Supervisor.objects.get(email=email)
            except Supervisor.DoesNotExist:
                raise forms.ValidationError("Invalid email or password!!!")

            if not check_password(password, supervisor.password):
                raise forms.ValidationError("Invalid email or password!!!")
        
        return cleaned_data
