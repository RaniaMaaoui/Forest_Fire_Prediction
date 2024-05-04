from django         import forms
from client.models  import Client


class ClientForm(forms.ModelForm):  
    password_confirmation = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm Password",
        required= True
    )

    class Meta:
        model = Client
        fields = ['firstName', 'lastName', 'email', 'phone', 'username', 'password', 'image']
        widgets = {
            'firstName': forms.TextInput(   attrs={'class': 'form-control', 'placeholder': 'First Name', 'required': 'True'}),
            'lastName': forms.TextInput(    attrs={'class': 'form-control', 'placeholder': 'Last Name', 'required': 'True'}),
            'email': forms.EmailInput(      attrs={'class': 'form-control', 'placeholder': 'Email Address', 'required': 'True'}),
            'phone': forms.TextInput(       attrs={'class': 'form-control', 'placeholder': 'Phone Number', 'required': 'True'}),
            'username': forms.TextInput(    attrs={'class': 'form-control', 'placeholder': 'Username', 'required': 'True'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'required': 'True'}),
            'image': forms.FileInput(       attrs={'class': 'form-control-file'})
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("password_confirmation")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data


    def clean_email(self):
            email = self.cleaned_data.get('email')
            if Client.objects.filter(email=email).exists():
                raise forms.ValidationError("This email is already in use.")
            return email
