from django         import forms
from client.models  import Client
from supervisor.models.project  import Project

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




class ProjectForm(forms.ModelForm):
    client = forms.ModelChoiceField(
        queryset = Client.objects.all(),
        required = True,
        empty_label = 'None',
        widget      = forms.Select( attrs={
            'name': 'client',
            'class': 'form-control',
            'placeholder': 'Select Client'
        })
    )
    class Meta:
        model = Project
        fields = ['name', 'city', 'descp', 'client', 'piece_joindre', 'date_debut', 'date_fin']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Project Name', 
                'required': True
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Region Name', 
                'required': True
            }),
            'descp': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Project Description'
            }),
            'piece_joindre': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'date_debut': forms.DateTimeInput(attrs={
                'class': 'form-control', 
                'type': 'datetime-local'
            }, format='%Y-%m-%dT%H:%M'),
            'date_fin': forms.DateTimeInput(attrs={
                'class': 'form-control', 
                'type': 'datetime-local'
            }, format='%Y-%m-%dT%H:%M')
        }

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        #? Handle the datetime-local input format for browser compatibility
        self.fields['date_debut'].input_formats = ('%Y-%m-%dT%H:%M',)
        self.fields['date_fin'].input_formats = ('%Y-%m-%dT%H:%M',)