from django                         import forms
from client.models                  import Client
from supervisor.models.project      import Project
from supervisor.models.parcelle     import Parcelle
from supervisor.models.localisation import Localisation
from supervisor.models.node         import  Node
from django.contrib.gis.geos        import Point
from django.core.exceptions import ValidationError

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



class CustomModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.gouvernorat_libelle}, {obj.delegation_libelle}, {obj.localite_libelle}"

class ProjectForm(forms.ModelForm):
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        required=True,
        empty_label='None',
        widget=forms.Select(attrs={
            'name': 'client',
            'class': 'form-control',
            'placeholder': 'Select Client'
        })
    )
    city = CustomModelChoiceField(
        queryset=Localisation.objects.all(),
        required=True,
        empty_label='Select Location',
        widget=forms.Select(attrs={
            'name': 'city',
            'class': 'form-control',
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
            'descp': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Project Description',
                'rows': 2,  
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


class ParcelleForm(forms.ModelForm):
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        required=True,
        empty_label='Select Project',
        widget=forms.Select(attrs={
            'name': 'project',
            'class': 'form-control',
            'id': 'id_project'
        })
    )
    
    class Meta:
        model = Parcelle
        fields = ['name', 'project']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ploygon Name',
                'required': True,
                'id': 'id_name_polygon'
                }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project'].widget.choices = [
            (project.polygon_id, f"{project.name} (lat: {project.city.latitude}, lon: {project.city.longitude})", 
             {'data-latitude': project.city.latitude, 'data-longitude': project.city.longitude})
            for project in Project.objects.all() if project.city
        ]

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError('This field is required.')
        return name

class NodeForm(forms.ModelForm):
    NODE_REFERENCE_CHOICES = [
        ('1:eui-b770421e86700821', '1:eui-b770421e86700821'),
        ('2:eui-a835411eb0084141', '2:eui-a835411eb0084141'),
    ]
    reference = forms.ChoiceField(
        choices=[('', 'Node reference')] + NODE_REFERENCE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control form-control-sm', 
            'id': 'nodeReference', 
            'style': 'height: calc(1.5em + .75rem + 3px);'
        })
    )
    class Meta:
        model = Node
        fields = ['name', 'reference', 'sensors', 'node_range', 'latitude', 'longitude', 'position', 'parcelle']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'id': 'nodeName', 'style': 'height: calc(1.5em + .75rem + 3px);'}),
            'sensors': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'id': 'nodeSensors', 'style': 'height: calc(1.5em + .75rem + 3px);'}),
            'node_range': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'id': 'nodeOrder', 'style': 'height: calc(1.5em + .75rem + 3px);'}),
            'latitude': forms.HiddenInput(attrs={'id': 'id_latitude'}),
            'longitude': forms.HiddenInput(attrs={'id': 'id_longitude'}),
            'position': forms.HiddenInput(attrs={'id': 'nodePosition'}),
            'parcelle': forms.HiddenInput(attrs={'id': 'id_parcelle'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        position = cleaned_data.get('position')
        parcelle = cleaned_data.get('parcelle')
        parcelle_id = parcelle.id if parcelle else None
        
        if position and parcelle_id:
            try:
                parcelle = Parcelle.objects.get(id=parcelle_id)
                point = Point(position.y, position.x)
                print(point, parcelle.polygon)
                if not parcelle.polygon.contains(point):
                    raise ValidationError("The node must be placed inside the plot.")
            except Parcelle.DoesNotExist:
                raise ValidationError("Parcelle not found.")
        return cleaned_data
