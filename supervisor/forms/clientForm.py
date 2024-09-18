from django         import forms
from client.models  import Client

class ClientForm(forms.ModelForm):
    password_confirmation = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm Password",
        required=False  # Make this optional
    )

    class Meta:
        model = Client
        fields = ['firstName', 'lastName', 'email', 'phone', 'username', 'password', 'image']
        widgets = {
            'firstName': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name', 'required': True}),
            'lastName': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address', 'required': True}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number', 'required': True}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username', 'required': True}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'required': False}),
            'image': forms.FileInput(attrs={'class': 'form-control-file'})
        }

    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['password'].required = False
            self.fields['password_confirmation'].required = False
        else:
            self.fields['password'].required = True
            self.fields['password_confirmation'].required = True

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("password_confirmation")
        phone = cleaned_data.get("phone")

        if not phone:
            raise forms.ValidationError("Phone number is required.")
        
        if not (isinstance(phone, int) and len(str(phone)) == 8):
            self.add_error('phone', 'Phone number must be exactly 8 digits long.')

        if self.instance and self.instance.pk:
            if password or confirm_password:
                if password != confirm_password:
                    raise forms.ValidationError("The passwords entered do not match. Please ensure both passwords are identical.")
        else:
            if not password or not confirm_password:
                raise forms.ValidationError("Both password fields are required.")
            if password != confirm_password:
                raise forms.ValidationError("The passwords entered do not match. Please ensure both passwords are identical.")

        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.instance and self.instance.pk:
            if Client.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("This email is already in use. Please provide a different email address.")
        else:
            if Client.objects.filter(email=email).exists():
                raise forms.ValidationError("This email is already in use. Please provide a different email address.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if self.instance and self.instance.pk:
            if Client.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("This username is already taken. Please choose a different username.")
        else:
            if Client.objects.filter(username=username).exists():
                raise forms.ValidationError("This username is already taken. Please choose a different username.")
        return username
