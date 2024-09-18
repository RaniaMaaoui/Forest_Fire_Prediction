from django.contrib.gis.db          import models
from django.utils                   import timezone
from client.models                  import Client
from .localisation                  import Localisation


class Project(models.Model):
    name            = models.CharField(max_length=30)
    descp           = models.TextField(null=True)
    date_debut      = models.DateTimeField(default=timezone.now)
    date_fin        = models.DateTimeField()
    city            = models.ForeignKey(Localisation, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects')
    piece_joindre   = models.FileField(upload_to='uploads/%Y/%m/%d/', null=True, blank=True)
    client          = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)
    polygon_id      = models.BigAutoField(primary_key=True, default=None)


    def __str__(self):
        return f'Project: {self.name}'